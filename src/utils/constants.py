import os

from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.expanduser("~/.hazard_tool_rc"))

USE_LOCAL = os.getenv("USE_LOCAL", "false").lower() == "true"

S3_BUCKET = os.getenv("S3_BUCKET")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_DEFAULT_REGION = os.getenv("AWS_DEFAULT_REGION")

PATH = "/vsis3/" + S3_BUCKET + "/" if not USE_LOCAL else "./"

POPULATION_RASTER_PATH = PATH + "pop_data/sadc_pop_1km.tif"

HAZARD_RASTER_PATH = {
    "flood": PATH + "hazard_data/flood/sadc_flood.tif",
    "earthquake": PATH + "hazard_data/earthquake/sadc_earthquake.tif",
    "landslide": PATH + "hazard_data/landslide/sadc_landslide.tif",
}

HAZARD_THRESHOLD = {
    "flood": 0.0,
    "earthquake": 0.115,
    "landslide": 2.5,
    "deforestation": 0.0,
}

ADMIN_VECTOR_PATH = PATH + "admin_data/sadc_adm1.geojson"

HAZARD_INPUT_PATH = {
    "cyclone": (
        PATH
        + "hazard_data/cyclone/STORM_FIXED_RETURN_PERIODS_SI_100_YR_RP.tif"  # noqa: E501
    ),
    "coastal_erosion": PATH + "hazard_data/coastal_erosion/sadc_coastal_erosion.shp",
    "deforestation": {
        "loss": PATH + "hazard_data/deforestation/sadc_lossyear.tif",
        "cover": PATH + "hazard_data/deforestation/sadc_treecover.tif",
    },
}

HAZARD_OUTPUT_PATH = {
    "flood": "output_data/flood/flood.csv",
    "earthquake": "output_data/earthquake/earthquake.csv",
    "landslide": "output_data/landslide/landslide.csv",
    "deforestation": "output_data/deforestation/deforestation.csv",
    "cyclone": "output_data/cyclone/cyclone.csv",
    "coastal_erosion": "output_data/coastal_erosion/coastal_erosion.csv",
}
