export interface PainPoint {
  title: string;
  detail: string;
}

export interface CompanyProfile {
  name: string;
  domain: string;
  tagline: string;
  industry: string;
  summary: string;
  buyer_persona: string;
  brand_color: string;
  tone: string;
  terminology: string[];
  pain_points: PainPoint[];
}

export interface SalesThesis {
  positioning: string;
  demo_world: string;
  never_do: string;
}

export interface KPI {
  label: string;
  value: string;
  delta: string;
  good: boolean;
}

export interface TrendPoint {
  label: string;
  value: number;
}

export interface Insight {
  kind: "win" | "risk" | "watch";
  title: string;
  body: string;
}

export interface DemoConfig {
  workspace_name: string;
  demo_slug: string;
  nav_items: string[];
  kpis: KPI[];
  trend_title: string;
  trend: TrendPoint[];
  table_title: string;
  table_columns: string[];
  table_rows: { cells: string[] }[];
  insights: Insight[];
  talk_track: string[];
}

export interface BriefQuestion {
  topic: string;
  question: string;
  why: string;
}

export interface DiscoveryBrief {
  snapshot: string;
  hypotheses: string[];
  questions: BriefQuestion[];
  landmines: string[];
  competitive_angle: string;
}

export interface RoiLine {
  label: string;
  assumption: string;
  annual_value: string;
}

export interface RoiSheet {
  headline: string;
  lines: RoiLine[];
  payback: string;
  cost_of_inaction: string;
  disclaimer: string;
}

export interface Dossier {
  company: CompanyProfile;
  thesis: SalesThesis;
  demo: DemoConfig;
  brief: DiscoveryBrief;
  roi: RoiSheet;
}

export interface GenerateResponse {
  dossier: Dossier;
  scraped_title: string | null;
  generated_in_seconds: number;
}
