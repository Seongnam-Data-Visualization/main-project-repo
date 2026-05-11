# Tableau Import Guide

권장 사용 파일은 이 폴더의 CSV입니다.

1. 지도 레이어: `Dataset_v1/seongnam_dong.geojson`을 Tableau의 spatial file로 불러옵니다.
2. 행정동 수요: `01_admin_dong_demand.csv`를 `ADM_CD` 기준으로 지도 레이어와 연결합니다.
3. 주거 비용: 법정동 기준 분석은 `02_legal_dong_cost_summary.csv`를 사용합니다.
4. 행정동 지도 위 가격 표현: `03_admin_dong_cost_proxy.csv`를 사용하되, `가격매핑방식` 필터/라벨을 같이 확인합니다.
5. 주택 재고: 구 단위 자료라 `04_gu_housing_stock_reference.csv` 또는 `05_gu_demand_and_stock_reference.csv`로 별도 sheet에서 다룹니다.

주의: `03_admin_dong_cost_proxy.csv`는 공식 법정동-행정동 매핑이 아니라 행정동명 기반 추정 매핑입니다.