import { useState } from "react";
import type { Dossier } from "../types";
import { DemoCanvas } from "./DemoCanvas";

const TABS = ["Subject", "Exhibit A · Demo", "Discovery Brief", "Value Case"] as const;

function Section({ num, title, children }: { num: string; title: string; children: React.ReactNode }) {
  return (
    <div className="section">
      <div className="section__label">
        <span className="num">{num}</span>
        <span className="micro">{title}</span>
      </div>
      {children}
    </div>
  );
}

export function DossierView({
  dossier,
  seconds,
  fileNo,
}: {
  dossier: Dossier;
  seconds: number;
  fileNo: string;
}) {
  const [tab, setTab] = useState<number>(0);
  const { company, thesis, demo, brief, roi } = dossier;

  return (
    <div className="dossier">
      <div className="dossier__head">
        <div>
          <span className="micro micro--stamp">Dossier · {company.domain}</span>
          <h2 className="dossier__title">{company.name}</h2>
        </div>
        <div className="dossier__meta">
          <span className="stamp">Prepared cold</span>
          <span className="micro">
            File {fileNo} · compiled in {seconds}s
          </span>
        </div>
      </div>

      <div className="tabs" role="tablist">
        {TABS.map((t, i) => (
          <button key={t} className={i === tab ? "active" : ""} onClick={() => setTab(i)} role="tab">
            {t}
          </button>
        ))}
      </div>

      <div className="sheet">
        {tab === 0 && (
          <>
            <Section num="01" title="Who they are">
              <p className="lede">{company.tagline}</p>
              <p className="prose" style={{ marginTop: 16 }}>
                {company.summary}
              </p>
              <div className="kv" style={{ marginTop: 24 }}>
                <div>
                  <span className="micro">Industry</span>
                  <span className="val">{company.industry}</span>
                </div>
                <div>
                  <span className="micro">Likely buyer</span>
                  <span className="val">{company.buyer_persona}</span>
                </div>
                <div>
                  <span className="micro">Brand voice</span>
                  <span className="val">{company.tone}</span>
                </div>
                <div>
                  <span className="micro">Brand color</span>
                  <span className="val">
                    <span
                      style={{
                        display: "inline-block",
                        width: 12,
                        height: 12,
                        background: company.brand_color,
                        marginRight: 8,
                        borderRadius: 3,
                        verticalAlign: "baseline",
                      }}
                    />
                    {company.brand_color}
                  </span>
                </div>
              </div>
            </Section>
            <Section num="02" title="Their vocabulary">
              <p className="prose">Words the demo speaks in — theirs, not ours.</p>
              <div className="chips">
                {company.terminology.map((t) => (
                  <span className="chip" key={t}>
                    {t}
                  </span>
                ))}
              </div>
            </Section>
            <Section num="03" title="Probable pain">
              <div className="pains">
                {company.pain_points.map((p) => (
                  <div className="pain" key={p.title}>
                    <h4>{p.title}</h4>
                    <p>{p.detail}</p>
                  </div>
                ))}
              </div>
            </Section>
            <Section num="04" title="The angle">
              <div className="thesis">
                <div className="thesis__row">
                  <span className="micro">Position as</span>
                  <p>{thesis.positioning}</p>
                </div>
                <div className="thesis__row">
                  <span className="micro">The demo shows</span>
                  <p>{thesis.demo_world}</p>
                </div>
                <div className="thesis__row thesis__row--never">
                  <span className="micro micro--stamp">Never</span>
                  <p>{thesis.never_do}</p>
                </div>
              </div>
            </Section>
          </>
        )}

        {tab === 1 && (
          <DemoCanvas demo={demo} brandColor={company.brand_color} domain={company.domain} />
        )}

        {tab === 2 && (
          <>
            <Section num="01" title="Pre-call read">
              <p className="lede">{brief.snapshot}</p>
            </Section>
            <Section num="02" title="Hypotheses to test">
              <ol className="numlist">
                {brief.hypotheses.map((h) => (
                  <li key={h}>
                    <div className="q">{h}</div>
                  </li>
                ))}
              </ol>
            </Section>
            <Section num="03" title="Discovery questions">
              <ol className="numlist">
                {brief.questions.map((q) => (
                  <li key={q.question}>
                    <div>
                      <div className="micro topic">{q.topic}</div>
                      <div className="q">{q.question}</div>
                      <div className="why">{q.why}</div>
                    </div>
                  </li>
                ))}
              </ol>
            </Section>
            <Section num="04" title="Landmines">
              <ol className="numlist">
                {brief.landmines.map((l) => (
                  <li key={l}>
                    <div className="q">{l}</div>
                  </li>
                ))}
              </ol>
            </Section>
            <Section num="05" title="Against the status quo">
              <p className="prose">{brief.competitive_angle}</p>
            </Section>
          </>
        )}

        {tab === 3 && (
          <>
            <Section num="01" title="The headline">
              <p className="lede">{roi.headline}</p>
            </Section>
            <Section num="02" title="Value drivers">
              <table className="roi-table">
                <thead>
                  <tr>
                    <th>Driver</th>
                    <th>Conservative assumption</th>
                    <th style={{ textAlign: "right" }}>Annual value</th>
                  </tr>
                </thead>
                <tbody>
                  {roi.lines.map((line) => (
                    <tr key={line.label}>
                      <td className="label">{line.label}</td>
                      <td className="assumption">{line.assumption}</td>
                      <td className="money">{line.annual_value}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
              <p className="fineprint">{roi.disclaimer}</p>
            </Section>
            <Section num="03" title="Payback & inaction">
              <div className="kv">
                <div>
                  <span className="micro">Estimated payback</span>
                  <span className="val">{roi.payback}</span>
                </div>
                <div>
                  <span className="micro">Cost of waiting</span>
                  <span className="val">{roi.cost_of_inaction}</span>
                </div>
              </div>
            </Section>
          </>
        )}
      </div>
    </div>
  );
}
