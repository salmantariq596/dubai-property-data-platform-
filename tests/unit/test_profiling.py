from datetime import datetime, timezone

import pandas as pd
import pytest

from dubai_property.profiling import profile_dataframe, read_raw_csv, render_markdown
from dubai_property.profiling.cli import main
from dubai_property.profiling.profile import profile_column


def col(profile, name):
    return next(c for c in profile.columns if c.name == name)


# --- reading -----------------------------------------------------------------


def test_read_keeps_everything_as_strings(sample_csv):
    df = read_raw_csv(sample_csv)
    assert all(pd.api.types.is_string_dtype(dtype) for dtype in df.dtypes)
    assert df.loc[0, "actual_worth"] == "1450000"


def test_read_does_not_turn_na_text_into_null(sample_csv):
    df = read_raw_csv(sample_csv)
    assert "n/a" in df["actual_worth"].tolist()


def test_read_preserves_arabic_text(sample_csv):
    df = read_raw_csv(sample_csv)
    assert df.loc[0, "area_name_ar"] == "الخليج التجارى"


def test_read_strips_bom_from_header(tmp_path):
    path = tmp_path / "bom.csv"
    path.write_bytes("﻿transaction_id,value\nA,1\n".encode())
    df = read_raw_csv(path)
    assert list(df.columns) == ["transaction_id", "value"]


def test_read_sample_rows(sample_csv):
    assert len(read_raw_csv(sample_csv, nrows=3)) == 3


# --- column profiling --------------------------------------------------------


def test_blank_and_whitespace_count_as_null():
    p = profile_column(pd.Series(["a", "", "  ", "b"], name="x"))
    assert p.non_null == 2
    assert p.null_pct == 50.0


def test_numeric_with_thousands_separator_is_numeric():
    p = profile_column(pd.Series(["1,250,000", "980000", "12.5"], name="v"))
    assert p.inferred_type == "numeric"
    assert p.max_numeric == 1_250_000


def test_plain_numbers_are_not_mistaken_for_dates():
    p = profile_column(pd.Series(["2024", "1250000", "85"], name="v"))
    assert p.date_pct == 0.0
    assert p.inferred_type == "numeric"


def test_day_first_dates_are_parsed():
    p = profile_column(pd.Series(["05-01-2024", "14-01-2024", "2024-03-01"], name="d"))
    assert p.inferred_type == "date"
    assert p.min_date == "2024-01-05"
    assert p.max_date == "2024-03-01"


def test_iso_dates_are_not_read_day_first():
    # Regression: dayfirst=True once turned 2024-03-01 into 3 January.
    p = profile_column(pd.Series(["2024-03-01", "2024-12-25T10:00:00"], name="d"))
    assert p.min_date == "2024-03-01"
    assert p.max_date == "2024-12-25"


def test_arabic_column_detected():
    p = profile_column(pd.Series(["مرسى دبي", "الخليج التجارى"], name="ar"))
    assert p.arabic_pct == 100.0
    assert p.inferred_type == "text (Arabic)"


def test_empty_column():
    p = profile_column(pd.Series(["", ""], name="e"))
    assert p.inferred_type == "empty"
    assert p.null_pct == 100.0


# --- dataset profiling on the fixture -----------------------------------------


@pytest.fixture
def fixture_profile(sample_csv):
    return profile_dataframe(read_raw_csv(sample_csv), name="sample", key_column="transaction_id")


def test_row_and_column_counts(fixture_profile):
    assert fixture_profile.row_count == 12
    assert fixture_profile.column_count == 12


def test_duplicate_business_key_found(fixture_profile):
    assert fixture_profile.duplicate_key_rows == 2
    assert fixture_profile.exact_duplicate_rows == 1


def test_bad_date_lowers_date_share(fixture_profile):
    d = col(fixture_profile, "instance_date")
    assert d.date_pct < 100
    assert d.max_date == "2024-01-15"


def test_bad_numeric_value_lowers_numeric_share(fixture_profile):
    worth = col(fixture_profile, "actual_worth")
    assert 50 <= worth.numeric_pct < 95
    assert worth.min_numeric == 0


def test_missing_key_column_raises(sample_csv):
    with pytest.raises(KeyError, match="not_a_column"):
        profile_dataframe(read_raw_csv(sample_csv), name="s", key_column="not_a_column")


# --- report and CLI ----------------------------------------------------------


def test_report_contains_summary_and_flags(fixture_profile):
    md = render_markdown(fixture_profile, generated_at=datetime(2026, 1, 1, tzinfo=timezone.utc))
    assert "# Profile: sample" in md
    assert "| Rows | 12 |" in md
    assert "share a `transaction_id`" in md
    assert "quarantine candidates" in md
    assert "zero or negative" in md


def test_report_escapes_pipes():
    df = pd.DataFrame({"t": ["a|b"]})
    md = render_markdown(profile_dataframe(df, name="p"))
    assert "a\\|b" in md


def test_cli_writes_report(sample_csv, tmp_path):
    out = tmp_path / "profiles" / "sample.md"
    code = main([str(sample_csv), "--key", "transaction_id", "--output", str(out)])
    assert code == 0
    assert out.read_text(encoding="utf-8").startswith("# Profile: sample_transactions")


def test_cli_missing_file_returns_error(tmp_path, capsys):
    assert main([str(tmp_path / "nope.csv")]) == 2
    assert "file not found" in capsys.readouterr().err
