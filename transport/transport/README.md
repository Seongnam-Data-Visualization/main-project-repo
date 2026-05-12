# Transport Analysis

성남시 생활권 프로젝트의 교통 분석 폴더다. 통근 목적 이동 데이터를 기준으로 행정동별 접근성, 서울 연계성, 수요 대비 취약 지역을 정리한다.

## Analysis Question

- 어느 동이 출근 통행 접근성이 높은가
- 어느 동이 통근 수요는 큰데 교통 접근성은 상대적으로 약한가
- 어느 동이 서울 및 주요 업무축과 강하게 연결되는가

## Scope

- 공간 단위: 성남시 행정동
- 시간 필터: 평일 오전 6시~9시
- 목적 필터: 통근 목적 이동만 사용
- 원천 데이터:
  - `T27`: 출발 행정동 기준 통행량, 교통수단, 체류시간
  - `T13`: 출발-도착 OD 기준 통근량

## Structure

```text
transport/
+-- data/
|   +-- raw/                  # 원본 ZIP/CSV, git 제외
|   +-- processed/
|   |   +-- clean/           # 기준 마스터 CSV
|   |   +-- tables/          # 발표용 요약표
|   |   +-- tableau/         # 시각화 연결용 CSV
|   |   +-- figures/         # 기본 그래프
|   |   +-- seongnam_transport_master.csv
|   |   +-- seongnam_transport_master_by_year.csv
|   +-- reference/           # 보조 매핑 테이블
|   +-- scripts/             # 전처리/집계 스크립트
+-- notebooks/               # 추가 탐색, Tableau 연계 메모
+-- memo/                    # 지표 정의 및 해석 메모
```

## Run

```powershell
python transport\data\scripts\build_transport_master.py
```

원본 파일은 아래 두 경로 중 하나에 있으면 된다.

- `transport/data/raw/T13`, `transport/data/raw/T27`
- `data/raw/T13`, `data/raw/T27` (fallback)

## Main Outputs

- `data/processed/seongnam_transport_master.csv`
  - 전체 연도 통합 기준 행정동 마스터
- `data/processed/seongnam_transport_master_by_year.csv`
  - 연도별 행정동 마스터
- `data/processed/tables/transport_priority_summary.csv`
  - 수요 대비 취약 지역 우선순위 표
- `data/processed/tables/gu_transport_summary.csv`
  - 구 단위 요약표
- `data/processed/tables/yearly_transport_summary.csv`
  - 연도별 추이 요약표

조인 키는 기본적으로 `gu_name`, `dong_name`을 쓰고, 보조 키로 `admi_cd`를 사용한다.

## Metric Notes

- `total_commute`: 평일 오전 출근 통행 총량
- `subway_share`, `bus_share`, `car_share`, `other_share`: 교통수단 비중
- `avg_stay_duration`: 통행량 가중 평균 체류시간
- `short_stay_share`: 60분 이하 체류 비중
- `axis_commute_share`: 주요 업무축으로 향하는 통근 비중
- `seoul_commute_share`: 서울행 통근 비중
- `accessibility_score`: 지하철 비중, 업무축 연계, 서울 연계를 합산한 접근성 지표
- `high_demand_low_access`: 통근 수요는 크지만 접근성은 약한 지역을 찾는 우선순위 지표

## Interpretation

`accessibility_score`는 절대 점수가 아니라 성남시 내부 상대 비교용 점수다. 값이 높을수록 대중교통 기반 접근성과 외부 연결성이 상대적으로 좋고, 값이 낮을수록 통근 취약도가 높다고 해석한다.
