# Transport Notes

## Purpose

이 분석은 성남시 행정동별 통근 접근성을 비교하고, 수요가 높지만 접근성이 낮은 지역을 찾기 위한 것이다. 주거, 업무 분석과 연결할 때는 다음 두 질문에 답하는 보조 축으로 쓰면 된다.

- 주거 수요가 큰데 통근 접근성이 낮은 곳은 어디인가
- 고용 집적과 통근 연결이 함께 높은 곳은 어디인가

## Master Files

- `data/processed/seongnam_transport_master.csv`
- `data/processed/seongnam_transport_master_by_year.csv`

기본 조인 키는 `gu_name`, `dong_name`, 보조 키는 `admi_cd`다.

## Filters

- 평일만 사용
- 오전 6시~9시만 사용
- `PURPOSE == 1`인 통근 목적 이동만 사용

이 필터를 명확히 적어두면 다른 폴더와 비교할 때 분석 단위가 흔들리지 않는다.

## Score Design

`accessibility_score`는 아래 네 요소를 표준화한 뒤 가중합했다.

- `subway_share` 0.45
- `axis_commute_share` 0.25
- `seoul_commute_share` 0.20
- `bus_share` -0.10

가중치는 정책적 판단이 섞인 실무형 설계다. 지하철 기반 접근성과 주요 업무축 연결을 가장 크게 보고, 서울 연계를 보조 지표로 반영했다. 버스 비중은 접근성의 대체 수단일 수 있지만 철도 기반 연결보다 제약이 크다고 보고 약한 음수 가중치를 두었다.

## Recommended Interpretation

- `accessibility_score` 상위: 철도 기반 접근성과 외부 연결성이 강한 동
- `vulnerability_score` 상위: 상대적으로 통근 취약한 동
- `high_demand_low_access` 상위: 통근 수요가 크지만 개선 필요성이 큰 동

## Presentation Tips

- 주거 파트와 연결할 때: 세대수, 생산가능인구가 큰데 `high_demand_low_access`가 높은 지역을 우선 제시
- 업무 파트와 연결할 때: `axis_commute_share`, `seoul_commute_share`가 높은 지역과 고용 밀집 지역을 같이 비교
- 점수는 순위와 구간 비교 중심으로 설명하고, 절대값 자체를 과도하게 해석하지 않기
