Quickly explore a dataset file and produce a summary report.

The user will provide a file path. Supported formats: CSV, GeoJSON, Parquet, GeoPackage (.gpkg), GeoTIFF/raster (.tif, .tiff).

Steps:
1. Detect the file format from the extension
2. Run the appropriate Python EDA:

For CSV/Parquet:
```python
import pandas as pd
df = pd.read_csv("PATH")  # or read_parquet
print(f"Shape: {df.shape}")
print(f"\nDtypes:\n{df.dtypes}")
print(f"\nMissing values:\n{df.isnull().sum()[df.isnull().sum() > 0]}")
print(f"\nSample (5 rows):\n{df.head()}")
print(f"\nNumeric summary:\n{df.describe()}")
```

For GeoJSON/GeoPackage:
```python
import geopandas as gpd
gdf = gpd.read_file("PATH")
print(f"Shape: {gdf.shape}")
print(f"CRS: {gdf.crs}")
print(f"Geometry type: {gdf.geometry.geom_type.value_counts().to_dict()}")
print(f"Bounds: {gdf.total_bounds}")
print(f"\nDtypes:\n{gdf.dtypes}")
print(f"\nSample (5 rows):\n{gdf.head()}")
```

For GeoTIFF/raster:
```python
import rasterio
with rasterio.open("PATH") as src:
    print(f"Size: {src.width} x {src.height}")
    print(f"Bands: {src.count}")
    print(f"CRS: {src.crs}")
    print(f"Transform: {src.transform}")
    print(f"Bounds: {src.bounds}")
    print(f"Dtype: {src.dtypes}")
    import numpy as np
    for i in range(1, src.count + 1):
        band = src.read(i)
        print(f"Band {i} — min: {np.nanmin(band):.4f}, max: {np.nanmax(band):.4f}, mean: {np.nanmean(band):.4f}, nodata: {src.nodata}")
```

3. Present the results in a clean, readable format with key observations
4. Flag any potential issues: high null rates (>20%), suspicious ranges, mixed types, large file size

Important:
- Run the python code via Bash
- If a library is missing, say which one and suggest how to install it
- Keep output concise — highlight what's interesting or unusual
