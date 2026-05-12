# Python Visualization Figure Guide

이 문서는 `residential/data/processed/python_visualizations` 폴더에 생성된 각 figure가 무엇을 보여주는지 정리한 설명서입니다. 모든 figure는 `residential/data/processed/tableau`의 CSV와 `residential/data/raw/Dataset_v1/seongnam_dong.geojson`을 기반으로 생성했습니다.

## 01_admin_dong_households.png

- 의미: 성남시 행정동별 세대수 규모를 비교한 가로 막대그래프입니다.
- 사용 데이터: `01_admin_dong_demand.csv`
- 해석 포인트: 세대수가 많은 행정동은 주거 수요의 절대 규모가 큰 지역으로 볼 수 있습니다. 막대 색상은 구를 나타냅니다.

## 02_admin_households_vs_working_age.png

- 의미: 행정동별 세대수와 생산가능인구(19-64세)의 관계를 보여주는 산점도입니다.
- 사용 데이터: `01_admin_dong_demand.csv`
- 해석 포인트: 오른쪽 위에 있는 행정동일수록 세대수와 생산가능인구가 모두 큰 지역입니다. 점 크기는 65세 이상 인구비율을 의미합니다.

## 03_map_admin_households.png

- 의미: 행정동별 세대수를 지도 위에 표현한 choropleth map입니다.
- 사용 데이터: `01_admin_dong_demand.csv`, `seongnam_dong.geojson`
- 해석 포인트: 색이 진할수록 세대수가 많습니다. 지리적으로 주거 수요 규모가 집중된 행정동을 확인하기 위한 지도입니다.

## 04_map_working_age_ratio.png

- 의미: 행정동별 생산가능인구(19-64세) 비율을 지도 위에 표현한 figure입니다.
- 사용 데이터: `01_admin_dong_demand.csv`, `seongnam_dong.geojson`
- 해석 포인트: 색이 진할수록 총인구 대비 생산가능인구 비율이 높습니다. 직주근접, 임대 수요, 활동 인구 기반 수요를 볼 때 참고할 수 있습니다.

## 05_map_elderly_ratio.png

- 의미: 행정동별 65세 이상 인구 비율을 지도 위에 표현한 figure입니다.
- 사용 데이터: `01_admin_dong_demand.csv`, `seongnam_dong.geojson`
- 해석 포인트: 색이 진할수록 고령인구 비율이 높습니다. 고령화된 주거지역과 상대적으로 젊은 수요가 많은 지역을 비교할 수 있습니다.

## 06_gu_housing_stock_composition.png

- 의미: 구별 주택 재고 구성을 100% 누적 막대그래프로 보여줍니다.
- 사용 데이터: `gu_housing_stock_long.csv`
- 해석 포인트: 각 구의 주택 재고가 아파트, 단독/다가구, 연립/다세대 등 어떤 유형 중심으로 구성되어 있는지 비교합니다.

## 07_gu_housing_supply_per_household.png

- 의미: 구별 세대수 대비 주택수 비율을 비교한 막대그래프입니다.
- 사용 데이터: `05_gu_demand_and_stock_reference.csv`
- 해석 포인트: 값이 1.00에 가까울수록 세대수와 주택수가 비슷합니다. 단, 주택 재고 데이터는 구 단위라 행정동 단위 세부 비교에는 사용하지 않았습니다.

## 08_legal_dong_sales_price_heatmap.png

- 의미: 법정동과 건축유형별 매매가 평당 중앙값을 히트맵으로 보여줍니다.
- 사용 데이터: `02_legal_dong_cost_summary.csv`
- 해석 포인트: 색이 진할수록 평당 매매가가 높습니다. 거래건수 10건 이상인 법정동-건축유형 조합만 표시했습니다.

## 09_legal_dong_jeonse_deposit_heatmap.png

- 의미: 법정동과 건축유형별 전세보증금 평당 중앙값을 히트맵으로 보여줍니다.
- 사용 데이터: `02_legal_dong_cost_summary.csv`
- 해석 포인트: 색이 진할수록 평당 전세보증금이 높습니다. 매매가와 비교해 전세 수요가 강한 지역/유형을 확인할 수 있습니다.

## 10_legal_dong_monthly_rent_heatmap.png

- 의미: 법정동과 건축유형별 월세 평당 중앙값을 히트맵으로 보여줍니다.
- 사용 데이터: `02_legal_dong_cost_summary.csv`
- 해석 포인트: 색이 진할수록 평당 월세가 높습니다. 월세형 임대 수익성이 상대적으로 높은 법정동-건축유형 조합을 확인하기 위한 참고 figure입니다.

## 11_transaction_volume_by_gu_and_type.png

- 의미: 구별, 건축유형별 거래건수를 매매/전세/월세로 나누어 비교한 막대그래프입니다.
- 사용 데이터: `02_legal_dong_cost_summary.csv`
- 해석 포인트: 가격 수준뿐 아니라 실제 거래량이 어느 구와 건축유형에 집중되는지 확인할 수 있습니다. 거래량이 낮은 조합은 가격 중앙값 해석에 주의가 필요합니다.

## 12_sales_price_distribution_by_type.png

- 의미: 건축유형별 매매가 평당 분포를 구별로 비교한 boxplot입니다.
- 사용 데이터: `transactions_sales_long.csv`
- 해석 포인트: 중앙선은 중앙값, 박스는 주요 분포 범위를 나타냅니다. IQR 기준 이상치는 제외해 극단값보다 전반적인 가격 분포를 보도록 했습니다.

## 13_monthly_rent_deposit_scatter.png

- 의미: 월세 거래의 보증금과 월세 관계를 보여주는 산점도입니다.
- 사용 데이터: `transactions_rent_long.csv`
- 해석 포인트: x축은 보증금, y축은 월세입니다. 보증금 축은 로그 스케일입니다. 구와 건축유형별 월세 거래 구조 차이를 확인할 수 있습니다.

## 14_monthly_transaction_trends.png

- 의미: 월별 매매가 평당 중앙값과 전월세 거래건수 추이를 함께 보여줍니다.
- 사용 데이터: `transactions_sales_long.csv`, `transactions_rent_long.csv`
- 해석 포인트: 상단은 구별 월별 매매가 중앙값, 하단은 구별 월별 전세/월세 거래건수입니다. 원자료 기간이 2025.5.13-2026.5.12이므로 2025년 5월과 2026년 5월은 부분월입니다.

## 주의사항

- `03_admin_dong_cost_proxy.csv` 기반 지도 가격 시각화는 공식 법정동-행정동 매핑이 아니라 행정동명 기반 추정 매핑이므로 이번 figure 묶음에서는 직접 사용하지 않았습니다.
- 가격 heatmap은 법정동 단위, 인구/세대 지도는 행정동 단위입니다. 두 단위를 직접 동일 지역처럼 해석하면 안 됩니다.
- 실거래가 데이터는 다운로드 시점 기준 최근 1년(2025.5.13-2026.5.12) 자료입니다.
