import importlib
import os
from datetime import datetime
from pathlib import Path

import geopandas as gpd
import pandas as pd
import rioxarray as rxr
import streamlit as st
from dotenv import load_dotenv

import src.main.hazards as hazards
from src.main.__main__ import main as run_full_pipeline
from src.main.hazards import coastal_erosion, process_cyclone, process_deforestation
from src.utils import constants
from src.utils.utils import compute_hazard_mask, compute_population_exposure

load_dotenv(dotenv_path=os.path.expanduser("~/.hazard_tool_rc"))


def _lookup_opened_data(hazard_name: str):
    """
    Load the admin boundaries, population raster,
    and preprocessed hazard exposure raster.
    Returns: admin_gdf, pop_raster, exposure_raster
    """
    admin_gdf = gpd.read_file(constants.ADMIN_VECTOR_PATH)
    pop_raster = rxr.open_rasterio(constants.POPULATION_RASTER_PATH, masked=True)
    hazard_raster = rxr.open_rasterio(
        constants.HAZARD_RASTER_PATH[hazard_name], masked=True
    )
    threshold = constants.HAZARD_THRESHOLD[hazard_name]

    hazard_mask = compute_hazard_mask(hazard_raster, pop_raster, threshold)
    exposure_raster = compute_population_exposure(hazard_mask, pop_raster)

    return admin_gdf, pop_raster, exposure_raster


st.set_page_config(page_title="Hazard Processing Tool", layout="wide")
st.image("img/MA-logo.png", width=300)
st.title("Hazard Processing Tool")
st.markdown("Process hazard data and export results locally or to S3.")

st.sidebar.header("Controls")
use_local = st.sidebar.checkbox("Use Local ETL (no S3)", value=True)


def _handle_run_full():
    os.environ["USE_LOCAL"] = "true" if use_local else "false"
    importlib.reload(constants)
    import src.utils.s3 as s3mod

    importlib.reload(s3mod)  # noqa: E702
    import src.utils.utils as utilmod

    importlib.reload(utilmod)  # noqa: E702
    with st.spinner(f"Executing full pipeline ({'Local' if use_local else 'AWS'})..."):
        run_full_pipeline()
    st.sidebar.success("Pipeline complete!")


if st.sidebar.button("Run Full Pipeline"):
    _handle_run_full()

sadc_member_countries = [
    "Angola",
    "Botswana",
    "Comoros",
    "Democratic Republic of the Congo",
    "Eswatini",
    "Lesotho",
    "Madagascar",
    "Malawi",
    "Mauritius",
    "Mozambique",
    "Namibia",
    "Seychelles",
    "South Africa",
    "Tanzania",
    "Zambia",
    "Zimbabwe",
]

st.sidebar.selectbox("Select SADC Member Country (Dummy Button)", sadc_member_countries)

subnational_admin_boundaries = [
    "Admin 1",
    "Admin 2",
    "Admin 3",
    "Admin 4",
]

st.sidebar.selectbox(
    "Select Subnational Admin Boundary (Dummy Button)", subnational_admin_boundaries
)
populations_options = [
    "WorldPop",
    "GHS",
]
st.sidebar.selectbox("Select Population Dataset (Dummy Button)", populations_options)

hazard_options = [
    "flood",
    "earthquake",
    "landslide",
    "deforestation",
    "cyclone",
    "coastal_erosion",
]
hazard_choice = st.sidebar.selectbox("Select Hazard", hazard_options)
tabs = st.tabs(["Analysis", "Visualisation"])

with tabs[0]:
    st.header("Hazard Analysis")

    if st.button(f"Run {hazard_choice.capitalize()} Analysis"):
        os.environ["USE_LOCAL"] = "true" if use_local else "false"
        importlib.reload(constants)

        with st.spinner(f"Processing {hazard_choice}..."):
            if hazard_choice in ["flood", "earthquake", "landslide"]:
                admin_gdf, pop_raster, exposure_raster = _lookup_opened_data(
                    hazard_choice
                )
                df = hazards.process_hazards(admin_gdf, pop_raster, exposure_raster)
            elif hazard_choice == "deforestation":
                admin_gdf = gpd.read_file(constants.ADMIN_VECTOR_PATH)
                df = process_deforestation(admin_gdf)
            elif hazard_choice == "cyclone":
                admin_gdf = gpd.read_file(constants.ADMIN_VECTOR_PATH)
                df = process_cyclone(admin_gdf)
            else:  # coastal_erosion
                admin_gdf = gpd.read_file(constants.ADMIN_VECTOR_PATH)
                df = coastal_erosion(admin_gdf)

        st.success(f"{hazard_choice.capitalize()} analysis complete!")
        st.session_state["result_df"] = df
        st.dataframe(df, use_container_width=True)

        # Save the result
        output_path = constants.HAZARD_OUTPUT_PATH[hazard_choice]
        if use_local:
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            df.to_csv(output_path, index=False)
        else:
            # Still save locally even if tick was to S3
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            df.to_csv(output_path, index=False)

    if "result_df" in st.session_state:
        csv_data = st.session_state["result_df"].to_csv(index=False).encode("utf-8")
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        fname = f"{hazard_choice}_results_{ts}.csv"
        st.download_button(
            "Download Results as CSV", data=csv_data, file_name=fname, mime="text/csv"
        )
    else:
        st.info("Click 'Run … Analysis' above to start.")

with tabs[1]:
    st.header("Visualisation")

    if "result_df" in st.session_state:
        df = st.session_state["result_df"]
    else:
        csv_path = Path(constants.HAZARD_OUTPUT_PATH[hazard_choice])
        df = pd.read_csv(csv_path) if csv_path.exists() else None

    if df is not None:
        st.dataframe(df, use_container_width=True)
    else:
        st.info("Run an analysis (or the full pipeline) to visualise results.")

st.markdown("---")
st.markdown("Built on the hazard-processing-tool AWS pipeline.")
