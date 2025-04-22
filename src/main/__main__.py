from .hazards import (
    process_hazards, 
    process_deforestation, 
    process_cyclone, 
    coastal_erosion
)
from src.utils.utils import prep_data
from src.utils.s3 import export_dataset  # Updated: export_dataset is now in s3.py
from src.utils.constants import (
    POPULATION_RASTER_PATH, 
    S3_BUCKET
)
import geopandas as gpd
import xarray as xr

def main():
    exposures = prep_data()

    # 1) Load the GeoDataFrame from file from S3
    admin_df = load_admin_data()

    # 2) Open the population raster from S3 using the VSI interface
    pop_raster_path = f"/vsis3/{S3_BUCKET}/{POPULATION_RASTER_PATH}"
    pop_raster = xr.open_dataarray(pop_raster_path)

    # Process hazards
    process_and_export_hazards(admin_df, pop_raster, exposures)

    # Process other specific hazards
    process_and_export_specific_hazards(admin_df)

def load_admin_data():
    """
    Reads the admin vector data from S3 using the VSI path.
    Note: This requires that your GDAL/Fiona installation supports the /vsis3/ interface.
    """
    from src.utils.constants import S3_BUCKET, ADMIN_VECTOR_PATH
    admin_path = f"/vsis3/{S3_BUCKET}/{ADMIN_VECTOR_PATH}"
    admin_df = gpd.read_file(admin_path)
    adm_complete_list = ['adm0_src', 'adm0_name', 'adm1_src', 'adm1_name', 'adm2_src', 'adm2_name']
    adm_list = [col for col in adm_complete_list if col in admin_df.columns]
    adm_list.append('geometry')
    return admin_df[adm_list]

def process_and_export_hazards(admin_df, pop_raster, exposures):
    for hazard in ['flood', 'earthquake', 'landslide']:
        df = process_hazards(admin_df, pop_raster, exposures[hazard])
        export_dataset(df, hazard)
        print(f'Finished processing {hazard}')

def process_and_export_specific_hazards(admin_df):
    df_deforestation = process_deforestation(admin_df)
    export_dataset(df_deforestation, 'deforestation')
    print('Finished processing deforestation')

    df_cyclone = process_cyclone(admin_df)
    export_dataset(df_cyclone, 'cyclone')
    print('Finished processing cyclone')

    df_coastal_erosion = coastal_erosion(admin_df)
    export_dataset(df_coastal_erosion, 'coastal_erosion')
    print('Finished processing coastal erosion')

if __name__ == "__main__":
    main()
