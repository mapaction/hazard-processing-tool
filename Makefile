.PHONY: all
all = help

.venv:
	@echo "Installing project dependencies.."
	@poetry install --no-root


hooks:
	@echo "Adding pre-commit hooks.."
	@poetry run pre-commit install
	

test:
	@echo "Running unit tests.."
	@poetry run python -m pytest

lint:
	@echo "Running lint tests.."
	@poetry run pre-commit run --all-files

clean:
	@echo "Removing .venv"
	@rm -rf .venv
	@poetry env remove --all

aws_etl:
	@echo "Running app.."
	@poetry run python -m src.main.__main__
	@echo "Hazard App run successfully"

local_etl:
	@echo "Running in LOCAL mode (no S3)..."
	@USE_LOCAL=true poetry run python -m src.main.__main__
	@echo "Hazard App run successfully"

app:
	@echo "Running Streamlit app..."
	@PYTHONPATH=. poetry run streamlit run src/main/app.py

help:
	@echo "Available make targets:"
	@echo " make help           - Print help"
	@echo " make .venv          - Install project dependencies"
	@echo " make hooks          - Add pre-commit hooks"
	@echo " make test           - Run unit tests"
	@echo " make lint           - Run lint tests"
	@echo " make clean          - Remove .venv"