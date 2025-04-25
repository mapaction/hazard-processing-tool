# utils.py

This module provides geospatial utility functions supporting hazard
impact analysis. It includes raster mask generation, exposure computation,
and zonal statistics aggregation.

## compute_hazard_mask(hazard_raster, population_raster,hazard_threshold)

Reprojects a hazard raster to match the CRS of a population raster.
Applies a threshold to create a binary mask.

## compute_population_exposure(hazard_mask_raster,population_raster)

Multiplies the population raster by the binary hazard mask to compute exposed
population counts.

## prep_data(hazard_raster_paths, population_raster_path,hazard_threshold)

Loads all hazard and population rasters, applies mask and exposure computation
to return a data array per hazard.

## compute_zonal_stat(raster, vector, stats)

Uses rasterstats.zonal_stats to calculate aggregate statistics for a raster
over administrative boundaries.

## compute_hazard_population_exposure(hazard_raster,population_raster, hazard_threshold)

Computes population exposure, total population, and ratio of exposure per
admin unit.

### compute_binary_zonal_stat(raster_path, vector_path, threshold)
