import os
import boto3
import numpy as np
import rioxarray as rio
import xarray as xr
from rasterio.session import AWSSession


S3_BUCKET = os.getenv("S3_BUCKET", "hazard-processing-ma-tool-lambda-bucket")


s3_client = boto3.Session().client("s3")

HAZARD_THRESHOLD = {
    "flood": 0.0,
    "earthquake": 0.115,
    "landslide": 2.5,
}


def read_raster_from_s3(s3_key):
    """
    Reads a raster file directly from S3 into an xarray DataArray.
    """
    s3_path = f"/vsis3/{S3_BUCKET}/{s3_key}"
    with rio.open_rasterio(s3_path) as dataset:
        return dataset


def write_raster_to_s3(raster, s3_key):
    """
    Writes a raster file to S3 directly.
    """
    s3_path = f"/vsis3/{S3_BUCKET}/{s3_key}"
    raster.rio.to_raster(s3_path)
    print(f"Saved {s3_key} to S3")


def compute_hazard_mask(hazard_raster: xr.DataArray, population_raster: xr.DataArray, hazard_threshold: float) -> xr.DataArray:
    """
    Transform hazard raster into a hazard mask raster following the population grid (1 - exposed / 0 - not exposed).
    """

    hazard_raster = hazard_raster.rio.reproject_match(population_raster)

    hazard_data = np.nan_to_num(hazard_raster[0].values)
    hazard_data[hazard_data <= hazard_threshold] = 0
    hazard_data[hazard_data > hazard_threshold] = 1

    hazard_mask_raster = hazard_raster
    hazard_mask_raster.values = [hazard_data]

    return hazard_mask_raster


def compute_population_exposure(hazard_mask_raster: xr.DataArray, population_raster: xr.DataArray) -> xr.DataArray:
    """
    Combine population and hazard mask rasters to compute exposed population raster.
    """
    pop_hazard_array = np.multiply(population_raster[0].values, hazard_mask_raster[0].values)
    pop_exp_raster = hazard_mask_raster
    pop_exp_raster.values = [pop_hazard_array]
    pop_exp_raster = pop_exp_raster.rio.write_crs("epsg:4326")

    return pop_exp_raster


def lambda_handler(event, context):
    """
    AWS Lambda entry point for hazard mask computation.
    """
    population_raster = read_raster_from_s3("pop_data/sadc_pop_1km.tif")

    for hazard, threshold in HAZARD_THRESHOLD.items():
        hazard_raster = read_raster_from_s3(f"hazard_data/{hazard}/sadc_{hazard}.tif")
        hazard_mask_raster = compute_hazard_mask(hazard_raster, population_raster, threshold)
        population_exposure_raster = compute_population_exposure(hazard_mask_raster, population_raster)

        # Save processed raster to S3
        output_path = f"prep_data/sadc_{hazard}_prep.tif"
        write_raster_to_s3(population_exposure_raster, output_path)

    return {"statusCode": 200, "body": "Hazard masks prepared and saved to S3"}
