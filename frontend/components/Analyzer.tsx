"use client";

import Image from "next/image";
import { FormEvent, useEffect, useMemo, useState } from "react";
import { analyzeScenario, fetchHealth } from "@/lib/api";
import type { AnalysisResponse, HealthResponse, SchoolAnalysis, SchoolKey } from "@/lib/types";

const SAMPLE_SCENARIOS = [
  "A buyer and seller complete an online sale, but the product description was ambiguous and the buyer asks whether the contract remains binding.",
  "A person finds lost property in a public place and wants to know what duties arise before they may use or dispose of it.",
  "Two business partners agree orally to share profits from a small venture, then disagree after one partner contributes most of the labor."
];

const SCHOOL_ORDER: SchoolKey[] = ["hanafi", "maliki", "shafii", "hanbali"];

const SOURCE_WEIGHTS: Record<SchoolKey, { label: string; weight: number }[]> = {
  hanafi: [
    { label: "Quran", weight: 100 },
    { label: "Hadith", weight: 78 },
    { label: "Qiyas", weight: 66 },
    { label: "Istihsan", weight: 58 },
    { label: "Ijma", weight: 44 }
  ],
  maliki: [
    { label: "Quran", weight: 100 },
    { label: "Medina", weight: 84 },
    { label: "Ijma", weight: 72 },
    { label: "Qiyas", weight: 46 }
  ],
  shafii: [
    { label: "Quran", weight: 100 },
    { label: "Hadith", weight: 88 },
    { label: "Qiyas", weight: 35 }
  ],
  hanbali: [
    { label: "Quran", weight: 100 },
    { label: "Hadith", weight: 92 },
    { label: "Ijma", weight: 52 },
    { label: "Qiyas", weight: 12 }
  ]
};

export function Analyzer() {
  const [scenario, setScenario] = useState("");
  const [result, setResult] = useState<AnalysisResponse | null>(null);
  const [activeSchool, setActiveSchool] = useState<SchoolKey>("hanafi");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [health, setHealth] = useState<HealthResponse | null>(null);

  useEffect(() => {
    fetchHealth()
      .then(setHealth)
      .catch((err: Error) => setError(err.message));
  }, []);

  const activeAnalysis = useMemo(() => {
    return result?.schools.find((school) => school.school === activeSchool) ?? null;
  }, [activeSchool, result]);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setResult(null);

    if (scenario.trim().length < 20) {
      setError("Please enter a scenario with enough detail to compare.");
      return;
    }

    setIsLoading(true);
    try {
      const analysis = await analyzeScenario(scenario);
      setResult(analysis);
      setActiveSchool(analysis.schools[0]?.school ?? "hanafi");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Analysis failed.");
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <main className="min-h-screen bg-paper text-ink">
      <header className="border-b border-ink/15 bg-vellum">
        <div className="mx-auto flex max-w-7xl flex-col gap-4 px-5 py-6 md:flex-row md:items-end md:justify-between">
          <div>
            <p className="section-kicker">Educational RAG prototype</p>
            <h1 className="font-serif text-4xl font-semibold leading-tight md:text-5xl">
              Comparative Legal Engine
            </h1>
            <p className="mt-3 max-w-3xl text-base leading-7 text-slate">
              A structured comparison of how Hanafi, Maliki, Shafi&apos;i, and Hanbali
              methodologies can produce different educational outcomes from the same facts.
            </p>
          </div>
          <div className="status-strip" aria-live="polite">
            <span className={health?.gemini_api_key_configured ? "status-dot ok" : "status-dot warn"} />
            <span>
              {health?.gemini_api_key_configured
                ? `RAG store: ${health.file_search_store}`
                : "Backend key not configured"}
            </span>
          </div>
        </div>
      </header>

      <section className="border-b border-ink/15 bg-ink text-vellum">
        <div className="mx-auto max-w-7xl px-5 py-3 text-sm leading-6">
          Educational demonstration only. Not legal advice, not a fatwa, and not a
          substitute for a qualified lawyer, scholar, or jurisdiction-specific authority.
        </div>
      </section>

      <div className="mx-auto grid max-w-7xl gap-6 px-5 py-8 lg:grid-cols-[minmax(0,1.05fr)_minmax(360px,0.95fr)]">
        <section className="tool-panel">
          <form onSubmit={handleSubmit} className="space-y-5">
            <div className="flex flex-col gap-2">
              <label htmlFor="scenario" className="label">
                Case scenario
              </label>
              <textarea
                id="scenario"
                value={scenario}
                onChange={(event) => setScenario(event.target.value)}
                placeholder="Describe the facts, parties, disputed action, and what outcome is being compared."
                className="scenario-input"
                rows={11}
                maxLength={4000}
              />
              <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                <p className="text-sm text-slate">{scenario.length}/4000 characters</p>
                <button type="submit" disabled={isLoading} className="primary-button">
                  <span aria-hidden="true">-&gt;</span>
                  {isLoading ? "Analyzing" : "Analyze"}
                </button>
              </div>
            </div>
          </form>

          <div className="sample-row" aria-label="Sample scenarios">
            {SAMPLE_SCENARIOS.map((sample) => (
              <button
                key={sample}
                type="button"
                className="sample-button"
                onClick={() => setScenario(sample)}
              >
                {sample}
              </button>
            ))}
          </div>

          {error ? <div className="error-box">{error}</div> : null}
          {isLoading ? <LoadingState /> : null}
        </section>

        <aside className="method-panel">
          <Image
            src="/source-lattice.svg"
            alt="Abstract layered source hierarchy"
            width={720}
            height={360}
            className="source-asset"
            priority
          />
          <div className="method-grid">
            {SCHOOL_ORDER.map((schoolKey) => (
              <button
                key={schoolKey}
                type="button"
                className={`method-button ${activeSchool === schoolKey ? "active" : ""}`}
                onClick={() => setActiveSchool(schoolKey)}
              >
                {schoolName(schoolKey)}
              </button>
            ))}
          </div>
          <SourceWeights activeSchool={activeSchool} />
        </aside>
      </div>

      {result ? (
        <section className="border-t border-ink/15 bg-vellum">
          <div className="mx-auto max-w-7xl px-5 py-8">
            <SynthesisView result={result} />
            <div className="mt-6 grid gap-5 lg:grid-cols-[minmax(300px,0.85fr)_minmax(0,1.15fr)]">
              <SchoolList
                schools={result.schools}
                activeSchool={activeSchool}
                onSelect={setActiveSchool}
              />
              {activeAnalysis ? <SchoolDetail school={activeAnalysis} /> : null}
            </div>
          </div>
        </section>
      ) : null}
    </main>
  );
}

