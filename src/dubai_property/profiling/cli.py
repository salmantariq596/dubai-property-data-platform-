"""Command line entry point: ``dld-profile <csv> --key <column> --output <md>``."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from dubai_property.profiling.profile import profile_dataframe, read_raw_csv
from dubai_property.profiling.report import render_markdown


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="dld-profile",
        description="Profile a raw DLD CSV file and write a Markdown report.",
    )
    parser.add_argument("input", type=Path, help="Path to the CSV file")
    parser.add_argument("--key", help="Business key column to check for duplicates")
    parser.add_argument("--name", help="Dataset name for the report title")
    parser.add_argument("--output", type=Path, help="Write the report here (default: stdout)")
    parser.add_argument(
        "--sample-rows",
        type=int,
        help="Only read the first N rows (useful for a quick look at a multi-GB file)",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if not args.input.exists():
        print(f"error: file not found: {args.input}", file=sys.stderr)
        return 2

    df = read_raw_csv(args.input, nrows=args.sample_rows)
    profile = profile_dataframe(
        df,
        name=args.name or args.input.stem,
        key_column=args.key,
        source_file=args.input.name,
    )
    report = render_markdown(profile)

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(report, encoding="utf-8")
        print(
            f"Profiled {profile.row_count:,} rows x {profile.column_count} columns -> {args.output}"
        )
    else:
        print(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
