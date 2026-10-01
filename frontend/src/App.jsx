import { useEffect, useRef, useState } from "react";
import { chat, health } from "./api.js";
import { Chips, ChoiceStep, Header, MicBar, NumberStep, PrintSheet, ResultView, SakhiBubble, Welcome } from "./components.jsx";
import { findVoice, recognitionSupported, speak, startListening, stopSpeaking, unlockAudio } from "./speech.js";
import { UI } from "./ui.js";

export default function App() {
  const [lang, setLang] = useState("ta");
  const [turn, setTurn] = useState(null);
  const [busy, setBusy] = useState(false);
  const [listening, setListening] = useState(false);
  const [interim, setInterim] = useState("");
  const [error, setError] = useState("");
  const [typing, setTyping] = useState(false);
  const [typed, setTyped] = useState("");
  const [autoListen, setAutoListen] = useState(true);
  const [num, setNum] = useState(40);
  const [ready, setReady] = useState({});
  const [serverTts, setServerTts] = useState(false);
  const [browserVoice, setBrowserVoice] = useState(true);
  const recRef = useRef(null);
  const live = useRef({});
  live.current = { lang, turn, autoListen, serverTts, browserVoice };
  const supported = recognitionSupported();
  const t = UI[lang];

  useEffect(() => {
    health().then((h) => setServerTts(!!h.tts));
    findVoice("ta-IN").then((v) => setBrowserVoice(!!v));
    return () => { stopSpeaking(); recRef.current?.abort(); };
  }, []);

  useEffect(() => {
    const s = turn?.step;
    if (s?.input === "number") setNum(turn.profile[s.slot] ?? s.default);
  }, [turn?.step?.id]); // eslint-disable-line react-hooks/exhaustive-deps

  function say(text, step, l = live.current.lang) {
    const { autoListen: auto, serverTts: srv, browserVoice: bv } = live.current;
    speak(text, l, { useServer: srv && !bv, onEnd: () => { if (auto && step?.id !== "result" && supported) listen(); } });
  }

  async function post(extra, l = live.current.lang) {
    const tn = live.current.turn;
    recRef.current?.abort();
    setBusy(true);
    setError("");
    try {
      const data = await chat({ lang: l, profile: tn?.profile ?? {}, pending: tn?.step?.slot ?? undefined, ...extra });
      setTurn(data);
      if (data.result) setReady(Object.fromEntries(data.result.documents.map((d) => [d.key, d.ready])));
      say(data.reply, data.step, l);
    } catch (e) {
      console.error("Sakhi request failed:", e);
      setError(e.message === "busy" ? UI[l].errBusy : UI[l].errNet);
    } finally {
      setBusy(false);
    }
  }

  function listen() {
    const l = live.current.lang;
    stopSpeaking();
    recRef.current?.abort();
    setInterim("");
    setError("");
    setListening(true);
    recRef.current = startListening({
      lang: l,
      onInterim: setInterim,
      onFinal: (text) => { setInterim(""); post({ message: text }); },
      onEnd: () => setListening(false),
      onError: (code) => {
        setListening(false);
        if (code === "not-allowed" || code === "service-not-allowed") setError(UI[l].errMicDenied);
        else if (code === "no-speech") setError(UI[l].errNoSpeech);
        else if (code !== "aborted") setError(UI[l].errMic);
      },
    });
  }

  const begin = () => { unlockAudio(); post({ start: true }); };
  const restart = () => { stopSpeaking(); recRef.current?.abort(); setListening(false); setTurn(null); setReady({}); setError(""); setInterim(""); setTyped(""); };
  const switchLang = (l) => { if (l === lang) return; setLang(l); if (turn) post({ start: true }, l); };
  const sendTyped = () => { const m = typed.trim(); if (m) { setTyped(""); post({ message: m }); } };
  const step = turn?.step;
  const result = turn?.result;

  return (
    <main className="app">
      <Header t={t} lang={lang} onLang={switchLang} onRestart={restart} showRestart={!!turn}
              autoListen={autoListen} onAuto={() => setAutoListen((a) => !a)} canListen={supported} />

      {error && <div className="error noPrint" role="alert">{error}</div>}
      {!turn && !busy && <Welcome t={t} onStart={begin} />}

      {(turn || busy) && (
        <>
          <SakhiBubble text={turn?.reply} busy={busy && !turn} t={t} onReplay={() => speak(turn.reply, lang, { useServer: serverTts && !browserVoice })} />
          {!browserVoice && !serverTts && <div className="notice noPrint">{t.noVoice}</div>}

          {turn && step.id !== "result" && (
            <>
              {step.input === "choice" && <ChoiceStep options={step.options} disabled={busy} onPick={(v) => post({ answer: { slot: step.slot, value: v } })} />}
              {step.input === "yesno" && <ChoiceStep options={step.options} disabled={busy} onPick={(v) => post({ answer: { slot: step.slot, value: v } })} />}
              {step.input === "number" && (
                <NumberStep step={step} value={num} setValue={setNum} unit={step.slot === "age" ? t.age : t.years} t={t}
                            disabled={busy} onConfirm={() => post({ answer: { slot: step.slot, value: num } })} />
              )}
              <MicBar t={t} supported={supported} listening={listening} busy={busy} interim={interim}
                      onMic={() => (listening ? recRef.current?.stop() : listen())}
                      typing={typing || !supported} setTyping={setTyping} typed={typed} setTyped={setTyped} onSend={sendTyped} />
            </>
          )}

          {turn && <Chips items={turn.understood} t={t} disabled={busy} onPick={(slot) => post({ ask: slot })} />}

          {result && (
            <ResultView result={result} ready={ready} t={t} onRestart={restart}
                        onToggle={(k) => setReady((r) => ({ ...r, [k]: !r[k] }))}
                        onListenDocs={() => speak(result.documents.map((d) => d.label).join("، "), lang, { useServer: serverTts && !browserVoice })}
                        onPrint={() => window.print()} />
          )}
        </>
      )}

      <footer className="noPrint">{t.disclaimer}</footer>
      <PrintSheet result={result} ready={ready} t={t} />
    </main>
  );
}
