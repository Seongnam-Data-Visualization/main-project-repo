import geopandas as gpd

path = r"C:\Users\rdh08\Desktop\2026_Data_Visualization\Dataset\BND_ADM_DONG_PG\BND_ADM_DONG_PG.shp"
gdf = gpd.read_file(path)
# gdf.to_file("seongnam_dong.geojson", driver="GeoJSON")

print(gdf.head())