import os
import boto3
import geopandas as gpd
import rasterio
from rasterstats import zonal_stats
import numpy as np
import affine
import pandas as pd
from rasterio.session import AWSSession
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get S3 bucket name from environment variable
S3_BUCKET = os.getenv("S3_BUCKET", "hazard-processing-ma-tool-lambda-bucket")

# Create a boto3 session and then a client
boto3_session = boto3.Session()
s3_client = boto3_session.client("s3")


def read_raster_from_s3(s3_key):
    """
    Reads a raster file from S3 directly using Rasterio.
    """
    s3_path = f"/vsis3/{S3_BUCKET}/{s3_key}"
    with rasterio.Env(AWSSession(boto3_session)):
        return rasterio.open(s3_path)


def compute_zonal_stat(data_value: np.ndarray, exp_affine: affine.Affine, 
    admin_df: gpd.geodataframe.GeoDataFrame, agg: str) -> list:
    """
    Compute zonal statistics for a raster and a set of polygons.
    """
    stats = zonal_stats(admin_df, data_value, affine=exp_affine, stats=agg)
    value_list = []
    for x in stats:
        value_list.append(x[agg])
    return value_list


def compute_hazard_population_exposure(admin_df: gpd.geodataframe.GeoDataFrame, pop_raster: rasterio.io.DatasetReader, 
    pop_exp_raster: rasterio.io.DatasetReader) -> pd.core.frame.DataFrame:
    """
    Compute the population exposed to a hazard per administrative division.
    """
    df = admin_df.drop(columns='geometry').copy()
    df['pop_exp'] = compute_zonal_stat(pop_exp_raster.read(1), pop_exp_raster.transform, admin_df, agg='sum')
    df['pop_tot'] = compute_zonal_stat(pop_raster.read(1), pop_raster.transform, admin_df, agg='sum')
    df['exp_ratio'] = df['pop_exp'] / df['pop_tot']
    return df
