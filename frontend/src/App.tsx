import { useEffect, useRef, useState } from "react";
import { generateDossier } from "./api";
import type { GenerateResponse } from "./types";
import { DossierView } from "./components/DossierView";

const LOG_LINES = [
  "opening a file on the prospect…",
  "reading their homepage the way a rep never has time to…",
  "extracting positioning, vocabulary, and tone…",
  "inferring the pains behind the marketing copy…",
  "re-skinning Meridian in their brand and language…",
  "fabricating twelve months of plausible history…",
  "drafting the discovery brief…",
  "running conservative value math…",
  "stamping the dossier…",
];

type Phase = "idle" | "loading" | "ready" | "error";

function makeFileNo() {
  const d = new Date();
  const seq = Math.floor(1000 + Math.random() * 9000);
  return `CO-${d.getFullYear()}${String(d.getMonth() + 1).padStart(2, "0")}-${seq}`;
}

export default function App() {
  const [url, setUrl] = useState("");
  const [phase, setPhase] = useState<Phase>("idle");
  const [logIndex, setLogIndex] = useState(0);
  const [result, setResult] = useState<GenerateResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const fileNo = useRef(makeFileNo());

  useEffect(() => {
    if (phase !== "loading") return;
    setLogIndex(0);
    const timer = setInterval(() => {
      setLogIndex((i) => Math.min(i + 1, LOG_LINES.length - 1));
    }, 3200);
    return () => clearInterval(timer);
  }, [phase]);

  async function open(e?: React.FormEvent) {
    e?.preventDefault();
    if (!url.trim() || phase === "loading") return;
    setPhase("loading");
    setError(null);
    setResult(null);
    fileNo.current = makeFileNo();
    try {
      const resp = await generateDossier(url.trim());
      setResult(resp);
      setPhase("ready");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong.");
      setPhase("error");
    }
  }

  function reset() {
    setPhase("idle");
    setResult(null);
    setError(null);
    setUrl("");
  }

  return (
    <>
      <header className="masthead">
        <div className="masthead__logo" onClick={reset} title="Start over">
          COLD<em>OPEN</em>
        </div>
        <span className="micro">Pre-call intelligence · for solutions engineers</span>
      </header>

      {phase !== "ready" && (
        <section className="landing">
          <h1>
            Walk into the first call <em>already knowing them.</em>
          </h1>
          <p className="landing__sub">
            Paste a prospect's website. ColdOpen reads it like a solutions engineer would —
            then hands you a branded demo environment in their vocabulary, a discovery brief,
            and a conservative value case. Before anyone has said hello.
          </p>

          <form className="subject-line" onSubmit={open}>
            <label className="micro" htmlFor="subject">
              Subject:
            </label>
            <input
              id="subject"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="prospect-company.com"
              autoFocus
              spellCheck={false}
            />
            <button type="submit" disabled={phase === "loading"}>
              {phase === "loading" ? "Compiling…" : "Open the file"}
            </button>
          </form>
          <p className="landing__hint">Takes about a minute. Real site in, full dossier out.</p>

          {phase === "loading" && (
            <div className="caselog">
              <div className="micro micro--stamp" style={{ marginBottom: 14 }}>
                Case log · {fileNo.current}
              </div>
              {LOG_LINES.slice(0, logIndex + 1).map((line, i) => (
                <div key={line} className={`caselog__line ${i === logIndex ? "caselog__line--active" : ""}`}>
                  — {line}
                </div>
              ))}
            </div>
          )}

          {phase === "error" && error && <div className="error-note">{error}</div>}
        </section>
      )}

      {phase === "ready" && result && (
        <>
          <DossierView
            dossier={result.dossier}
            seconds={result.generated_in_seconds}
            fileNo={fileNo.current}
          />
          <div className="footer-note">
            <span className="micro">ColdOpen · demo data is generated and illustrative</span>
            <span className="micro" style={{ cursor: "pointer" }} onClick={reset}>
              ← Open another file
            </span>
          </div>
        </>
      )}
    </>
  );
}
