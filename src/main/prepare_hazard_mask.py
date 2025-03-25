import os
import boto3
import numpy as np
import rioxarray as rio
import xarray as xr
import rasterio
from rasterio.io import MemoryFile
from rasterio.session import AWSSession
from dotenv import load_dotenv

load_dotenv()

S3_BUCKET = os.getenv("S3_BUCKET", "hazard-processing-ma-tool-lambda-bucket")
boto3_session = boto3.Session(region_name=os.environ.get("AWS_DEFAULT_REGION"))
s3_client = boto3_session.client("s3")

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
    print(f"Reading raster from {s3_path}")
    with rasterio.Env(AWSSession(boto3_session)):
        return rio.open_rasterio(s3_path)

def write_raster_to_s3(raster, s3_key):
    """
    Writes a raster to a MemoryFile and uploads it to S3 using boto3.
    """
    print(f"Writing raster to memory...")

    raster_meta = {
        "driver": "GTiff",
        "dtype": str(raster.dtype),
        "nodata": raster.rio.nodata,
        "count": 1,
        "width": raster.rio.width,
        "height": raster.rio.height,
        "crs": raster.rio.crs,
        "transform": raster.rio.transform(),
    }

    with MemoryFile() as memfile:
        with memfile.open(**raster_meta) as dataset:
            dataset.write(raster.values[0], 1)  # Write the first band

        print(f"Uploading {s3_key} to S3")
        s3_client.put_object(Bucket=S3_BUCKET, Key=s3_key, Body=memfile.read())


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


def main(event, context):
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

if __name__ == "__main__":
    main({}, None)
