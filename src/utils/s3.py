from rasterio.session import AWSSession
import rasterio
import boto3
from .constants import ( S3_BUCKET, 
                        AWS_ACCESS_KEY_ID, 
                        AWS_SECRET_ACCESS_KEY, 
                        AWS_DEFAULT_REGION, 
                        POPULATION_RASTER_PATH, 
                        HAZARD_RASTER_PATH, 
                        HAZARD_INPUT_PATH, 
                        HAZARD_OUTPUT_PATH )

boto3_session = boto3.Session(
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_DEFAULT_REGION
)

s3_client = boto3_session.client("s3")

def read_raster_from_s3(s3_key):
    """
    Reads a raster file from S3 directly using Rasterio.
    """
    s3_path = f"/vsis3/{S3_BUCKET}/{s3_key}"
    with rasterio.Env(AWSSession(boto3_session)):
        return rasterio.open(s3_path)
