# Data manifests

One JSON file per public data source. Schema:

```json
{
  "source": "Human-readable name",
  "url": "Citation / download URL",
  "primary": "<sha256 of canonical file>",
  "notes": "Any caveats"
}
```

Manifests are consulted by loaders to verify SHA256 of cached files. A
mismatch yields `MeasurementStatus.DATA_QUALITY_FAILED`.
