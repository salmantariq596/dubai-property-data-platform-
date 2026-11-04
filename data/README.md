# data/

Local working copies of the raw DLD downloads. **Nothing under `data/raw/` is committed** (see `.gitignore`): the files are large and can always be re-downloaded from the official source.

Expected layout, matching the bronze landing convention used later in the pipeline:

```
data/raw/
├── transactions/load_date=YYYY-MM-DD/<file>.csv
└── rents/load_date=YYYY-MM-DD/<file>.csv
```

Record where and when each file was downloaded in `docs/data_sources.md`.
