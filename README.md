# Hazard Processing Tool AWS

A CLI tool to process hazard data (flood, earthquake,
landslide, deforestation, cyclone, coastal erosion) and export results to AWS S3.

## Poetry Usage

Install Poetry (if not already installed):

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

Project installation:

```bash
poetry --version
```

## Features

- Prepare exposure data from various sources
- Process multiple hazards with xarray and geopandas
- Export processed datasets to S3 using the VSI interface
- Configurable via `src/utils/constants.py`
- Interactive web app UI via Streamlit

## Requirements

- Python 3.10+
- Poetry
- AWS CLI configured with appropriate permissions

## Installation

```bash
git clone <repository_url>
cd hazard-processing-tool-aws
make .venv      # Install dependencies
make hooks      # Install pre-commit hooks
```

## Usage

```bash
make paths     # Setup paths
make aws_etl   # Run the hazard processing pipeline
make local_etl # Run the hazard processing pipeline locally without S3
make test      # Run unit tests
make lint      # Run lint checks
make app      # Run the interactive Streamlit application
```

## Configuration

Create a `~/.hazard_tool_rc` file in your home directory
with the following environment variables:

```bash
export S3_BUCKET=<your-s3-bucket>
export AWS_ACCESS_KEY_ID=<your-aws-access-key-id>
export AWS_SECRET_ACCESS_KEY=<your-aws-secret-access-key>
export AWS_DEFAULT_REGION=<your-aws-default-region>
export USE_LOCAL=true
```

Optionally, adjust path constants (e.g., `ADMIN_VECTOR_PATH`, `POPULATION_RASTER_PATH`)
directly in `src/utils/constants.py` if needed.

## Project Structure

```bash
.
├── src/
│   ├── main/   # Entry point and processing logic
│   └── utils/  # Helper functions and constants
├── tests/      # Unit tests
├── Makefile    # Common tasks
├── pyproject.toml
└── README.md
```

## Contributing

Contributions welcome! Please open issues and pull requests.

## License

GPL-3.0-only. See [LICENSE](LICENSE) for details.
