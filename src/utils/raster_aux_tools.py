
import geopandas as gpd
import rasterio
from rasterstats import zonal_stats
import numpy as np
import affine
import pandas as pd


def compute_zonal_stat(data_value: np.ndarray, exp_affine: affine.Affine, 
    admin_df: gpd.geodataframe.GeoDataFrame, agg: str) -> list:
    """
    Compute zonal statistics for a raster and a set of polygons.
    """
        
    stats = zonal_stats(admin_df, data_value, affine=exp_affine, stats = agg)
    
    value_list = []
    for x in stats:
        value_list.append(x[agg])

    
    return(value_list)



def compute_hazard_population_exposure(admin_df: gpd.geodataframe.GeoDataFrame, pop_raster: rasterio.io.DatasetReader, 
    pop_exp_raster: rasterio.io.DatasetReader) -> pd.core.frame.DataFrame:
    """
    Compute the population exposed to a hazard per administrative division.
    """

    df = admin_df.drop(columns = 'geometry').copy()
    df['pop_exp'] = compute_zonal_stat(pop_exp_raster.read(1), pop_exp_raster.transform, admin_df, agg = 'sum')
    df['pop_tot'] = compute_zonal_stat(pop_raster.read(1), pop_raster.transform, admin_df, agg = 'sum')
    df['exp_ratio'] = df['pop_exp']/df['pop_tot']


    return df
