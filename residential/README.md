# Residential Analysis

성남시 생활권 재정의 프로젝트의 주거 파트 작업 폴더입니다.

## Structure

```text
residential/
├── data/
│   ├── raw/                  # 원본 데이터, git 제외
│   ├── processed/
│   │   ├── clean/            # 정제 중간 산출물
│   │   ├── tables/           # 분석 요약 테이블
│   │   ├── tableau/          # Tableau 연결용 CSV
│   │   └── figures/          # 파이썬 확인용 그림
│   └── scripts/              # 전처리/집계 스크립트
├── notebooks/                # 분석 노트북
└── memo/                     # 메모와 데이터 주의사항
```

## Run

```powershell
python residential\data\scripts\residential_pipeline.py
```

`data/raw/Dataset_v1`에 원본 파일이 있어야 실행됩니다.
