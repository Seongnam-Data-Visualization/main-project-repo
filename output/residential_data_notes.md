# Residential Data Notes

- 세대수/인구: `2026.3 인구현황(1인세대수 현황 포함).xlsx` 첫 시트에서 행정동별 세대수와 인구를 추출했습니다.
- 지도 조인: `Dataset_v1/seongnam_dong.geojson`의 `ADM_CD`와 `동`을 세대수 테이블에 붙였습니다.
- 생산가능인구_19_64세: 원자료의 `19세 이상`에서 `65세 이상`을 뺀 값으로 계산했습니다.
- 기본 granularity: 생활권 재정의 목적에 맞춰 행정동 수요 테이블과 법정동 실거래가 테이블을 분리했습니다.
- 주택 재고: `경기도 성남시_주택_통계_20250618.csv`가 구 단위 총량만 제공하므로 동 단위 테이블에 억지 배분하지 않고 구 단위 reference로 분리했습니다.
- 공동주택현황: 단지별 세대수는 별도 `apartment_complexes_clean.csv`로 저장했습니다. 전체 주택 재고가 아니므로 총 공급량에는 합산하지 않았습니다.
- 실거래가: 국토교통부 실거래가 CSV의 안내문 이후 `NO` 헤더 행부터 읽었습니다. 금액 단위는 원자료 컬럼명 기준 `만원`입니다.
- 실거래가 지역 단위: 원자료에 법정동코드가 없어 `시군구` 문자열의 마지막 동명을 `읍면동`으로 사용했습니다.
- Tableau용 `03_admin_dong_cost_proxy.csv`는 행정동명에서 숫자를 제거한 법정동 추정명으로 가격을 붙인 참고용 테이블입니다. 엄밀한 분석에는 법정동-행정동 매핑표가 필요합니다.
- 오피스텔 재고: 주택 통계 파일에 오피스텔 재고 컬럼이 없어 수요-공급 표의 오피스텔수/비율은 결측으로 남겼습니다.
- 매매 실거래 정제 건수: 14,459건
- 전월세 실거래 정제 건수: 56,761건

## Tableau CSV

- `output/tableau/01_admin_dong_demand.csv`: ADM_CD가 포함된 행정동 단위 수요/인구 테이블입니다.
- `output/tableau/02_legal_dong_cost_summary.csv`: 법정동 x 건축유형 단위 매매/전세/월세 요약입니다.
- `output/tableau/03_admin_dong_cost_proxy.csv`: 행정동 지도에 가격을 얹기 위한 추정 결합 테이블입니다.
- `output/tableau/04_gu_housing_stock_reference.csv`: 구 단위 주택 재고 wide table입니다.
- `output/tableau/05_gu_demand_and_stock_reference.csv`: 구 단위 수요와 주택 재고를 함께 본 reference table입니다.
- `output/tableau/transactions_sales_long.csv`, `transactions_rent_long.csv`: Tableau에서 직접 필터링할 수 있는 실거래 long table입니다.

## 추가로 있으면 좋은 데이터

1. 법정동-행정동 코드 매핑표: 가격 분석과 세대수/주택재고를 같은 공간 단위로 연결하는 데 필요합니다.
2. 행정동 또는 격자 단위 주택 재고: 현재 full stock은 구 단위라 생활권 세부 비교에는 해상도가 낮습니다.
3. 오피스텔 재고 데이터: 오피스텔 실거래가는 있으나 공급 재고와 직접 비교할 수 없습니다.
4. 법정동코드가 포함된 실거래 원자료: 문자열 동명보다 안정적인 join이 가능합니다.