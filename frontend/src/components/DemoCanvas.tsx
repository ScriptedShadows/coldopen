import type { DemoConfig } from "../types";

function TrendChart({ points, color }: { points: { label: string; value: number }[]; color: string }) {
  const w = 560;
  const h = 180;
  const pad = { top: 12, right: 8, bottom: 26, left: 8 };
  const values = points.map((p) => p.value);
  const min = Math.min(...values);
  const max = Math.max(...values);
  const span = max - min || 1;
  const x = (i: number) => pad.left + (i / (points.length - 1)) * (w - pad.left - pad.right);
  const y = (v: number) => pad.top + (1 - (v - min) / span) * (h - pad.top - pad.bottom);
  const line = points.map((p, i) => `${i === 0 ? "M" : "L"}${x(i).toFixed(1)},${y(p.value).toFixed(1)}`).join(" ");
  const area = `${line} L${x(points.length - 1).toFixed(1)},${h - pad.bottom} L${x(0).toFixed(1)},${h - pad.bottom} Z`;

  return (
    <svg viewBox={`0 0 ${w} ${h}`} style={{ width: "100%", height: "auto", display: "block" }} role="img">
      <defs>
        <linearGradient id="trend-fill" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor={color} stopOpacity="0.22" />
          <stop offset="100%" stopColor={color} stopOpacity="0.02" />
        </linearGradient>
      </defs>
      <path d={area} fill="url(#trend-fill)" />
      <path d={line} fill="none" stroke={color} strokeWidth="2.5" strokeLinejoin="round" strokeLinecap="round" />
      {points.map((p, i) => (
        <text
          key={p.label + i}
          x={x(i)}
          y={h - 8}
          textAnchor="middle"
          fontSize="10"
          fill="#9a9da4"
          fontFamily="inherit"
        >
          {p.label}
        </text>
      ))}
      <circle cx={x(points.length - 1)} cy={y(points[points.length - 1].value)} r="4" fill={color} />
    </svg>
  );
}

export function DemoCanvas({ demo, brandColor, domain }: { demo: DemoConfig; brandColor: string; domain: string }) {
  const initial = demo.workspace_name.trim().charAt(0).toUpperCase() || "M";
  return (
    <div>
      <div className="exhibit-note">
        <span className="micro micro--stamp">Exhibit A</span>
        <span className="micro"> — tailored demo environment, generated from {domain}</span>
      </div>
      <div className="browser">
        <div className="browser__bar">
          <div className="browser__dots">
            <span />
            <span />
            <span />
          </div>
          <div className="browser__url">meridian.app/{demo.demo_slug}/overview</div>
        </div>
        <div className="demo">
          <div className="demo__top" style={{ background: brandColor }}>
            <div className="demo__brand">
              <span className="dot">{initial}</span>
              {demo.workspace_name}
            </div>
            <div className="demo__meridian">Powered by Meridian</div>
          </div>
          <div className="demo__nav">
            {demo.nav_items.map((item, i) => (
              <span key={item} className={i === 0 ? "on" : ""}>
                {item}
              </span>
            ))}
          </div>
          <div className="demo__body">
            <div className="demo__kpis">
              {demo.kpis.map((kpi) => (
                <div className="kpi" key={kpi.label}>
                  <div className="k-label">{kpi.label}</div>
                  <div className="k-value">{kpi.value}</div>
                  <div className={`k-delta ${kpi.good ? "up" : "down"}`}>{kpi.delta}</div>
                </div>
              ))}
            </div>
            <div className="panel">
              <h5>{demo.trend_title}</h5>
              <TrendChart points={demo.trend} color={brandColor} />
            </div>
            <div className="demo__row">
              <div className="panel">
                <h5>{demo.table_title}</h5>
                <table className="demo-table">
                  <thead>
                    <tr>
                      {demo.table_columns.map((c) => (
                        <th key={c}>{c}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {demo.table_rows.map((row, i) => (
                      <tr key={i}>
                        {row.cells.map((cell, j) => (
                          <td key={j}>{cell}</td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              <div className="panel">
                <h5>Signals</h5>
                {demo.insights.map((ins) => (
                  <div className="insight" key={ins.title}>
                    <span className={`tag ${ins.kind}`}>{ins.kind}</span>
                    <div>
                      <h6>{ins.title}</h6>
                      <p>{ins.body}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="talktrack">
        <div className="micro micro--stamp" style={{ marginBottom: 14 }}>
          Talk track — what to say while screen-sharing
        </div>
        <ol className="numlist">
          {demo.talk_track.map((beat) => (
            <li key={beat}>
              <div className="q talktrack__beat">“{beat}”</div>
            </li>
          ))}
        </ol>
      </div>
    </div>
  );
}
