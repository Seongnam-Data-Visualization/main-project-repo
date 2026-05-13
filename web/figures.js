const FIGURE_GROUPS = [
  {
    id: "type-map",
    category: "integrated",
    title: "성남시 행정동 Type Label 지도",
    description: "주거·노동·교통 3-axis 통합 점수로 분류한 Type A-D 지도와 구 경계.",
    figures: [
      { path: "../analysis/figures/seongnam_type_label_map.png", title: "성남시 행정동 Type Label 지도" },
    ],
  },
  {
    id: "residential-insights",
    category: "residential",
    title: "주거 종합 인사이트",
    description: "핵심 인사이트 요약, 행정동 수요 포지셔닝, 구별 수요-공급-가격 비교.",
    figures: [
      { path: "../residential/data/processed/python_visualizations/15_insight_executive_summary.png", title: "주거 데이터 핵심 인사이트" },
      { path: "../residential/data/processed/python_visualizations/16_insight_admin_dong_quadrants.png", title: "행정동 수요 포지셔닝" },
      { path: "../residential/data/processed/python_visualizations/17_insight_gu_demand_supply_price.png", title: "구별 수요-공급-가격 포지셔닝" },
    ],
  },
  {
    id: "housing-supply",
    category: "residential",
    title: "주택 공급 구조",
    description: "구별 주택 유형 구성, 아파트 집중도, 연립·다세대 비중 비교.",
    figures: [
      { path: "../residential/data/processed/python_visualizations/06_gu_housing_stock_composition.png", title: "구별 주택 재고 구성" },
      { path: "../residential/data/processed/figures/apartment_ratio_by_region.png", title: "아파트 비율" },
      { path: "../residential/data/processed/figures/rowhouse_multifamily_ratio_by_region.png", title: "연립·다세대 비율" },
    ],
  },
  {
    id: "employment-gu",
    category: "employment",
    title: "구별 일자리 구조",
    description: "구별 종사자 규모, 산업 구성, 사업체-종사자 관계.",
    figures: [
      { path: "../business_employment/data/processed/figures/gu_total_workers_bar.png", title: "구별 종사자 수" },
      { path: "../business_employment/data/processed/figures/gu_industry_stack_bar.png", title: "구별 산업 구성" },
      { path: "../business_employment/data/processed/figures/scatter_biz_vs_workers.png", title: "사업체 수와 종사자 수" },
    ],
  },
  {
    id: "employment-dong",
    category: "employment",
    title: "동별 일자리 특성",
    description: "행정동 단위 종사자 규모, 고용 안정성, IT 법인 집중도.",
    figures: [
      { path: "../business_employment/data/processed/figures/dong_total_workers.png", title: "행정동별 종사자 수" },
      { path: "../business_employment/data/processed/figures/dong_regular_worker_ratio.png", title: "행정동별 상용근로자 비율" },
      { path: "../business_employment/data/processed/figures/dong_it_corp_ratio.png", title: "행정동별 IT 법인 비율" },
    ],
  },
  {
    id: "transport-priority",
    category: "transport",
    title: "교통 우선 개입 분석",
    description: "높은 통근 수요와 낮은 접근성이 겹치는 동을 사분면·우선순위로 식별.",
    figures: [
      { path: "../transport/transport/data/processed/figures/high_demand_low_access_top10.png", title: "높은 수요·낮은 접근성 Top 10" },
      { path: "../transport/data/processed/figures/transport_quadrant_story.png", title: "교통 사분면 분석" },
      { path: "../transport/data/processed/figures/transport_priority_story.png", title: "교통 투자 우선순위" },
    ],
  },
  {
    id: "transport-commute",
    category: "transport",
    title: "통근-접근성 구조",
    description: "동별 통근 수요와 접근성 점수의 관계, 교통 변수 전체 프로파일.",
    figures: [
      { path: "../transport/transport/data/processed/figures/commute_vs_accessibility.png", title: "통근 수요와 접근성" },
      { path: "../transport/data/processed/figures/transport_profile_heatmap.png", title: "교통 변수 프로파일 히트맵" },
    ],
  },
  {
    id: "transport-mode",
    category: "transport",
    title: "수단 분담과 혼잡",
    description: "구별 대중교통·승용차 수단 구조와 도로 혼잡-접근성 관계.",
    figures: [
      { path: "../transport/transport/data/processed/figures/mode_share_by_gu.png", title: "구별 통행 수단 비중" },
      { path: "../transport/data/processed/figures/congestion_vs_accessibility_story.png", title: "혼잡도와 접근성 관계" },
    ],
  },
];
