# Dataset Governance

## Default rule

Repository source may contain manifests and small legally-cleared fixtures, not downloaded corpora or private/student recordings.

## Required manifest fields

Each materialized dataset must record at minimum:

- canonical name and source,
- version/release identifier,
- license or terms reference,
- acquisition date/method,
- file/integrity hash where practical,
- allowed research/redistribution status,
- local storage path outside Git when large.

## Human gate

If license, redistribution, commercial use or privacy status is ambiguous, data acquisition/materialization stops while architecture, synthetic fixtures and independent work continue.
