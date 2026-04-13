from config import(
    df_population,
    df_disability_population,
    df_low_income_population,
    df_single_person_household,
    df_basement_living_beneficiaries
    )

print("경기도 성남시_인구및세대_현황_20260331 (1).csv")
print(df_population.columns)

print("\n경기도 성남시_장애인등록_현황_20250524.csv")
print(df_disability_population.columns)

print("\n경기도 성남시_저소득_한부모가족_현황_20250531.csv")
print(df_low_income_population.columns)

print("\n경기도 성남시_1인세대_현황_20250430.csv")
print(df_single_person_household.columns)

print("\n경기도 성남시_기초생활수급자_현황_20250912.csv")
print(df_basement_living_beneficiaries.columns)

# 1인세대 "1인세대수_계" col의 row들 확인
print("\n경기도 성남시_1인세대_현황_20250430.csv - 1인세대수_계")
print(df_single_person_household["1인세대수_계"])