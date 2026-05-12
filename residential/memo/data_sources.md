# Residential Data Sources

이 문서는 `residential/data/raw/Dataset_v1`에 저장한 원자료를 기준으로, 어떤 데이터를 어디서 내려받았는지 정리한 것입니다. `residential/data/processed` 아래 파일들은 아래 원자료를 `residential/data/scripts/residential_pipeline.py`로 정제/집계한 2차 산출물입니다.

## 원자료 출처

| 데이터 | 원본 파일/폴더 | 출처 | 수집/필터 조건 | 비고 |
|---|---|---|---|---|
| 주택 실거래가 | `아파트(매매)_실거래가_20260512004606_분당구.csv` 등 `*_실거래가_*.csv` 24개 | 국토교통부 실거래가 공개시스템<br>https://rt.molit.go.kr/pt/xls/xls.do?mobileAt= | 기간: 2025.5.13-2026.5.12<br>지역: 성남시 분당구/수정구/중원구<br>주거유형: 아파트, 연립다세대, 단독다가구, 오피스텔<br>거래유형: 매매, 전월세 | 파일명에 다운로드 시각과 구 단위가 포함되어 있음 |
| 인구/세대 현황 | `2026.3 인구현황(1인세대수 현황 포함).xlsx` | 성남시 통계 게시판<br>https://www.seongnam.go.kr/stat/1001720/30387/bbsView.do?currentPage=1&searchSelect=&searchWord=&searchOrganDeptCd=&searchCategory=&idx=382546&post_size=10 | 2026년 3월 기준 인구현황 및 1인세대수 포함 자료 | 행정동별 인구, 19세 이상, 65세 이상, 세대수 추출에 사용 |
| 공동주택 현황 | `경기도 성남시_공동주택현황_20250705.csv` | 공공데이터포털<br>https://www.data.go.kr/data/15000796/fileData.do | 경기도 성남시 공동주택 현황 | 구/동, 단지명, 주소, 층수, 동수, 세대수 등 |
| 주택 통계 | `경기도 성남시_주택_통계_20250618.csv` | 공공데이터포털<br>https://www.data.go.kr/data/15032480/fileData.do | 경기도 성남시 주택 통계 | 구 단위 주택 유형별 물량 참고 자료 |
| 주택보급률 현황 | `경기도 성남시_주택보급률현황_20250630.csv` | 공공데이터포털<br>https://www.data.go.kr/data/15032484/fileData.do | 경기도 성남시 주택보급률 현황 | 구분, 주택수, 가구수, 보급률 |
| 행정동별 인구분포 | `행정동별 인구분포.csv` | 성남 데이터 포털 통계 대시보드<br>https://data.seongnam.go.kr/portal/statDash/populationStatus.do | 행정동별 인구분포 CSV 다운로드 | 행정동 단위 수요 지표 보조 자료 |
| 연령별 인구현황 | `연령별 인구현황.csv` | 성남 데이터 포털 통계 대시보드<br>https://data.seongnam.go.kr/portal/statDash/populationStatus.do | 연령별 인구현황 CSV 다운로드 | 연령 구조 확인용 보조 자료 |
| 센서스 행정동 경계 | `BND_ADM_DONG_PG/` | 브이월드 데이터마켓<br>https://www.vworld.kr/dtmk/dtmk_ntads_s002.do?searchKeyword=%ED%96%89%EC%A0%95%EB%8F%99&searchSvcCde=&searchOrganization=&searchBrmCode=&searchTagList=&searchFrm=&pageIndex=1&gidmCd=&gidsCd=&sortType=00&svcCde=MK&dsId=30017&listPageIndex=1 | 센서스 행정동 경계 데이터 다운로드 | `.shp`, `.dbf`, `.shx`, `.prj`, `.cpg` 포함 |

## 실거래가 원자료 목록

국토교통부 실거래가 공개시스템에서 같은 기간(2025.5.13-2026.5.12)으로 내려받은 파일입니다.

| 주거유형 | 거래유형 | 대상 구 | 파일 수 |
|---|---|---:|---:|
| 아파트 | 매매 | 분당구, 수정구, 중원구 | 3 |
| 아파트 | 전월세 | 분당구, 수정구, 중원구 | 3 |
| 연립다세대 | 매매 | 분당구, 수정구, 중원구 | 3 |
| 연립다세대 | 전월세 | 분당구, 수정구, 중원구 | 3 |
| 단독다가구 | 매매 | 분당구, 수정구, 중원구 | 3 |
| 단독다가구 | 전월세 | 분당구, 수정구, 중원구 | 3 |
| 오피스텔 | 매매 | 분당구, 수정구, 중원구 | 3 |
| 오피스텔 | 전월세 | 분당구, 수정구, 중원구 | 3 |

## 직접 생성한 파일

| 파일 | 설명 | 출처 표기 |
|---|---|---|
| `seongnam_dong.geojson` | `BND_ADM_DONG_PG` 센서스 행정동 경계 데이터에서 성남시 행정동만 추출해 만든 GeoJSON | 별도 외부 출처 없음. 원 경계 데이터 출처는 브이월드 |

## 파생 산출물

아래 파일들은 외부에서 직접 받은 데이터가 아니라, 위 원자료를 가공해 생성한 결과물입니다.

- `residential/data/processed/clean/*.csv`
- `residential/data/processed/tables/*.csv`
- `residential/data/processed/tableau/*.csv`
- `residential/data/processed/figures/*.png`