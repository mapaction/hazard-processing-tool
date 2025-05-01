# Interactive Web App (app.py)

Minimal guide for the Streamlit interface.

## Running the App

• `make app`
• `PYTHONPATH=. poetry run streamlit run src/main/app.py`

## Sidebar Controls

• **Use Local ETL (no S3)**: save results locally
• **Run Full Pipeline**: execute entire data workflow
• **Select Hazard**: choose one of `flood`, `earthquake`, `landslide`,
`deforestation`, `cyclone`, `coastal_erosion`
• **Run [Hazard] Analysis**: process selected hazard and display results

## Tabs

• **Analysis**: display and download processed data as CSV
• **Visualisation**: view previously saved results

## File Location

`src/main/app.py`
