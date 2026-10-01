export function Header({ t, lang, onLang, onRestart, showRestart, autoListen, onAuto, canListen }) {
  return (
    <header className="topbar noPrint">
      <div className="brand">
        <span className="logo" aria-hidden="true">🪷</span>
        <div>
          <strong>சகி <span className="latin">Sakhi</span></strong>
          <small>{t.tagline}</small>
        </div>
      </div>
      <div className="topActions">
        <div className="seg" role="group" aria-label="Language">
          <button className={lang === "ta" ? "on" : ""} onClick={() => onLang("ta")} aria-pressed={lang === "ta"}>தமிழ்</button>
          <button className={lang === "en" ? "on" : ""} onClick={() => onLang("en")} aria-pressed={lang === "en"}>English</button>
        </div>
        {canListen && showRestart && (
          <button className="iconBtn" onClick={onAuto} aria-pressed={autoListen} title={autoListen ? t.autoOn : t.autoOff}>
            {autoListen ? "🎙️" : "🔇"}
          </button>
        )}
        {showRestart && <button className="iconBtn" onClick={onRestart} aria-label={t.restart} title={t.restart}>↻</button>}
      </div>
    </header>
  );
}

export function Welcome({ t, onStart }) {
  return (
    <section className="welcome noPrint">
      <div className="bigEmoji" aria-hidden="true">🪷</div>
      <h1>{t.welcomeTitle}</h1>
      <p>{t.welcomeSub}</p>
      <button className="startBtn" onClick={onStart}><span aria-hidden="true">🔊</span> {t.start}</button>
      <small className="privacy">🔒 {t.privacy}</small>
    </section>
  );
}

export function SakhiBubble({ text, busy, t, onReplay }) {
  return (
    <section className="bubble noPrint" aria-live="polite">
      <div className="avatar" aria-hidden="true">🪷</div>
      <p className={busy ? "dim" : ""}>{busy ? t.thinking : text}</p>
      <button className="replay" onClick={onReplay} aria-label={t.replay} title={t.replay}>🔊</button>
    </section>
  );
}

export function Chips({ items, t, onPick, disabled }) {
  if (!items.length) return null;
  return (
    <section className="chips noPrint" aria-label={t.understood}>
      <small>{t.understood}</small>
      <div>
        {items.map((c) => (
          <button key={c.slot} onClick={() => onPick(c.slot)} disabled={disabled}><span aria-hidden="true">{c.icon}</span> {c.text} <span aria-hidden="true">✎</span></button>
        ))}
      </div>
    </section>
  );
}

export function ChoiceStep({ options, onPick, disabled }) {
  return (
    <div className="choices noPrint">
      {options.map((o) => (
        <button key={String(o.value)} className="choice" onClick={() => onPick(o.value)} disabled={disabled}>
          <span className="cIcon" aria-hidden="true">{o.icon}</span>
          <span className="cLabel">{o.label}</span>
        </button>
      ))}
    </div>
  );
}

export function NumberStep({ step, value, setValue, unit, t, onConfirm, disabled }) {
  const bump = (d) => setValue(Math.min(step.max, Math.max(step.min, value + d)));
  return (
    <div className="numberStep noPrint">
      <div className="stepper">
        <div className="side">
          <button className="pm" onClick={() => bump(-1)} aria-label="-1">−</button>
          <button className="pm small" onClick={() => bump(-5)} aria-label="-5">−5</button>
        </div>
        <div className="num" aria-live="polite"><strong>{value}</strong><span>{unit}</span></div>
        <div className="side">
          <button className="pm" onClick={() => bump(1)} aria-label="+1">+</button>
          <button className="pm small" onClick={() => bump(5)} aria-label="+5">+5</button>
        </div>
      </div>
      <button className="primary" onClick={onConfirm} disabled={disabled}>✓ {t.ok}</button>
    </div>
  );
}

