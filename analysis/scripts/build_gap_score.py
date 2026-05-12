"""seongnam_total_master.csv → GAP/정규화/통합 점수/K-means/유형 라벨 → seongnam_scored.csv."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[2]
INPUT_CSV = REPO_ROOT / "analysis/data/seongnam_total_master.csv"
OUT_DIR = REPO_ROOT / "analysis/data"
OUT_CSV = OUT_DIR / "seongnam_scored.csv"


def min_max_series(s: pd.Series) -> pd.Series:
    lo, hi = float(s.min()), float(s.max())
    if not np.isfinite(lo) or not np.isfinite(hi) or hi == lo:
        return pd.Series(0.5, index=s.index, dtype=float)
    return ((s.astype(float) - lo) / (hi - lo)).clip(0.0, 1.0)


def kmeans_labels(X: np.ndarray, k: int, random_state: int = 42, max_iter: int = 300) -> np.ndarray:
    """Lloyd K-means, reproducible init (random data points). sklearn 미사용."""
    rng = np.random.RandomState(random_state)
    n = X.shape[0]
    ind = rng.choice(n, size=k, replace=False)
    centroids = X[ind].astype(float).copy()
    labels = np.zeros(n, dtype=int)
    for _ in range(max_iter):
        dist_sq = ((X[:, None, :] - centroids[None, :, :]) ** 2).sum(axis=2)
        new_labels = dist_sq.argmin(axis=1)
        if np.array_equal(new_labels, labels) and _ > 0:
            break
        labels = new_labels
        for j in range(k):
            mask = labels == j
            if np.any(mask):
                centroids[j] = X[mask].mean(axis=0)
    return labels


def main() -> None:
    if not INPUT_CSV.is_file():
        raise FileNotFoundError(f"Missing input: {INPUT_CSV}")

    df = pd.read_csv(INPUT_CSV, encoding="utf-8-sig")

    # STEP 1
    pop = df["생산가능인구_19_64세"].astype(float)
    workers = df["total_workers"].astype(float)
    df["supply_gap"] = np.where(pop > 0, workers / pop, np.nan)
    df["commute_gap"] = df["axis_commute_share"].astype(float) + df["seoul_commute_share"].astype(float)

    # STEP 2 — supply: 일자리/인구 비율이 높을수록 양호 → minmax 후 (1-x)로 “높을수록 취약”에 맞춤
    #         commute: 외부 통근 비중이 높을수록 취약 → minmax만 (높을수록 취약 유지)
    #         (문서에 commute도 (1-x)가 있으나, 그렇게 하면 STEP3 가중과 방향이 충돌해 commute는 뒤집지 않음)
    #         accessibility: minmax만 저장, STEP3에서 (1 - accessibility_norm)으로 반영
    mm_supply = min_max_series(df["supply_gap"].fillna(df["supply_gap"].median()))
    df["supply_gap_norm"] = 1.0 - mm_supply

    df["accessibility_norm"] = min_max_series(df["accessibility_score"].fillna(df["accessibility_score"].median()))
    df["commute_gap_norm"] = min_max_series(df["commute_gap"].fillna(df["commute_gap"].median()))

    # STEP 3 (높을수록 취약)
    df["integrated_score"] = (
        df["supply_gap_norm"] * 0.4
        + (1.0 - df["accessibility_norm"]) * 0.3
        + df["commute_gap_norm"] * 0.3
    )

    # STEP 4 — K-means (k=4, random_state=42)
    feat = df[["supply_gap_norm", "accessibility_norm", "commute_gap_norm"]].to_numpy(dtype=float)
    df["cluster"] = kmeans_labels(feat, k=4, random_state=42).astype(int)

    print("클러스터별 평균 (supply_gap_norm, accessibility_norm, commute_gap_norm):")
    grp = df.groupby("cluster", sort=True)[["supply_gap_norm", "accessibility_norm", "commute_gap_norm"]].mean()
    print(grp.to_string(float_format=lambda x: f"{x:.4f}"))
    print()

    med_s = df["supply_gap_norm"].median()
    med_a = df["accessibility_norm"].median()
    med_c = df["commute_gap_norm"].median()

    def type_label_row(row: pd.Series) -> str:
        s, a, c = row["supply_gap_norm"], row["accessibility_norm"], row["commute_gap_norm"]
        if s < med_s and a > med_a and c < med_c:
            return "Type A (자족형)"
        if s >= med_s and c >= med_c:
            return "Type B (직주분리형)"
        if a <= med_a:
            return "Type C (접근성 불량형)"
        return "Type D (복합 취약형)"

    df["type_label"] = df.apply(type_label_row, axis=1)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT_CSV, index=False, encoding="utf-8-sig")

    print(f"저장: {OUT_CSV} (행 수: {len(df)})")
    print()

    print("타입별 동 목록:")
    for t in sorted(df["type_label"].unique()):
        sub = df.loc[df["type_label"] == t, ["gu_name", "dong_name"]]
        names = [f"{r.gu_name} {r.dong_name}" for r in sub.itertuples(index=False)]
        print(f"  [{t}] ({len(names)}개)")
        for n in names:
            print(f"    - {n}")
    print()

    top5 = df.nlargest(5, "integrated_score")[["gu_name", "dong_name", "integrated_score"]]
    print("통합 Score 상위 5 (가장 취약):")
    print(top5.to_string(index=False, float_format=lambda x: f"{x:.4f}"))


if __name__ == "__main__":
    main()
