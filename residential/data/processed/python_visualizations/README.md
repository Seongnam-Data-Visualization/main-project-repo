# Python Visualizations

Tableau 대신 Python에서 바로 확인할 수 있도록 만든 정적 시각화 산출물입니다.

## 입력 데이터

- `residential/data/processed/tableau/*.csv`
- `residential/data/raw/Dataset_v1/seongnam_dong.geojson`

## 산출물

- `01_admin_dong_households.png`
- `02_admin_households_vs_working_age.png`
- `03_map_admin_households.png`
- `04_map_working_age_ratio.png`
- `05_map_elderly_ratio.png`
- `06_gu_housing_stock_composition.png`
- `07_gu_housing_supply_per_household.png`
- `08_legal_dong_sales_price_heatmap.png`
- `09_legal_dong_jeonse_deposit_heatmap.png`
- `10_legal_dong_monthly_rent_heatmap.png`
- `11_transaction_volume_by_gu_and_type.png`
- `12_sales_price_distribution_by_type.png`
- `13_monthly_rent_deposit_scatter.png`
- `14_monthly_transaction_trends.png`

## 재생성

```powershell
python .\residential\data\scripts\make_pretty_visualizations.py
```

지도 이미지는 `geopandas`가 설치되어 있을 때 생성됩니다.