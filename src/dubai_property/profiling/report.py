"""Render a DatasetProfile as Markdown, ready to commit under docs/profiles/."""

from __future__ import annotations

from datetime import datetime, timezone

from dubai_property.profiling.profile import ColumnProfile, DatasetProfile


def _fmt_num(value: float | None) -> str:
    if value is None:
        return ""
    return f"{value:,.0f}" if float(value).is_integer() else f"{value:,.2f}"


def _range(col: ColumnProfile) -> str:
    if col.inferred_type == "numeric":
        return f"{_fmt_num(col.min_numeric)} – {_fmt_num(col.max_numeric)}"
    if col.inferred_type == "date":
        return f"{col.min_date} – {col.max_date}"
    return ""


def _escape(text: str, limit: int = 30) -> str:
    text = text.replace("|", "\\|").replace("\n", " ")
    return text if len(text) <= limit else text[: limit - 1] + "…"


def render_markdown(profile: DatasetProfile, generated_at: datetime | None = None) -> str:
    """Return the profile as a Markdown document."""
    generated_at = generated_at or datetime.now(timezone.utc)
    lines = [
        f"# Profile: {profile.name}",
        "",
        f"Generated {generated_at:%Y-%m-%d %H:%M} UTC by `dld-profile`.",
        "",
        "## Summary",
        "",
        "| Metric | Value |",
        "|---|---|",
        f"| Source file | `{profile.source_file or 'n/a'}` |",
        f"| Rows | {profile.row_count:,} |",
        f"| Columns | {profile.column_count} |",
        f"| Exact duplicate rows | {profile.exact_duplicate_rows:,} |",
    ]
    if profile.key_column:
        lines.append(f"| Rows sharing a `{profile.key_column}` | {profile.duplicate_key_rows:,} |")

    lines += [
        "",
        "## Columns",
        "",
        "| Column | Inferred type | Null % | Distinct | Range | Top values |",
        "|---|---|---:|---:|---|---|",
    ]
    for col in profile.columns:
        top = ", ".join(f"{_escape(v)} ({n:,})" for v, n in col.top_values[:3])
        lines.append(
            f"| `{col.name}` | {col.inferred_type} | {col.null_pct:.1f} | "
            f"{col.distinct:,} | {_range(col)} | {top} |"
        )

    issues = _quality_flags(profile)
    lines += ["", "## Flags for the data dictionary", ""]
    lines += [f"- {i}" for i in issues] if issues else ["- None found."]
    lines.append("")
    return "\n".join(lines)


def _quality_flags(profile: DatasetProfile) -> list[str]:
    """Plain-language issues worth copying into docs/data_dictionary.md."""
    flags = []
    if profile.duplicate_key_rows:
        flags.append(
            f"{profile.duplicate_key_rows:,} rows share a `{profile.key_column}` value "
            "— decide the dedup rule for silver (latest ingested wins?)."
        )
    if profile.exact_duplicate_rows:
        flags.append(f"{profile.exact_duplicate_rows:,} exact duplicate rows.")
    for col in profile.columns:
        if col.non_null == 0:
            flags.append(f"`{col.name}` is completely empty — candidate to drop.")
            continue
        if col.null_pct >= 20:
            flags.append(f"`{col.name}` is {col.null_pct:.1f}% null.")
        if 50 <= col.numeric_pct < 95:
            flags.append(
                f"`{col.name}` is mostly numeric ({col.numeric_pct:.1f}%) "
                "but some values will fail a cast — quarantine candidates."
            )
        if 50 <= col.date_pct < 95:
            flags.append(
                f"`{col.name}` is mostly dates ({col.date_pct:.1f}%) "
                "but some values will fail a cast — quarantine candidates."
            )
        if col.inferred_type == "numeric" and col.min_numeric is not None and col.min_numeric <= 0:
            flags.append(f"`{col.name}` has zero or negative values (min {col.min_numeric:,.0f}).")
    return flags
