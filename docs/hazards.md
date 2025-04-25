# hazards.py

This module defines processing functions for each hazard type supported by the tool:

- process_flood: Reads flood raster, applies threshold,
  computes zonal statistics.
- process_earthquake: Opens earthquake hazard data,
  thresholds, and aggregates exposure.
- process_landslide: Processes landslide rasters similarly to
  flood and earthquake.
- process_deforestation: Computes separate statistics for tree
  cover loss and forest cover.
- process_cyclone: Loads cyclone wind return period data and
  summarizes by admin unit.
- coastal_erosion: Buffers administrative boundaries, reads
  shoreline erosion shapefile, and calculates mean erosion rate.

Each function takes a GeoDataFrame of administrative boundaries
and returns a pandas DataFrame with aggregated hazard metrics.