function LoadingState() {
  return (
    <div className="loading-box">
      <div className="loading-bar">
        <span />
      </div>
      <p>Running four source-grounded school agents and one synthesis pass.</p>
    </div>
  );
}

function SourceWeights({ activeSchool }: { activeSchool: SchoolKey }) {
  return (
    <div className="source-stack" aria-label={`${schoolName(activeSchool)} source weights`}>
      <div className="source-stack-header">
        <span>{schoolName(activeSchool)}</span>
        <span>Authority profile</span>
      </div>
      {SOURCE_WEIGHTS[activeSchool].map((item) => (
        <div className="weight-row" key={item.label}>
          <span>{item.label}</span>
          <div className="weight-track">
            <span style={{ width: `${item.weight}%` }} />
          </div>
        </div>
      ))}
    </div>
  );
}

function SynthesisView({ result }: { result: AnalysisResponse }) {
  return (
    <div className="synthesis-band">
      <div>
        <p className="section-kicker">Synthesis</p>
        <h2 className="font-serif text-3xl font-semibold">Where the methods diverge</h2>
      </div>
      <div className="synthesis-copy">
        <p>{result.synthesis.core_divergence}</p>
        <p>
          <strong>Consensus:</strong> {result.synthesis.consensus_point}
        </p>
      </div>
    </div>
  );
}

function SchoolList({
  schools,
  activeSchool,
  onSelect
}: {
  schools: SchoolAnalysis[];
  activeSchool: SchoolKey;
  onSelect: (school: SchoolKey) => void;
}) {
  return (
    <div className="school-list">
      {schools.map((school) => (
        <button
          key={school.school}
          type="button"
          className={`school-card ${activeSchool === school.school ? "active" : ""}`}
          onClick={() => onSelect(school.school)}
        >
          <span>{school.school_name}</span>
          <p>{school.final_ruling}</p>
        </button>
      ))}
    </div>
  );
}

function SchoolDetail({ school }: { school: SchoolAnalysis }) {
  return (
    <article className="detail-panel">
      <div className="detail-header">
        <div>
          <p className="section-kicker">{school.school_name}</p>
          <h2 className="font-serif text-3xl font-semibold">Ruling and support</h2>
        </div>
        <span className={`school-token ${school.school}`}>{school.school_name}</span>
      </div>

      <p className="ruling-text">{school.final_ruling}</p>

      <section className="detail-section">
        <h3>Evidence</h3>
        <div className="evidence-list">
          {school.primary_evidence.map((evidence, index) => (
            <div className="evidence-item" key={`${evidence.citation}-${index}`}>
              <div className="evidence-meta">
                <span>{evidence.source_type}</span>
                <cite>{evidence.citation}</cite>
              </div>
              <blockquote>{evidence.quote}</blockquote>
              <p>{evidence.relevance}</p>
            </div>
          ))}
        </div>
      </section>

      {school.legal_reasoning.length ? (
        <section className="detail-section">
          <h3>Reasoning</h3>
          <div className="reasoning-list">
            {school.legal_reasoning.map((reasoning, index) => (
              <div className="reasoning-item" key={`${reasoning.reasoning_type}-${index}`}>
                <span>{reasoning.reasoning_type}</span>
                <p>{reasoning.explanation}</p>
              </div>
            ))}
          </div>
        </section>
      ) : (
        <section className="detail-section">
          <h3>Reasoning</h3>
          <p className="muted-copy">
            This school output did not use a separate rational-reasoning step.
          </p>
        </section>
      )}

      <section className="detail-section">
        <h3>Source scope</h3>
        <div className="source-pills">
          {school.methodology.source_scope.map((source) => (
            <span key={source}>{source}</span>
          ))}
        </div>
      </section>
    </article>
  );
}

function schoolName(school: SchoolKey) {
  const names: Record<SchoolKey, string> = {
    hanafi: "Hanafi",
    maliki: "Maliki",
    shafii: "Shafi'i",
    hanbali: "Hanbali"
  };
  return names[school];
}
