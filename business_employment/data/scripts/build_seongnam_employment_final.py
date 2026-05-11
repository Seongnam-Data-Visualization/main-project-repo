"""workers + biz 동명 매핑 후 seongnam_employment_final.csv 생성."""

from pathlib import Path

import pandas as pd

WORKERS_CSV = Path(__file__).resolve().parent.parent / "processed" / "seongnam_workers_by_dong.csv"
BIZ_CSV = Path(__file__).resolve().parent.parent / "processed" / "seongnam_biz_by_dong.csv"
OUT_CSV = Path(__file__).resolve().parent.parent / "processed" / "seongnam_employment_final.csv"

# 통계 파일 `행정구역읍면동코드`는 구마다 같은 숫자가 다른 동을 가리킨다.
# 행안부 행정동 목록(kr-juso administrationCode.tsv)의 구·동 순서와,
# workers CSV에 나타난 코드 나열 순을 1:1로 대응시킨 매핑이다.
SEONGNAM_EMDONG_CODE_TO_DONG: dict[str, dict[int, str]] = {
    "수정구": {
        510: "신흥1동",
        520: "신흥2동",
        530: "신흥3동",
        540: "태평1동",
        550: "태평2동",
        560: "태평3동",
        570: "태평4동",
        580: "수진1동",
        590: "수진2동",
        600: "단대동",
        610: "산성동",
        620: "양지동",
        640: "복정동",
        650: "위례동",
        660: "신촌동",
        670: "고등동",
        680: "시흥동",
    },
    "중원구": {
        510: "성남동",
        530: "금광1동",
        540: "금광2동",
        550: "은행1동",
        560: "은행2동",
        570: "상대원1동",
        580: "상대원2동",
        590: "상대원3동",
        600: "하대원동",
        610: "도촌동",
        620: "중앙동",
    },
    "분당구": {
        510: "분당동",
        520: "수내1동",
        530: "수내2동",
        540: "수내3동",
        550: "정자동",
        560: "정자1동",
        580: "정자2동",
        590: "정자3동",
        600: "서현1동",
        610: "서현2동",
        620: "이매1동",
        630: "이매2동",
        640: "야탑1동",
        670: "야탑2동",
        680: "야탑3동",
        710: "판교동",
        720: "삼평동",
        740: "백현동",
        750: "금곡동",
        760: "구미1동",
        770: "구미동",
        780: "운중동",
    },
}


def main() -> None:
    workers = pd.read_csv(WORKERS_CSV, encoding="utf-8-sig")
    biz = pd.read_csv(BIZ_CSV, encoding="utf-8-sig")

    # 1
    codes = sorted(workers["행정구역읍면동코드"].dropna().unique().tolist())
    print(f"행 수: {len(workers)}")
    print(f"행정구역읍면동코드 고유값 전체 ({len(codes)}개): {codes}")

    # 2
    print("\ngu_name, dong_name (seongnam_biz_by_dong.csv):")
    print(biz[["gu_name", "dong_name"]].to_string(index=False))

    # 3–5
    def lookup_dong(row: pd.Series) -> str | float:
        gu = row["gu_name"]
        code = int(row["행정구역읍면동코드"])
        m = SEONGNAM_EMDONG_CODE_TO_DONG.get(gu, {})
        return m.get(code, pd.NA)

    workers = workers.copy()
    workers["dong_name"] = workers.apply(lookup_dong, axis=1)
    n_unmapped = workers["dong_name"].isna().sum()
    if n_unmapped:
        print(f"\n경고: dong_name 미매핑 행 {n_unmapped}건 (merge에서 제외됨)")

    merged = workers.merge(
        biz,
        on=["gu_name", "dong_name"],
        how="inner",
        suffixes=("_workers", "_biz"),
    )
    merged.to_csv(OUT_CSV, index=False, encoding="utf-8-sig")
    print(f"\n저장: {OUT_CSV} (행 수 {len(merged)})")


if __name__ == "__main__":
    main()
