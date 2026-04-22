export type SchoolKey = "hanafi" | "maliki" | "shafii" | "hanbali";

export type Evidence = {
  source_type: "Quran" | "Hadith" | "Ijma";
  citation: string;
  quote: string;
  relevance: string;
};

export type LegalReasoning = {
  reasoning_type: "Qiyas" | "Istihsan";
  explanation: string;
};

export type Methodology = {
  authority_order: string[];
  reasoning_posture: string;
  source_scope: string[];
};

export type SchoolAnalysis = {
  school: SchoolKey;
  school_name: string;
  final_ruling: string;
  primary_evidence: Evidence[];
  legal_reasoning: LegalReasoning[];
  methodology: Methodology;
};

export type Synthesis = {
  core_divergence: string;
  consensus_point: string;
};

export type AnalysisResponse = {
  scenario: string;
  disclaimer: string;
  generated_at: string;
  synthesis: Synthesis;
  schools: SchoolAnalysis[];
};

export type HealthResponse = {
  status: "ok";
  gemini_api_key_configured: boolean;
  file_search_store: string;
  file_search_model: string;
  synthesis_model: string;
};
