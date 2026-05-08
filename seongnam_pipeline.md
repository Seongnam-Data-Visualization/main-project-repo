# 성남시 체감 생활권 분석 파이프라인

> **메인 주장** : 성남시의 현재 생활권 개편 방향은 optimal하지 않다  
> 체감 이동 경계 ≠ 행정 생활권 경계 → Type B·C·D 밀집 권역에 우선 개선 필요

---

## 목차

1. [분석 개요](#분석-개요)
2. [데이터 수집 구조](#데이터-수집-구조)
3. [분석 3단계](#분석-3단계)
4. [통합 Score 산출](#통합-score-산출)
5. [시각화 플랜](#시각화-플랜)
6. [지역 유형 분류](#지역-유형-분류)
7. [최종 주장 도출 흐름](#최종-주장-도출-흐름)

---

## 분석 개요

```mermaid
flowchart TD
    PROB["Pain Point\n신도시(분당·판교·위례) vs 구시가지(수정·중원) 격차 심화"]
    GOAL["분석 목표\n계획 생활권 vs 체감 생활권의 괴리 정량화"]
    CLAIM["메인 주장\n현재 생활권 개편 방향은 optimal하지 않다"]

    PROB --> GOAL --> CLAIM
```

---

## 데이터 수집 구조

세 개의 독립 테이블을 **행정동 코드(법정동 코드)** 기준으로 JOIN하는 구조.

```mermaid
flowchart LR
    subgraph D["수요 데이터 (KOSIS / 행안부)"]
        D1["행정동별 인구\n고령인구 비율\n아동인구 비율\n1인가구 비율"]
        D2["기초생활수급자\n장애인 등록\n다문화가정\n돌봄 수요"]
    end

    subgraph S["공급 데이터 (data.go.kr / HIRA)"]
        S1["복지시설\n(노인·장애인·아동)"]
        S2["의료기관"]
        S3["공원·문화·체육시설\n어린이집·유치원"]
    end

    subgraph A["접근성 데이터 (TAGO / 국토정보플랫폼)"]
        A1["버스 정류장 위치\n노선·승하차 OD"]
        A2["지하철 역사 위치\n승하차 통계"]
        A3["보행로·자전거도로\nGIS shapefile"]
    end

    subgraph B["보조(행동) 데이터 ★ 차별화 포인트"]
        B1["카드 관외소비\n(BC·신한 빅데이터캠퍼스)"]
        B2["유동인구\n(SKT 지오비전 / KT)"]
        B3["통계청 생활이동 OD\n(2019~)"]
        B4["부동산 실거래가\n(국토부)"]
    end

    JOIN[("행정동 코드\nJOIN KEY")]

    D --> JOIN
    S --> JOIN
    A --> JOIN
    B --> JOIN
```

---

## 분석 3단계

```mermaid
flowchart TD
    subgraph STEP1["1단계 : 수요-공급 불균형 파악"]
        direction LR
        S1_IN["수요 데이터\n+ 공급 데이터"]
        S1_CALC["행정동별 집계\n- 고령인구 1천명당 노인시설 수\n- 장애인 등록 대비 장애인복지시설 수\n- 아동인구 대비 어린이집 정원 수"]
        S1_OUT(["공급 GAP Score\n(행정동 단위)"])
        S1_IN --> S1_CALC --> S1_OUT
    end

    subgraph STEP2["2단계 : 실질 접근성 분석"]
        direction LR
        S2_IN["접근성 데이터\n+ 공급 데이터"]
        S2_CALC["도달 가능성 분석\n- 복지시설 반경 300m 내 정류장 밀도\n- 정류장 간 평균 환승 횟수\n- inter 생활권 이동 편의성\n  vs intra 생활권 이동 편의성"]
        S2_OUT(["접근성 Score\n(행정동 단위)"])
        S2_IN --> S2_CALC --> S2_OUT
    end

    subgraph STEP3["3단계 : 체감 생활권 도출"]
        direction LR
        S3_IN["보조(행동) 데이터\n(카드 OD + 생활이동 OD)"]
        S3_CALC["행정 생활권과 비교\n- 카드 소비의 관외 비율 (동별)\n- 실제 이동 목적지 분포\n- 체감 생활권 경계 역산"]
        S3_OUT(["체감이동 GAP Score\n(행정동 단위)"])
        S3_IN --> S3_CALC --> S3_OUT
    end

    STEP1 --> STEP2 --> STEP3
```

---

## 통합 Score 산출

```mermaid
flowchart TD
    G1(["공급 GAP Score"])
    G2(["접근성 Score"])
    G3(["체감이동 GAP Score"])

    FORMULA[**어떤 공식으로 score 책정할지 의논해 봐야할듯**]

    RESULT(["행정동별 종합 취약 Score"])

    G1 --> FORMULA
    G2 --> FORMULA
    G3 --> FORMULA
    FORMULA --> RESULT
```

> **가중치 권고** : PCA로 1차 산출 후 선행연구와 비교·보정하는 방식 권장.  
> 공모전 심사 설명을 위해 가중치 근거 문서화 필수.

---

## 시각화 플랜

각 시각화가 답해야 하는 질문을 기준으로 설계.

```mermaid
flowchart LR
    SCORE(["종합 Score\n(행정동 단위)"])

    subgraph VIZ["시각화 4종"]
        V1["① 단변량 분포\n히스토그램 / Box plot\n\n답할 질문\n- 고령인구는 어디 몰려있나?\n- 시설 수 분포의 Skewness는?"]
        V2["② 공간 분포\nChoropleth 지도\n(다변량)\n\n답할 질문\n- 취약 지역은 어디인가?\n- 시설과 수요의 공간적 미스매치?"]
        V3["③ 변수 관계\nScatter plot\nCorrelation Heatmap\n\n답할 질문\n- 접근성은 어떤 변수와 움직이나?\n- 인과 방향은?"]
        V4["④ 지역 유형화\nK-means Clustering\n\n답할 질문\n- 비슷한 동네끼리 묶으면?\n- 유형이 생활권 경계와 어긋나는가?"]
    end

    SCORE --> V1
    SCORE --> V2
    SCORE --> V3
    SCORE --> V4
```

---

## 지역 유형 분류

클러스터링 결과를 아래 4개 유형으로 프레이밍.

```mermaid
flowchart TD
    CLUSTER["K-means Clustering 결과"]

    TA["Type A : 자족형\n수요 ↔ 공급 균형\n타 생활권 이동 낮음\n예상 : 분당·판교 일부"]
    TB["Type B : 외부의존형\n공급 부족 → 타 생활권 소비·이동 ↑\n카드 관외소비 비율 높음\n예상 : 위례·수정구 일부"]
    TC["Type C : 접근성 불량형\n시설은 있으나 연결 안됨\n버스 커버리지 낮음\n예상 : 중원구 구시가지"]
    TD["Type D : 복합 취약형\n수요↑ 공급↓ 접근성↓\n가장 우선 개선 필요\n예상 : 수정구 북부"]

    CLUSTER --> TA
    CLUSTER --> TB
    CLUSTER --> TC
    CLUSTER --> TD
```

| 유형 | 수요 | 공급 | 접근성 | 체감이동 | 우선순위 |
|------|------|------|--------|----------|----------|
| Type A 자족형 | 보통 | 충분 | 양호 | 내부순환 | 낮음 |
| Type B 외부의존형 | 높음 | 부족 | 보통 | 외부유출↑ | 중간 |
| Type C 접근성 불량형 | 보통 | 보통 | 불량 | 이동 포기 | 중간 |
| Type D 복합 취약형 | 높음 | 부족 | 불량 | 외부유출↑ | **최우선** |

---

## 최종 주장 도출 흐름

```mermaid
flowchart TD
    A["데이터 수집\n수요 + 공급 + 접근성 + 행동"]
    B["3단계 분석\n공급GAP / 접근성GAP / 체감이동GAP"]
    C["통합 Score 산출\n행정동 단위 취약도 지표화"]
    D["시각화\n분포·지도·상관·클러스터링"]
    E["지역 4유형 분류\nType A / B / C / D"]

    F{"Type B·C·D\n밀집 권역이\n어디인가?"}

    G["현재 개편안 검토\n북부/중부/남부 재구성이\n해당 권역을 포괄하는가?"]

    H["주장 도출\n현재 생활권 개편 방향은\noptimal하지 않다\n\n→ 연결 보완이 필요한 구체적 권역과\n   개선 유형을 제안"]

    A --> B --> C --> D --> E --> F --> G --> H
```

---

## 데이터 수집 분담 체크리스트

| 팀원 | 담당 영역 | 주요 출처 | 완료 |
|------|-----------|-----------|------|
| A | 인구·복지 수요 | KOSIS, 행안부, 복지부 | ☐ |
| B | 교통 (대중교통) | TAGO, GBIS, data.go.kr | ☐ |
| C | 생활인프라·시설 공급 | data.go.kr, HIRA, 세움터 | ☐ |
| D | 보조(행동) 데이터 | 빅데이터캠퍼스, 통계청, 국토부 | ☐ |

> 각자 **5개 데이터셋** 확보 후 행정동 코드 기준 JOIN 가능 여부 확인 필수.

---

*최종 업데이트 : 2026-05*
