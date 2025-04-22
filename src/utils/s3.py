import boto3
import pandas as pd
import rasterio
from rasterio.session import AWSSession

from .constants import (
    AWS_ACCESS_KEY_ID,
    AWS_DEFAULT_REGION,
    AWS_SECRET_ACCESS_KEY,
    HAZARD_OUTPUT_PATH,
    S3_BUCKET,
)

boto3_session = boto3.Session(
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_DEFAULT_REGION,
)

s3_client = boto3_session.client("s3")


def read_raster_from_s3(s3_key):
    """
    Reads a raster file from S3 directly using Rasterio.
    """
    s3_path = f"/vsis3/{S3_BUCKET}/{s3_key}"
    with rasterio.Env(AWSSession(boto3_session)):
        return rasterio.open(s3_path)


def export_dataset(df: pd.DataFrame, hazard: str) -> None:
    """
    Export the computed hazard data as a CSV file directly to S3.
    """

    if "adm2_src" in df.columns:
        df.sort_values(by=["adm1_src", "adm2_src"], inplace=True)

    csv_str = df.to_csv(index=False)
    s3_key = HAZARD_OUTPUT_PATH.get(hazard)
    if not s3_key:
        raise ValueError(f"Invalid hazard type: {hazard}")
    s3_client.put_object(Bucket=S3_BUCKET, Key=s3_key, Body=csv_str)
    print(f"Saved {s3_key} to S3")
