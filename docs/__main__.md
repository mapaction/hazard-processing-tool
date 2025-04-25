# __main__.py

This is the entrypoint for the Hazard Processing Tool CLI.

It performs the following steps:

- Parses configuration and environment flags
- Loads administrative boundary data
- Prepares exposure datasets (population and hazard rasters)
- Invokes hazard-specific processing functions from `hazards.py`
- Exports results via `export_dataset` (to S3 or locally based on `USE_LOCAL`)
