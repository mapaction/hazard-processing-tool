from .hazards import (process_hazards, 
                      process_deforestation, 
                      process_cyclone, 
                      coastal_erosion)
from src.utils.utils import (prep_data, 
                             export_dataset)
from src.utils.constants import (ADMIN_VECTOR_PATH, 
                                  POPULATION_RASTER_PATH, 
                                  HAZARD_OUTPUT_PATH)
import geopandas as gpd
import xarray as xr

exposures = prep_data()

# 1) Load the GeoDataFrame from file
admin_df = gpd.read_file(ADMIN_VECTOR_PATH)
# (Optional) Keep only certain columns plus geometry
adm_complete_list = ['adm0_src','adm0_name','adm1_src','adm1_name','adm2_src','adm2_name']
adm_list = [col for col in adm_complete_list if col in admin_df.columns]
adm_list.append('geometry')
admin_df = admin_df[adm_list]
# 2) Open the population raster (using rasterio)
pop_raster = xr.open_dataarray(POPULATION_RASTER_PATH)

for hazard in ['flood', 'earthquake', 'landslide']:
    df = process_hazards(admin_df, pop_raster, exposures[hazard])
    export_dataset(df, hazard)
    print(f'Finished processing {hazard}')

df_deforestation = process_deforestation(admin_df)
export_dataset(df_deforestation, 'deforestation')
print(f'Finished processing deforestation')

df_cyclone = process_cyclone(admin_df)
export_dataset(df_cyclone, 'cyclone')   
print(f'Finished processing cyclone')

df_coastal_erosion = coastal_erosion(admin_df)
export_dataset(df_coastal_erosion, 'coastal_erosion')
print(f'Finished processing coastal erosion')