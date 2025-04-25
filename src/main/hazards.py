import geopandas as gpd
import pandas as pd
import xarray as xr

from src.utils.constants import HAZARD_INPUT_PATH
from src.utils.utils import (
    compute_binary_zonal_stat,
    compute_hazard_population_exposure,
    compute_zonal_stat,
)


def process_hazards(
    admin_gdf: gpd.geodataframe,
    pop_raster: xr.DataArray,
    exposures: xr.DataArray,  # noqa: E501
) -> pd.DataFrame:
    """ "
    Process hazard data""
    """
    return compute_hazard_population_exposure(admin_gdf, pop_raster, exposures)


def process_deforestation(admin_df: gpd.GeoDataFrame) -> pd.DataFrame:
    """
    Process deforestation data
    """
    df = admin_df.drop(columns="geometry").copy()
    df["loss"] = compute_binary_zonal_stat(
        HAZARD_INPUT_PATH["deforestation"]["loss"], admin_df
    )
    df["cover"] = compute_binary_zonal_stat(
        HAZARD_INPUT_PATH["deforestation"]["cover"], admin_df
    )
    df["deforestation"] = df["loss"] / df["cover"]
    return df


def process_cyclone(admin_df: gpd.GeoDataFrame) -> pd.DataFrame:
    """ "
    Process cyclone data
    """
    df = admin_df.drop(columns="geometry").copy()
    hazard_raster = xr.open_dataarray(HAZARD_INPUT_PATH["cyclone"])
    hazard_data = hazard_raster[0].values
    df["max_speed"] = compute_zonal_stat(
        hazard_data, hazard_raster.rio.transform(), admin_df, agg="max"
    )
    return df


def coastal_erosion(admin_df: gpd.GeoDataFrame) -> pd.DataFrame:
    """
    Process coastal erosion by applying a 1 km buffer on admin boundaries,
    aggregating hazard ‘rate_time’ back onto the original admin IDs.
    """
    metric_crs = admin_df.estimate_utm_crs()
    admin_metric = admin_df.to_crs(metric_crs).copy()
    admin_metric["geometry"] = admin_metric.geometry.buffer(1000)  # 1 000 m
    hazard_path = HAZARD_INPUT_PATH["coastal_erosion"]
    hazard = gpd.read_file(hazard_path).to_crs(metric_crs)[["rate_time", "geometry"]]
    adm_col = next(
        col for col in ("adm2_src", "adm1_src", "adm0_src") if col in admin_df.columns
    )
    joined = gpd.sjoin(
        admin_metric, hazard, how="left", predicate="intersects", rsuffix="_hz"
    )
    stats = (
        joined.groupby(adm_col)["rate_time"]
        .mean()
        .reset_index()
        .rename(columns={"rate_time": "mean_rate_time"})
    )
    result = admin_df.drop(columns="geometry").merge(stats, on=adm_col, how="left")
    return result
