import geopandas as gpd
import xarray as xr

from src.utils.constants import ADMIN_VECTOR_PATH, POPULATION_RASTER_PATH
from src.utils.s3 import export_dataset
from src.utils.utils import prep_data

from .hazards import (
    coastal_erosion,
    process_cyclone,
    process_deforestation,
    process_hazards,
)


def main():
    exposures = prep_data()

    # 1) Load the GeoDataFrame from file from S3
    admin_df = load_admin_data()

    # 2) Open the population raster from S3 using the VSI interface
    pop_raster_path = POPULATION_RASTER_PATH
    pop_raster = xr.open_dataarray(pop_raster_path)

    # Process hazards
    process_and_export_hazards(admin_df, pop_raster, exposures)

    # Process other specific hazards
    process_and_export_specific_hazards(admin_df)


def load_admin_data():
    """
    Reads the admin vector data from S3 using the VSI path.
    """

    admin_path = ADMIN_VECTOR_PATH
    admin_df = gpd.read_file(admin_path)
    adm_complete_list = [
        "adm0_src",
        "adm0_name",
        "adm1_src",
        "adm1_name",
        "adm2_src",
        "adm2_name",
    ]
    adm_list = [col for col in adm_complete_list if col in admin_df.columns]
    adm_list.append("geometry")
    return admin_df[adm_list]


def process_and_export_hazards(admin_df, pop_raster, exposures):
    for hazard in ["flood", "earthquake", "landslide"]:
        df = process_hazards(admin_df, pop_raster, exposures[hazard])
        export_dataset(df, hazard)
        print(f"Finished processing {hazard}")


def process_and_export_specific_hazards(admin_df):
    df_deforestation = process_deforestation(admin_df)
    export_dataset(df_deforestation, "deforestation")
    print("Finished processing deforestation")

    df_cyclone = process_cyclone(admin_df)
    export_dataset(df_cyclone, "cyclone")
    print("Finished processing cyclone")

    df_coastal_erosion = coastal_erosion(admin_df)
    export_dataset(df_coastal_erosion, "coastal_erosion")
    print("Finished processing coastal erosion")


if __name__ == "__main__":
    main()
