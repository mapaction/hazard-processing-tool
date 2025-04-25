from pathlib import Path

import boto3
import pandas as pd

from .constants import (
    AWS_ACCESS_KEY_ID,
    AWS_DEFAULT_REGION,
    AWS_SECRET_ACCESS_KEY,
    HAZARD_OUTPUT_PATH,
    S3_BUCKET,
    USE_LOCAL,
)

boto3_session = boto3.Session(
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_DEFAULT_REGION,
)

s3_client = boto3_session.client("s3")


def export_dataset(df: pd.DataFrame, hazard: str) -> None:
    """
    Export the computed hazard data as a CSV file directly to S3.
    """

    if "adm2_src" in df.columns:
        df.sort_values(by=["adm1_src", "adm2_src"], inplace=True)

    out_path = HAZARD_OUTPUT_PATH.get(hazard)
    if not out_path:
        raise ValueError(f"Invalid hazard type: {hazard}")

    if USE_LOCAL:
        out_path = Path(out_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(out_path, index=False)
        print(f"Saved {out_path} locally")
    else:
        # Write to S3 using boto3
        csv_bytes = df.to_csv(index=False).encode("utf-8")
        s3_client.put_object(Bucket=S3_BUCKET, Key=out_path, Body=csv_bytes)
        print(f"Saved {out_path} to S3")
