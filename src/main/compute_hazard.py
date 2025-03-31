import os
import boto3
import geopandas as gpd
import pandas as pd
import numpy as np
import rasterio
from rasterstats import zonal_stats
from src.utils.raster_aux_tools import ( read_raster_from_s3, 
                                        compute_zonal_stat, 
                                        compute_hazard_population_exposure
)
from dotenv import load_dotenv


# Load environment variables from .env file
load_dotenv()

# Set S3 bucket name from env (default if not set)
S3_BUCKET = os.getenv("S3_BUCKET", "hazard-processing-ma-tool-lambda-bucket")
s3_client = boto3.client("s3")

# Update file paths to be S3 keys (remove the './')
POPULATION_RASTER_PATH = "pop_data/sadc_pop_1km.tif"
ADMIN_VECTOR_PATH = "admin_data/sadc_adm1.geojson"

HAZARD_INPUT_PATH = {
    'flood': "prep_data/sadc_flood_prep.tif",
    'earthquake': "prep_data/sadc_earthquake_prep.tif",
    'landslide': "prep_data/sadc_landslide_prep.tif",
    'cyclone': "hazard_data/cyclone/STORM_FIXED_RETURN_PERIODS_SI_100_YR_RP.tif",
    'coastal_erosion': "hazard_data/coastal_erosion/sadc_coastal_erosion.shp",
    'deforestation': {
        'loss': "hazard_data/deforestation/sadc_lossyear.tif",
        'cover': "hazard_data/deforestation/sadc_treecover.tif"
    }
}

HAZARD_OUTPUT_PATH = {
    'flood': "output_data/flood.csv",
    'earthquake': "output_data/earthquake.csv",
    'landslide': "output_data/landslide.csv",
    'cyclone': "output_data/cyclone.csv",
    'coastal_erosion': "output_data/coastal_erosion.csv",
    'deforestation': "output_data/deforestation.csv"
}


def process_flood(admin_df: gpd.GeoDataFrame,
    pop_raster: rasterio.io.DatasetReader) -> pd.DataFrame:
    """
    Compute Hazard level for Flood through exposed population.
    """
    pop_exp_raster = read_raster_from_s3(HAZARD_INPUT_PATH['flood'])
    df = compute_hazard_population_exposure(admin_df, pop_raster, pop_exp_raster)
    return df


def process_earthquake(admin_df: gpd.GeoDataFrame, 
    pop_raster: rasterio.io.DatasetReader) -> pd.DataFrame:
    """
    Compute Hazard level for Earthquake through exposed population.
    """
    pop_exp_raster = read_raster_from_s3(HAZARD_INPUT_PATH['earthquake'])
    df = compute_hazard_population_exposure(admin_df, pop_raster, pop_exp_raster)
    return df


def process_landslide(admin_df: gpd.GeoDataFrame, 
    pop_raster: rasterio.io.DatasetReader) -> pd.DataFrame:
    """
    Compute Hazard level for Landslide through exposed population.
    """    
    pop_exp_raster = read_raster_from_s3(HAZARD_INPUT_PATH['landslide'])
    df = compute_hazard_population_exposure(admin_df, pop_raster, pop_exp_raster)
    return df


def process_deforestation(admin_df: gpd.GeoDataFrame) -> pd.DataFrame:
    """
    Compute Hazard level for Deforestation through ratio between treecover loss and initial treecover.
    """
    df = admin_df.drop(columns='geometry').copy()
    hazard_threshold = 0

    loss_raster = read_raster_from_s3(HAZARD_INPUT_PATH['deforestation']['loss'])
    loss_data = np.nan_to_num(loss_raster.read(1))
    loss_data[loss_data <= hazard_threshold] = 0
    loss_data[loss_data > hazard_threshold] = 1
    df['loss'] = compute_zonal_stat(loss_data, loss_raster.transform, admin_df, agg='sum')

    cover_raster = read_raster_from_s3(HAZARD_INPUT_PATH['deforestation']['cover'])
    cover_data = np.nan_to_num(cover_raster.read(1))
    cover_data[cover_data <= hazard_threshold] = 0
    cover_data[cover_data > hazard_threshold] = 1
    df['cover'] = compute_zonal_stat(cover_data, cover_raster.transform, admin_df, agg='sum')

    df['deforestation'] = df['loss'] / df['cover']
    
    return df


