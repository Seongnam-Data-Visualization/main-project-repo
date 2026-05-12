"""동별 소스 CSV → seongnam_master.csv."""

from pathlib import Path

import numpy as np
import pandas as pd

PROC = Path(__file__).resolve().parent.parent / "processed"
OUT_CSV = PROC / "seongnam_master.csv"

COL_IT_BIZ = "it_ratio(biz기준)"
COL_IT_CORP = "it_ratio(corp기준)"


def main() -> None:
    base = pd.read_csv(PROC / "seongnam_employment_final.csv", encoding="utf-8-sig")
    keep = [
        "gu_name",
        "dong_name",
        "total_workers",
        "regular_workers",
        "self_employed",
        "self_employed_ratio",
        "total_biz",
        "it_ratio",
    ]
    base = base[keep].rename(columns={"it_ratio": COL_IT_BIZ})

    corp = pd.read_csv(PROC / "seongnam_corp_by_dong.csv", encoding="utf-8-sig").rename(
        columns={"admi_nm": "dong_name", "it_ratio": COL_IT_CORP}
    )
    new = pd.read_csv(PROC / "seongnam_new_corp_by_dong.csv", encoding="utf-8-sig").rename(
        columns={"admi_nm": "dong_name", "ncr_crp_comp_cn": "new_corp"}
    )
    move = pd.read_csv(PROC / "seongnam_corp_move_by_dong.csv", encoding="utf-8-sig").rename(
        columns={"admi_nm": "dong_name"}
    )

    m = base.merge(corp, on="dong_name", how="left")
    m = m.merge(new, on="dong_name", how="left")
    m = m.merge(move, on="dong_name", how="left")

    for c in ("total_corp", "it_corp", "new_corp", "corp_in", "corp_out", "순유입"):
        m[c] = m[c].fillna(0)
    m["total_corp"] = m["total_corp"].astype(int)
    m["it_corp"] = m["it_corp"].astype(int)
    m["new_corp"] = m["new_corp"].astype(int)
    m["corp_in"] = m["corp_in"].astype(int)
    m["corp_out"] = m["corp_out"].astype(int)
    m["순유입"] = m["순유입"].astype(int)

    tc = m["total_corp"].to_numpy(dtype=float)
    ic = m["it_corp"].to_numpy(dtype=float)
    m[COL_IT_CORP] = np.where(tc > 0, ic / tc, 0.0)

    ordered = [
        "gu_name",
        "dong_name",
        "total_workers",
        "regular_workers",
        "self_employed",
        "self_employed_ratio",
        "total_biz",
        COL_IT_BIZ,
        "total_corp",
        "it_corp",
        COL_IT_CORP,
        "new_corp",
        "corp_in",
        "corp_out",
        "순유입",
    ]
    m = m[ordered]

    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    m.to_csv(OUT_CSV, index=False, encoding="utf-8-sig")

    print(f"저장: {OUT_CSV}")
    print(f"행 수: {len(m)}")
    print("\n컬럼 목록:")
    print(list(m.columns))
    print("\n샘플 5행:")
    with pd.option_context("display.max_columns", None, "display.width", 200):
        print(m.head(5).to_string(index=False))


if __name__ == "__main__":
    main()
