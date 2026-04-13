import pandas as pd
import matplotlib.pyplot as plt
import os

# =========================
# Configs
# =========================
INPUT_PATH = r"C:\Users\rdh08\Desktop\2026_Data_Visualization\Dataset\경기도 성남시_1인세대_현황_20250430.csv"
OUTPUT_DIR = "./results/outputs_single_household"

os.makedirs(OUTPUT_DIR, exist_ok=True)

plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False


# =========================
# Data Loading & Processing
# =========================
def load_data(path):
    df = pd.read_csv(path)
    return df


def aggregate_total(df):
    """전체 합 (성남시 전체 기준)"""
    numeric_cols = df.select_dtypes(include='number').columns
    return df[numeric_cols].sum()


def make_age_groups(total_series):
    """연령대 재구성 (성별 합쳐진 계 기준)"""

    age_groups = {
        "10대": ["10세-14세(계)", "15세-19세(계)"],
        "20대": ["20세-24세(계)", "25세-29세(계)"],
        "30대": ["30세-34세(계)", "35세-39세(계)"],
        "40대": ["40세-44세(계)", "45세-49세(계)"],
        "50대": ["50세-54세(계)", "55세-59세(계)"],
        "60대": ["60세-64세(계)"],
        "65세+": ["65세 이상(계)"]
    }

    result = {}
    for k, cols in age_groups.items():
        result[k] = sum([total_series[c] for c in cols if c in total_series])

    return pd.Series(result)


def make_age_gender_groups(total_series):
    """연령대 × 성별"""

    age_groups = {
        "10대": [("10세-14세(남)", "10세-14세(여)"),
               ("15세-19세(남)", "15세-19세(여)")],
        "20대": [("20세-24세(남)", "20세-24세(여)"),
               ("25세-29세(남)", "25세-29세(여)")],
        "30대": [("30세-34세(남)", "30세-34세(여)"),
               ("35세-39세(남)", "35세-39세(여)")],
        "40대": [("40세-44세(남)", "40세-44세(여)"),
               ("45세-49세(남)", "45세-49세(여)")],
        "50대": [("50세-54세(남)", "50세-54세(여)"),
               ("55세-59세(남)", "55세-59세(여)")],
        "60대": [("60세-64세(남)", "60세-64세(여)")],
        "65세+": [("65세 이상(남)", "65세 이상(여)")]
    }

    male = {}
    female = {}

    for age, pairs in age_groups.items():
        m_sum, f_sum = 0, 0
        for m_col, f_col in pairs:
            if m_col in total_series:
                m_sum += total_series[m_col]
            if f_col in total_series:
                f_sum += total_series[f_col]

        male[age] = m_sum
        female[age] = f_sum

    return pd.Series(male), pd.Series(female)


def make_lifecycle_groups(total_series):
    """생애주기 그룹"""

    lifecycle = {
        "미성년": ["0세-4세(계)", "5세-9세(계)", "10세-14세(계)", "15세-19세(계)"],
        "생산가능": [
            "20세-24세(계)", "25세-29세(계)", "30세-34세(계)", "35세-39세(계)",
            "40세-44세(계)", "45세-49세(계)", "50세-54세(계)", "55세-59세(계)",
            "60세-64세(계)"
        ],
        "노인": ["65세 이상(계)"]
    }

    result = {}
    for k, cols in lifecycle.items():
        result[k] = sum([total_series[c] for c in cols if c in total_series])

    return pd.Series(result)


def make_gender_total(total_series):
    return pd.Series({
        "남": total_series["1인세대수_남"],
        "여": total_series["1인세대수_여"]
    })


# =========================
# 3. Plot
# =========================
def plot_age_distribution(age_series):
    plt.figure()
    age_series.plot(kind='bar')
    plt.title("연령대별 1인가구 분포")
    plt.ylabel("가구 수")
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "age_distribution.png"))
    plt.close()