export function MicBar({ t, supported, listening, busy, interim, onMic, typing, setTyping, typed, setTyped, onSend }) {
  return (
    <section className="micBar noPrint">
      {supported && (
        <>
          <button className={`mic ${listening ? "on" : ""}`} onClick={onMic} disabled={busy} aria-pressed={listening}
                  aria-label={listening ? t.listening : t.speak}>
            <span aria-hidden="true">{listening ? "●" : "🎙️"}</span>
          </button>
          <div className="micLabel">{listening ? t.listening : t.speak}</div>
          {interim && <div className="interim" aria-live="polite">“{interim}”</div>}
        </>
      )}
      {!typing ? (
        <button className="linkBtn" onClick={() => setTyping(true)}>✍️ {t.write}</button>
      ) : (
        <form className="typeRow" onSubmit={(e) => { e.preventDefault(); onSend(); }}>
          <input value={typed} onChange={(e) => setTyped(e.target.value)} placeholder={t.placeholder} maxLength={500}
                 aria-label={t.placeholder} autoFocus />
          <button type="submit" disabled={busy || !typed.trim()}>{t.send}</button>
        </form>
      )}
    </section>
  );
}

export function ResultView({ result, ready, onToggle, t, onListenDocs, onPrint, onRestart }) {
  const match = result.status === "potential_match";
  const total = result.documents.length;
  const have = result.documents.filter((d) => ready[d.key]).length;
  return (
    <section className={`result noPrint ${match ? "good" : "soft"}`}>
      <div className="verdict">
        <span className="vIcon" aria-hidden="true">{match ? "✅" : "ℹ️"}</span>
        <h2>{result.headline}</h2>
      </div>
      {result.scheme && (
        <div className="schemeBox">
          <strong>{result.scheme.name}</strong>
          {result.scheme.amount && <span className="amount">{result.scheme.amount}</span>}
        </div>
      )}
      {match && (
        <>
          <h3>📋 {t.docsTitle}</h3>
          <p className="hint">{t.docsHint} · {have}/{total}</p>
          <div className="bar" role="progressbar" aria-valuemin={0} aria-valuemax={total} aria-valuenow={have}><span style={{ width: `${(have / total) * 100}%` }} /></div>
          <ul className="docs">
            {result.documents.map((d) => (
              <li key={d.key}>
                <button className={ready[d.key] ? "doc ok" : "doc"} onClick={() => onToggle(d.key)} aria-pressed={!!ready[d.key]}>
                  <span className="dIcon" aria-hidden="true">{d.icon}</span>
                  <span className="dLabel">{d.label}</span>
                  <span className="tick" aria-hidden="true">{ready[d.key] ? "✓" : ""}</span>
                </button>
              </li>
            ))}
          </ul>

          <h3>👣 {t.stepsTitle}</h3>
          <ol className="steps">
            {result.steps.map((s, i) => (<li key={i}><span className="sNum">{i + 1}</span><span aria-hidden="true">{s.icon}</span> {s.text}</li>))}
          </ol>

          <div className="actions">
            <button onClick={onListenDocs}>🔊 {t.listenDocs}</button>
            <button onClick={onPrint}>🖨️ {t.print}</button>
            <a className="btn" href={`https://wa.me/?text=${encodeURIComponent(result.share_text)}`} target="_blank" rel="noreferrer">💬 {t.whatsapp}</a>
          </div>
        </>
      )}

      <div className="sources">
        <strong>{t.official}</strong>
        {result.sources.map((s) => (<a key={s.url} href={s.url} target="_blank" rel="noreferrer">{s.title} ↗</a>))}
        <small>{t.verified}{result.verified_on}</small>
      </div>
      <button className="primary ghost" onClick={onRestart}>↻ {t.restart}</button>
    </section>
  );
}

export function PrintSheet({ result, ready, t }) {
  if (!result || result.status !== "potential_match") return null;
  return (
    <section className="printSheet">
      <h1>{t.printTitle}</h1>
      <h2>{result.scheme.name}</h2>
      <p><strong>{result.scheme.amount}</strong></p>
      <h3>{t.printDocs}</h3>
      <ul>{result.documents.map((d) => (<li key={d.key}>{ready[d.key] ? "☑" : "☐"} {d.label}</li>))}</ul>
      <ol>{result.steps.map((s, i) => (<li key={i}>{s.text}</li>))}</ol>
      <p className="fine">{t.disclaimer}</p>
      <p className="fine">{result.sources[0].url}</p>
    </section>
  );
}