def process_cyclone(admin_df: gpd.GeoDataFrame) -> pd.DataFrame:
    """
    Compute Hazard level for Cyclone through maximum speed for a fixed return period.
    """
    df = admin_df.drop(columns='geometry').copy()
    cyclone_raster = read_raster_from_s3(HAZARD_INPUT_PATH['cyclone'])
    cyclone_data = cyclone_raster.read(1)
    df['max_speed'] = compute_zonal_stat(cyclone_data, cyclone_raster.transform, admin_df, agg='max')
    return df


def process_coastal_erosion(admin_df: gpd.GeoDataFrame, adm_col: str) -> pd.DataFrame:
    """
    Compute Hazard level for Coastal Erosion through mean erosion ratio over coastline.
    """
    # Read the coastal erosion shapefile from S3 using a URL (requires s3fs)
    coastal_path = f"s3://{S3_BUCKET}/{HAZARD_INPUT_PATH['coastal_erosion']}"
    hazard_df = gpd.read_file(coastal_path)

    admin_df.geometry = admin_df.geometry.buffer(0.01)
    hazard_df = hazard_df[['rate_time','geometry']]
    merge_df = gpd.sjoin(admin_df, hazard_df)
    merge_df = merge_df.groupby([adm_col])['rate_time'].mean().reset_index()
    df = admin_df.merge(merge_df, on=adm_col, how='left')
    df = df.drop(columns='geometry')
    return df


def export_dataset(df: pd.DataFrame, hazard: str):
    """
    Export the computed hazard data as CSV to S3.
    """
    if 'adm2_src' in df.columns:
        df.sort_values(by=['adm1_src', 'adm2_src'], inplace=True)
    csv_str = df.to_csv(index=False)
    s3_key = HAZARD_OUTPUT_PATH[hazard]
    s3_client.put_object(Bucket=S3_BUCKET, Key=s3_key, Body=csv_str)
    print(f"Saved {s3_key} to S3")


def main():
    # Read population raster from S3
    pop_raster = read_raster_from_s3(POPULATION_RASTER_PATH)
    # Read admin vector using GeoPandas with S3 support (requires s3fs)
    admin_df = gpd.read_file(f"s3://{S3_BUCKET}/{ADMIN_VECTOR_PATH}")

    adm_complete_list = ['adm0_src', 'adm0_name', 'adm1_src', 'adm1_name', 'adm2_src', 'adm2_name']
    adm_list = [adm_col for adm_col in adm_complete_list if adm_col in admin_df.columns]
    adm_list.append('geometry')
    admin_df = admin_df[adm_list]

    df = process_flood(admin_df, pop_raster)
    export_dataset(df, 'flood')

    df = process_earthquake(admin_df, pop_raster)
    export_dataset(df, 'earthquake')

    df = process_landslide(admin_df, pop_raster)
    export_dataset(df, 'landslide')

    df = process_deforestation(admin_df)
    export_dataset(df, 'deforestation')

    df = process_cyclone(admin_df)
    export_dataset(df, 'cyclone')

    if 'adm2_src' in admin_df.columns:
        adm_col = 'adm2_src'
    elif 'adm1_src' in admin_df.columns:
        adm_col = 'adm1_src'
    else:
        adm_col = 'adm0_src'
    df = process_coastal_erosion(admin_df, adm_col)
    export_dataset(df, 'coastal_erosion')


if __name__ == "__main__":
    main()
