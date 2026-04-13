import pandas as pd

import pandas as pd
import matplotlib.pyplot as plt
import os

# =========================
# Configs
# =========================
INPUT_PATH = r"C:\Users\rdh08\Desktop\2026_Data_Visualization\Dataset\경기도 성남시_저소득_한부모가족_현황_20250531.csv"
OUTPUT_DIR = "./results/outputs_low_income_single_parent"

os.makedirs(OUTPUT_DIR, exist_ok=True)

plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False


# =========================
# Loading & Processing
# =========================
def load_data(path):
    df = pd.read_csv(path, encoding="euc-kr")
    df.columns = df.columns.str.replace(" ", "")

    return df


def aggregate_total(df):
    numeric_cols = df.select_dtypes(include='number').columns
    return df[numeric_cols].sum()


def make_family_type(total_series):
    return pd.Series({
        "모자가족": total_series["모자가족_세대수"],
        "부자가족": total_series["부자가족_세대수"]
    })


def make_family_members(total_series):
    return pd.Series({
        "모자가족": total_series["모자가족_가구원수"],
        "부자가족": total_series["부자가족_가구원수"]
    })


def make_avg_household_size(total_series):
    return pd.Series({
        "전체": total_series["한부모가족_가구원수"] / total_series["한부모가족_세대수"],
        "모자가족": total_series["모자가족_가구원수"] / total_series["모자가족_세대수"],
        "부자가족": total_series["부자가족_가구원수"] / total_series["부자가족_세대수"]
    })


# =========================
# Plot
# =========================
def plot_total_households(total_series):
    value = total_series["한부모가족_세대수"]

    plt.figure()
    plt.bar(["한부모가족"], [value], color="#4C72B0")

    plt.title("저소득 한부모가족 세대수 (전체)")
    plt.ylabel("세대수")

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "total_households.png"))
    plt.close()


def plot_family_type(family_series):
    plt.figure()
    plt.bar(family_series.index, family_series.values, color=["#4C72B0", "#DD8452"])

    plt.title("모자가족 vs 부자가족 (세대수)")
    plt.ylabel("세대수")

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "family_type.png"))
    plt.close()


def plot_family_members(members_series):
    plt.figure()
    plt.bar(members_series.index, members_series.values, color=["#4C72B0", "#DD8452"])

    plt.title("모자가족 vs 부자가족 (가구원수)")
    plt.ylabel("가구원수")

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "family_members.png"))
    plt.close()


def plot_avg_household(avg_series):
    plt.figure()
    plt.bar(avg_series.index, avg_series.values)

    plt.title("평균 가구 규모")
    plt.ylabel("평균 인원")

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "avg_household_size.png"))
    plt.close()


# =========================
# 구별 / 동별
# =========================
def plot_by_gu(df):
    grouped = df.groupby("구별").sum(numeric_only=True)

    plt.figure()
    grouped["한부모가족_세대수"].plot(kind='bar')

    plt.title("구별 한부모가족 세대수")
    plt.ylabel("세대수")

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "gu_total.png"))
    plt.close()


def plot_by_gu_stacked(df):
    grouped = df.groupby("구별").sum(numeric_only=True)

    x = range(len(grouped))

    plt.figure()
    plt.bar(x, grouped["모자가족_세대수"], label="모자", color="#4C72B0")
    plt.bar(x, grouped["부자가족_세대수"],
            bottom=grouped["모자가족_세대수"],
            label="부자",
            color="#DD8452")

    plt.xticks(x, grouped.index)
    plt.title("구별 모자/부자 구조")
    plt.ylabel("세대수")
    plt.legend()

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "gu_stacked.png"))
    plt.close()

def plot_avg_household_by_gu(df):
    grouped = df.groupby("구별").sum(numeric_only=True)

    avg = grouped["한부모가족_가구원수"] / grouped["한부모가족_세대수"]

    plt.figure()
    avg.plot(kind='bar')

    plt.title("구별 평균 가구 규모")
    plt.ylabel("평균 인원")

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "avg_household_gu.png"))
    plt.close()

def plot_by_dong(df):
    grouped = df.groupby("동별")["한부모가족_세대수"].sum().sort_values()

    plt.figure(figsize=(8, 12))
    grouped.plot(kind='barh')

    plt.title("동별 한부모가족 세대수")
    plt.xlabel("세대수")

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "dong_total.png"))
    plt.close()

def plot_avg_household_by_dong(df):
    grouped = df.groupby("동별").sum(numeric_only=True)

    avg = grouped["한부모가족_가구원수"] / grouped["한부모가족_세대수"]
    avg = avg.sort_values()

    plt.figure(figsize=(8, 12))
    avg.plot(kind='barh')

    plt.title("동별 평균 가구 규모")
    plt.xlabel("평균 인원")

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "avg_household_dong.png"))
    plt.close()

def plot_top_dong(df, top_n=10):
    grouped = df.groupby("동별")["한부모가족_세대수"].sum().sort_values(ascending=False).head(top_n)

    plt.figure()
    grouped.plot(kind='bar')

    plt.title(f"한부모가족 상위 {top_n}개 동")
    plt.ylabel("세대수")

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "dong_top.png"))
    plt.close()

def plot_avg_household_distribution(df):
    grouped = df.groupby("동별").sum(numeric_only=True)

    avg = grouped["한부모가족_가구원수"] / grouped["한부모가족_세대수"]

    plt.figure()
    plt.hist(avg, bins=10)

    plt.title("평균 가구 규모 분포")
    plt.xlabel("평균 인원")

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "avg_household_dist.png"))
    plt.close()

# =========================
# 4. Main
# =========================
def main():
    df = load_data(INPUT_PATH)

    total = aggregate_total(df)

    family_series = make_family_type(total)
    members_series = make_family_members(total)
    avg_series = make_avg_household_size(total)

    plot_total_households(total)
    plot_family_type(family_series)
    plot_family_members(members_series)
    plot_avg_household(avg_series)

    plot_by_gu(df)
    plot_by_gu_stacked(df)
    plot_avg_household_by_gu(df)
    plot_by_dong(df)
    plot_top_dong(df)
    plot_avg_household_by_dong(df)
    plot_avg_household_distribution(df)

    print("Saved:", OUTPUT_DIR)


if __name__ == "__main__":
    main()