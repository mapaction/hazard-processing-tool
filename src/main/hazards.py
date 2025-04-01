import geopandas as gpd
import xarray as xr
import numpy as np
import pandas as pd
from typing import List
from typing import Dict
from src.utils.constants import ( HAZARD_INPUT_PATH, S3_BUCKET )
from src.utils.utils import ( 
    compute_hazard_population_exposure,
    compute_binary_zonal_stat,
    compute_zonal_stat )

def process_hazards(admin_gdf: gpd.geodataframe, 
                    pop_raster:xr.DataArray, 
                    exposures: xr.DataArray
                    )-> pd.DataFrame:
    """"
    Process hazard data""
    """
    return compute_hazard_population_exposure(admin_gdf, pop_raster, exposures)

def process_deforestation(admin_df: gpd.GeoDataFrame) -> pd.DataFrame:
    """
    Process deforestation data
    """
    df = admin_df.drop(columns='geometry').copy()
    df['loss'] = compute_binary_zonal_stat(HAZARD_INPUT_PATH['deforestation']['loss'], admin_df)
    df['cover'] = compute_binary_zonal_stat(HAZARD_INPUT_PATH['deforestation']['cover'], admin_df)
    df['deforestation'] = df['loss'] / df['cover']
    return df

def process_cyclone(admin_df: gpd.GeoDataFrame) -> pd.DataFrame:
    """"
    Process cyclone data
    """
    df = admin_df.drop(columns='geometry').copy()
    hazard_raster = xr.open_dataarray(f"/vsis3/{S3_BUCKET}/{HAZARD_INPUT_PATH['cyclone']}")
    hazard_data = hazard_raster[0].values
    df['max_speed'] = compute_zonal_stat(hazard_data, hazard_raster.rio.transform(), admin_df, agg='max')
    return df

def coastal_erosion(admin_df: gpd.GeoDataFrame) -> pd.DataFrame:
    """"
    Process coastal erosion data"
    """
    adm_col = next(col for col in ['adm2_src', 'adm1_src', 'adm0_src'] if col in admin_df.columns)
    hazard_df = gpd.read_file(f"/vsis3/{S3_BUCKET}/{HAZARD_INPUT_PATH['coastal_erosion']}")
    admin_df.geometry = admin_df.geometry.buffer(0.01)
    hazard_df = hazard_df[['rate_time', 'geometry']]
    merge_df = gpd.sjoin(admin_df, hazard_df)
    merge_df = merge_df.groupby([adm_col])['rate_time'].mean().reset_index()
    df = admin_df.merge(merge_df, on=adm_col, how='left')
    df = df.drop(columns='geometry')
    return df