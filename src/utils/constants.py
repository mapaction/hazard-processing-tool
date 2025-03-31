from pathlib import Path

parent_dir = Path.cwd()

POPULATION_RASTER_PATH = parent_dir / './pop_data/sadc_pop_1km.tif'

HAZARD_RASTER_PATH = {
    'flood': parent_dir / './hazard_data/flood/sadc_flood.tif',
    'earthquake': parent_dir / './hazard_data/earthquake/sadc_earthquake.tif',
    'landslide': parent_dir / './hazard_data/landslide/sadc_landslide.tif'
}

HAZARD_THRESHOLD = {
    'flood': 0.0,
    'earthquake': 0.115,
    'landslide': 2.5,
    'deforestation': 0.0
}

ADMIN_VECTOR_PATH = parent_dir /'./admin_data/sadc_adm1.geojson'

HAZARD_INPUT_PATH = {
    'cyclone': parent_dir / './hazard_data/cyclone/STORM_FIXED_RETURN_PERIODS_SI_100_YR_RP.tif',
    'coastal_erosion': parent_dir / './hazard_data/coastal_erosion/sadc_coastal_erosion.shp',
        'deforestation': {
        'loss': parent_dir / './hazard_data/deforestation/sadc_lossyear.tif',
        'cover': parent_dir / './hazard_data/deforestation/sadc_treecover.tif'
    }
}

HAZARD_OUTPUT_PATH = {
    'flood' : parent_dir / './output_data/flood/flood.csv',
    'earthquake' : parent_dir / './output_data/earthquake/earthquake.csv',
    'landslide' : parent_dir / './output_data/landslide/landslide.csv',
    'deforestation' : parent_dir / './output_data/deforestation/deforestation.csv',
    'cyclone' : parent_dir / './output_data/cyclone/cyclone.csv',
    'coastal_erosion' : parent_dir / './output_data/coastal_erosion/coastal_erosion.csv'
}