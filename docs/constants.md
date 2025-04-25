# constants.py

This module loads environment variables and defines I/O paths:

- Uses `dotenv` to load variables from `~/.hazard_tool_rc`.
- USE_LOCAL: boolean flag to toggle between S3 mode and local mode.
- S3_BUCKET, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_DEFAULT_REGION: AWS credentials.
- PATH: I/O prefix (`/vsis3/{S3_BUCKET}/` or `./`).
- Defines relative keys for all raster/shapefile inputs and output CSVs:
  - POPULATION_RASTER_PATH
  - HAZARD_RASTER_PATH
  - ADMIN_VECTOR_PATH
  - HAZARD_INPUT_PATH
  - HAZARD_OUTPUT_PATH
