import rioxarray as rio
import xarray as xr
import numpy as np
import geopandas as gpd
from rasterstats import zonal_stats
from affine import Affine
from typing import List, Dict
import pandas as pd
import rasterio
from .constants import (
    S3_BUCKET,
    HAZARD_RASTER_PATH, 
    POPULATION_RASTER_PATH, 
    HAZARD_THRESHOLD,
    HAZARD_OUTPUT_PATH  # You may no longer need this here if export_dataset moves to s3.py
)

def compute_hazard_mask(hazard_raster: xr.DataArray, 
                        population_raster: xr.DataArray, 
                        hazard_threshold: float
                        ) -> xr.DataArray:
    """"
    Compute hazard mask from hazard raster and population raster"
    """
    hazard_raster = hazard_raster.rio.reproject_match(population_raster)
    hazard_data = hazard_raster[0].values
    hazard_data = np.nan_to_num(hazard_data)
    hazard_data[hazard_data <= hazard_threshold] = 0
    hazard_data[hazard_data > hazard_threshold] = 1
    hazard_mask_raster = hazard_raster
    hazard_mask_raster.values = [hazard_data]
    return hazard_mask_raster

def compute_population_exposure(hazard_mask_raster: xr.DataArray, 
                                population_raster: xr.DataArray
                                ) -> xr.DataArray:
    """"
    Compute population exposure from hazard mask raster and population raster""
    """
    pop_hazard_array = np.multiply(
        population_raster[0].values,hazard_mask_raster[0].values
        )
    pop_exp_raster = hazard_mask_raster
    pop_exp_raster.values = [pop_hazard_array]
    pop_exp_raster = pop_exp_raster.rio.write_crs("epsg:4326")
    return pop_exp_raster

def prep_data()-> Dict[str, xr.DataArray]:
    """"
    Prepare data for exposure computation"
    """
    prep_exposures = {}
    for hazard in HAZARD_RASTER_PATH:
        hazard_raster_path = f"/vsis3/{S3_BUCKET}/{HAZARD_RASTER_PATH[hazard]}"
        pop_raster_path = f"/vsis3/{S3_BUCKET}/{POPULATION_RASTER_PATH}"
        hazard_raster = xr.open_dataarray(hazard_raster_path)
        population_raster = xr.open_dataarray(pop_raster_path)
        hazard_mask_raster = compute_hazard_mask(hazard_raster, population_raster, HAZARD_THRESHOLD[hazard])
        population_exposure_raster = compute_population_exposure(hazard_mask_raster, population_raster)
        prep_exposures[hazard] = population_exposure_raster
    return prep_exposures

def compute_zonal_stat(data_value:np.ndarray, 
                       exp_affine: Affine,
                       admin_df:gpd.GeoDataFrame, 
                       agg:str
                       )->List[float]:
    """""
    Compute zonal statistics for raster/pop the exposure data"
    """
    stats = zonal_stats(admin_df, data_value, affine=exp_affine, stats=agg)
    value_list = [x[agg] for x in stats]
    return value_list

def compute_hazard_population_exposure(admin_df: gpd.GeoDataFrame, 
                                       pop_raster:xr.DataArray, 
                                       pop_exp_raster: xr.DataArray
                                       )-> pd.DataFrame:
    
    pop_arr = pop_raster[0].values
    pop_affine = pop_raster.rio.transform()

    exp_arr = pop_exp_raster[0].values
    exp_affine = pop_exp_raster.rio.transform()
    
    
    exposure_df = admin_df.drop(columns='geometry').copy() # drop the geometry column
    exposure_df['pop_exp'] = compute_zonal_stat(exp_arr, exp_affine, admin_df, agg='sum')
    exposure_df['pop_tot'] = compute_zonal_stat(pop_arr, pop_affine, admin_df, agg='sum')
    exposure_df['exp_ratio'] = exposure_df['pop_exp']/exposure_df['pop_tot']
    return exposure_df

def compute_binary_zonal_stat(raster_path: str, 
                              admin_df: gpd.GeoDataFrame, 
                              threshold: float=0
                              ) -> List[float]:
    """
    Compute zonal statistics for binary data.
    Reads the raster from S3 using the VSI interface.
    """
    # Build full S3 path for the raster
    full_raster_path = f"/vsis3/{S3_BUCKET}/{raster_path}"
    with rasterio.open(full_raster_path) as src:
        data = np.nan_to_num(src.read(1))
        data[data <= threshold] = 0
        data[data > threshold] = 1
        return compute_zonal_stat(data, src.transform, admin_df, agg='sum')