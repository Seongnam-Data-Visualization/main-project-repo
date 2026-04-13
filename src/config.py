"""
Define file paths and load datasets.
"""

import pandas as pd

# Demand Datasets
path_population = r"C:\Users\rdh08\Desktop\2026_Data_Visualization\Dataset\경기도 성남시_인구및세대_현황_20260331 (1).csv"
df_population = pd.read_csv(path_population)

path_disability_population = r"C:\Users\rdh08\Desktop\2026_Data_Visualization\Dataset\경기도 성남시_장애인등록_현황_20250524.csv"
df_disability_population = pd.read_csv(path_disability_population)

path_low_income_population = r"C:\Users\rdh08\Desktop\2026_Data_Visualization\Dataset\경기도 성남시_저소득_한부모가족_현황_20250531.csv"
df_low_income_population = pd.read_csv(path_low_income_population, encoding="euc-kr")

path_single_person_household = r"C:\Users\rdh08\Desktop\2026_Data_Visualization\Dataset\경기도 성남시_1인세대_현황_20250430.csv"
df_single_person_household = pd.read_csv(path_single_person_household)

path_basement_living_beneficiaries = r"C:\Users\rdh08\Desktop\2026_Data_Visualization\Dataset\경기도 성남시_기초생활수급자_현황_20250912.csv"
df_basement_living_beneficiaries = pd.read_csv(path_basement_living_beneficiaries)

# Senior Facilities
# path_senior_medicare_center = r"C:\Users\rdh08\Desktop\2026_Data_Visualization\Dataset\경기도 성남시_노인_의료복지시설_현황_20250605.csv"
# df_senior_medicare_center = pd.read_csv(path_senior_medicare_center, encoding="utf-8-sig")

# path_senior_community_welfare_center = r"C:\Users\rdh08\Desktop\2026_Data_Visualization\Dataset\경기도 성남시_노인_종합복지관_현황_20250605.csv"
#  = pd.read_csv(path_senior_community_welfare_center, encoding="utf-8-sig")

# path_senior_residential_care_center = r"C:\Users\rdh08\Desktop\2026_Data_Visualization\Dataset\경기도 성남시_노인_주거복지시설_현황_20250605.csv"
# df_senior_residential_care_center = pd.read_csv(path_senior_residential_care_center, encoding="utf-8-sig")

# Disability Facilities
# path_disability_welfare_center = r"C:\Users\rdh08\Desktop\2026_Data_Visualization\Dataset\경기도 성남시_장애인_복지시설_현황_20250524.csv"
# df_disability_welfare_center = pd.read_csv(path_disability_welfare_center, encoding="utf-8-sig")
