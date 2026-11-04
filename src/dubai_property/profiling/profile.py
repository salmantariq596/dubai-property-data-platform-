"""Column-level profiling for raw DLD CSV files.

Design choices (mirrors the bronze layer that comes later):

* Every column is read as a string. Profiling reports what *could* be cast,
  instead of letting pandas guess types and silently mangle values.
* Empty strings and whitespace-only cells count as null.
* Arabic text is detected explicitly, because DLD files carry Arabic and
  English columns side by side.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd

# Arabic Unicode blocks: Arabic, Arabic Supplement, Arabic Presentation Forms A/B
_ARABIC_RE = re.compile(r"[؀-ۿݐ-ݿﭐ-﷿ﹰ-﻿]")

# Number formats seen in DLD exports: "1250000", "1,250,000", "1250000.50", "-12"
_NUMERIC_RE = re.compile(r"^-?\d{1,3}(,\d{3})+(\.\d+)?$|^-?\d+(\.\d+)?$")

_ISO_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}")

# A cast "works" for a column when at least this share of non-null values parse.
_TYPE_THRESHOLD = 0.95


@dataclass(frozen=True)
class ColumnProfile:
    """What one raw column looks like."""

    name: str
    non_null: int
    null_pct: float
    distinct: int
    numeric_pct: float
    date_pct: float
    arabic_pct: float
    min_numeric: float | None
    max_numeric: float | None
    min_date: str | None
    max_date: str | None
    top_values: list[tuple[str, int]] = field(default_factory=list)

    @property
    def inferred_type(self) -> str:
        """Best-guess target type for the silver layer."""
        if self.non_null == 0:
            return "empty"
        if self.numeric_pct >= _TYPE_THRESHOLD:
            return "numeric"
        if self.date_pct >= _TYPE_THRESHOLD:
            return "date"
        if self.arabic_pct >= _TYPE_THRESHOLD:
            return "text (Arabic)"
        return "text"


@dataclass(frozen=True)
class DatasetProfile:
    """Summary of a whole file plus one profile per column."""

    name: str
    row_count: int
    column_count: int
    columns: list[ColumnProfile]
    key_column: str | None = None
    duplicate_key_rows: int | None = None
    exact_duplicate_rows: int = 0
    source_file: str | None = None


def read_raw_csv(path: str | Path, nrows: int | None = None) -> pd.DataFrame:
    """Read a DLD CSV the way bronze will: all strings, UTF-8, nothing coerced.

    ``utf-8-sig`` strips the byte-order mark some government exports start with,
    which would otherwise end up glued to the first column name.
    """
    df = pd.read_csv(
        path,
        dtype=str,
        encoding="utf-8-sig",
        keep_default_na=False,  # keep "NA" etc. as literal text; we decide what null is
        nrows=nrows,
    )
    df.columns = [c.strip() for c in df.columns]
    return df


def _null_mask(series: pd.Series) -> pd.Series:
    return series.isna() | (series.astype(str).str.strip() == "")


def _to_numeric(values: pd.Series) -> pd.Series:
    cleaned = values.str.strip()
    ok = cleaned.str.match(_NUMERIC_RE)
    return pd.to_numeric(cleaned.where(ok).str.replace(",", "", regex=False), errors="coerce")


def _to_date(values: pd.Series) -> pd.Series:
    """Parse ISO (yyyy-mm-dd) and day-first (dd-mm-yyyy, dd/mm/yyyy) dates.

    The two formats are parsed separately on purpose: with ``dayfirst=True``
    pandas reads ISO "2024-03-01" as 3 January, which silently corrupts dates.
    """
    cleaned = values.str.strip()
    is_iso = cleaned.str.match(_ISO_DATE_RE)
    parsed = pd.Series(pd.NaT, index=cleaned.index, dtype="datetime64[ns]")
    if is_iso.any():
        parsed[is_iso] = pd.to_datetime(
            cleaned[is_iso].str[:10], errors="coerce", format="%Y-%m-%d"
        )
    rest = ~is_iso
    if rest.any():
        parsed[rest] = pd.to_datetime(cleaned[rest], errors="coerce", dayfirst=True, format="mixed")
    return parsed


def profile_column(series: pd.Series, top_n: int = 5) -> ColumnProfile:
    """Profile one column of raw string values."""
    total = len(series)
    nulls = _null_mask(series)
    values = series[~nulls].astype(str)
    non_null = len(values)

    numeric = _to_numeric(values) if non_null else pd.Series(dtype=float)
    numeric_ok = numeric.dropna()

    # Only try dates on values that are not plain numbers; "2024" or "1250000"
    # would otherwise parse as dates and inflate date_pct.
    date_candidates = values[numeric.isna()] if non_null else values
    dates = _to_date(date_candidates) if len(date_candidates) else pd.Series(dtype="datetime64[ns]")
    dates_ok = dates.dropna()

    arabic = values.str.contains(_ARABIC_RE) if non_null else pd.Series(dtype=bool)

    def pct(n: int) -> float:
        return round(100.0 * n / non_null, 2) if non_null else 0.0

    top = values.value_counts().head(top_n)

    return ColumnProfile(
        name=str(series.name),
        non_null=non_null,
        null_pct=round(100.0 * int(nulls.sum()) / total, 2) if total else 0.0,
        distinct=int(values.nunique()),
        numeric_pct=pct(len(numeric_ok)),
        date_pct=pct(len(dates_ok)),
        arabic_pct=pct(int(arabic.sum())),
        min_numeric=float(numeric_ok.min()) if len(numeric_ok) else None,
        max_numeric=float(numeric_ok.max()) if len(numeric_ok) else None,
        min_date=dates_ok.min().date().isoformat() if len(dates_ok) else None,
        max_date=dates_ok.max().date().isoformat() if len(dates_ok) else None,
        top_values=[(str(k), int(v)) for k, v in top.items()],
    )


def profile_dataframe(
    df: pd.DataFrame,
    name: str,
    key_column: str | None = None,
    source_file: str | None = None,
    top_n: int = 5,
) -> DatasetProfile:
    """Profile every column, plus duplicate checks on the business key."""
    if key_column is not None and key_column not in df.columns:
        raise KeyError(f"Key column {key_column!r} not found. Columns: {list(df.columns)}")

    duplicate_key_rows = None
    if key_column is not None:
        keys = df.loc[~_null_mask(df[key_column]), key_column].str.strip()
        # Rows that share a key with at least one other row
        duplicate_key_rows = int(keys.duplicated(keep=False).sum())

    return DatasetProfile(
        name=name,
        row_count=len(df),
        column_count=df.shape[1],
        columns=[profile_column(df[c], top_n=top_n) for c in df.columns],
        key_column=key_column,
        duplicate_key_rows=duplicate_key_rows,
        exact_duplicate_rows=int(df.duplicated().sum()),
        source_file=source_file,
    )
