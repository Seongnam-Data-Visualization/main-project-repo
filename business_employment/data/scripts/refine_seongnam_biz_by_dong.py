"""seongnam_biz_by_dong.csv 정제 후 동일 경로에 덮어쓰기."""

from pathlib import Path

import pandas as pd

CSV_PATH = Path(__file__).resolve().parent.parent / "processed" / "seongnam_biz_by_dong.csv"

BLOCKLIST = frozenset(
    {
        "분당구",
        "수정구",
        "중원구",
        "도촌",
        "상대원",
        "신흥",
        "하대원",
        "여수",
        "성남",
        "성남시",
        "성남점",
        "세종",
        "중동",
        "중앙빌딩)",
        "중앙지하상가",
        "아이에스센트럴타워",
        "우성메디피아",
        "당동",
        "상남동",
        "위예동",
    }
)


def _merge_by_dong(df: pd.DataFrame) -> pd.DataFrame:
    industry_cols = [c for c in df.columns if c not in ("gu_name", "dong_name", "total_biz", "it_ratio")]
    rows: list[dict] = []
    for dong, g in df.groupby("dong_name", sort=False):
        w = int(g["total_biz"].sum())
        it_num = float((g["it_ratio"].astype(float) * g["total_biz"].astype(float)).sum())
        gu = g["gu_name"].mode()
        gu_name = gu.iloc[0] if len(gu) else g["gu_name"].iloc[0]
        row: dict = {
            "dong_name": dong,
            "gu_name": gu_name,
            "total_biz": w,
            "it_ratio": (it_num / w) if w else 0.0,
        }
        for c in industry_cols:
            row[c] = int(g[c].sum())
        rows.append(row)
    out = pd.DataFrame(rows)
    return out[["gu_name", "dong_name", "total_biz", "it_ratio"] + industry_cols]


def main() -> None:
    df = pd.read_csv(CSV_PATH, encoding="utf-8-sig")
    n_before = len(df)

    df = df.copy()
    df.loc[df["dong_name"].astype(str) == "위예동", "dong_name"] = "위례동"
    df = _merge_by_dong(df)

    dong_s = df["dong_name"].astype(str)
    drop = (
        dong_s.str.fullmatch(r"\d+")
        | (df["total_biz"] == 1)
        | df["dong_name"].isin(BLOCKLIST)
    )
    df = df.loc[~drop].reset_index(drop=True)

    n_after = len(df)
    print(f"정제 전 행 수: {n_before}")
    print(f"정제 후 행 수: {n_after}")

    df.to_csv(CSV_PATH, index=False, encoding="utf-8-sig")


if __name__ == "__main__":
    main()