def plot_age_gender_stacked(male, female):
    plt.figure()

    x = range(len(male))

    plt.bar(x, male.values, label='남', color='#4C72B0')   # 파랑
    plt.bar(x, female.values, bottom=male.values, label='여', color='#DD8452')  # 주황

    plt.xticks(x, male.index)
    plt.title("연령대별 성별 1인가구 (Stacked)")
    plt.ylabel("가구 수")
    plt.legend()

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "age_gender_stacked.png"))
    plt.close()


def plot_lifecycle(lifecycle_series):
    plt.figure()
    lifecycle_series.plot(kind='bar')
    plt.title("생애주기별 1인가구")
    plt.ylabel("가구 수")
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "lifecycle.png"))
    plt.close()


def plot_lifecycle_ratio(lifecycle_series):
    ratio = lifecycle_series / lifecycle_series.sum()

    plt.figure()
    ratio.plot(kind='bar')
    plt.title("생애주기 비율 (100%)")
    plt.ylabel("비율")
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "lifecycle_ratio.png"))
    plt.close()


def plot_gender(gender_series):
    plt.figure()
    gender_series.plot(kind='bar')
    plt.title("성별 1인가구")
    plt.ylabel("가구 수")
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "gender.png"))
    plt.close()


def plot_age_gender_stacked(male, female):
    """연령대별 성별 1인가구 (Stacked Bar Chart)"""
    plt.figure()

    x = range(len(male))

    plt.bar(x, male.values, label='남', color='#4C72B0')   # 파랑
    plt.bar(x, female.values, bottom=male.values, label='여', color='#DD8452')  # 주황

    plt.xticks(x, male.index)
    plt.title("연령대별 성별 1인가구 (Stacked)")
    plt.ylabel("가구 수")
    plt.legend()

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "age_gender_stacked.png"))
    plt.close()


def plot_by_gu_age(df):
    """구별 연령대별 1인가구 분포"""
    grouped = df.groupby("구별").sum(numeric_only=True)

    results = []

    for gu, row in grouped.iterrows():
        age_series = make_age_groups(row)
        age_series.name = gu
        results.append(age_series)

    result_df = pd.DataFrame(results)

    result_df.plot(kind='bar')

    plt.title("구별 연령대별 1인가구 분포")
    plt.ylabel("가구 수")
    plt.xticks(rotation=0)

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "gu_age_distribution.png"))
    plt.close()


def plot_by_gu_lifecycle(df):
    """구별 생애주기별 1인가구"""
    grouped = df.groupby("구별").sum(numeric_only=True)

    results = []

    for gu, row in grouped.iterrows():
        lifecycle_series = make_lifecycle_groups(row)
        lifecycle_series.name = gu
        results.append(lifecycle_series)

    result_df = pd.DataFrame(results)

    result_df.plot(kind='bar')

    plt.title("구별 생애주기별 1인가구")
    plt.ylabel("가구 수")

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "gu_lifecycle.png"))
    plt.close()


def plot_by_dong_total(df):
    """동별 1인가구 수 (총합)"""
    grouped = df.groupby("동별")["1인세대수_계"].sum().sort_values()

    plt.figure(figsize=(8, 12))
    grouped.plot(kind='barh')

    plt.title("동별 1인가구 수")
    plt.xlabel("가구 수")

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "dong_total.png"))
    plt.close()

# =========================
# 4. Main
# =========================
def main():
    df = load_data(INPUT_PATH)

    total = aggregate_total(df)

    age_series = make_age_groups(total)
    male, female = make_age_gender_groups(total)
    lifecycle_series = make_lifecycle_groups(total)
    gender_series = make_gender_total(total)

    plot_age_distribution(age_series)
    plot_age_gender_stacked(male, female)
    plot_lifecycle(lifecycle_series)
    plot_lifecycle_ratio(lifecycle_series)
    plot_gender(gender_series)

    plot_by_gu_age(df)
    plot_by_gu_lifecycle(df)
    plot_by_dong_total(df)

    print("Saved:", OUTPUT_DIR)


if __name__ == "__main__":
    main()