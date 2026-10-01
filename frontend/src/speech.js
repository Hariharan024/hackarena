import { ttsBlob } from "./api.js";

// A one-sample silent clip, played on the first tap so mobile browsers allow later audio.
const SILENT = "data:audio/wav;base64,UklGRiQAAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQAAAAA=";
let audio = null;
let current = 0; // bumped on every speak/stop so stale "ended" callbacks never fire

const getAudio = () => (audio ||= new Audio());

export function unlockAudio() {
  try {
    const a = getAudio();
    a.src = SILENT;
    a.play().catch(() => {});
  } catch { /* audio is a nicety, never a blocker */ }
}

export const recognitionSupported = () =>
  typeof window !== "undefined" && ("SpeechRecognition" in window || "webkitSpeechRecognition" in window);

function voices() {
  return new Promise((resolve) => {
    const synth = window.speechSynthesis;
    if (!synth) return resolve([]);
    const now = synth.getVoices();
    if (now.length) return resolve(now);
    const done = () => resolve(synth.getVoices());
    synth.addEventListener?.("voiceschanged", done, { once: true });
    setTimeout(done, 800);
  });
}

export async function findVoice(locale) {
  const list = await voices();
  const base = locale.split("-")[0];
  return list.find((v) => v.lang === locale) || list.find((v) => v.lang?.startsWith(base)) || null;
}

export function stopSpeaking() {
  current += 1;
  try { window.speechSynthesis?.cancel(); } catch { /* ignore */ }
  try { audio?.pause(); } catch { /* ignore */ }
}

export async function speak(text, lang, { useServer = false, onEnd = () => {} } = {}) {
  stopSpeaking();
  const id = current;
  const finish = () => { if (id === current) onEnd(); };

  if (useServer && lang === "ta") {
    try {
      const url = URL.createObjectURL(await ttsBlob(text));
      const a = getAudio();
      a.src = url;
      a.onended = finish;
      a.onerror = finish;
      await a.play();
      return;
    } catch { /* fall back to the browser voice below */ }
  }

  if (!window.speechSynthesis) return finish();
  const locale = lang === "ta" ? "ta-IN" : "en-IN";
  const u = new SpeechSynthesisUtterance(text);
  u.lang = locale;
  u.rate = 0.9;
  const voice = await findVoice(locale);
  if (voice) u.voice = voice;
  u.onend = finish;
  u.onerror = finish;
  window.speechSynthesis.speak(u);
}

export function startListening({ lang, onInterim, onFinal, onError, onEnd }) {
  const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SR) { onError("unsupported"); return null; }
  const rec = new SR();
  rec.lang = lang === "ta" ? "ta-IN" : "en-IN";
  rec.interimResults = true;
  rec.continuous = false;
  let heard = "";
  let cancelled = false;
  rec.onresult = (e) => {
    let interim = "";
    for (let i = e.resultIndex; i < e.results.length; i += 1) {
      const r = e.results[i];
      if (r.isFinal) heard += r[0].transcript; else interim += r[0].transcript;
    }
    onInterim(heard + interim);
  };
  rec.onerror = (e) => onError(e.error);
  rec.onend = () => { onEnd(); if (!cancelled && heard.trim()) onFinal(heard.trim()); };
  try { rec.start(); } catch { onError("start-failed"); }
  return {
    stop: () => { try { rec.stop(); } catch { /* already stopped */ } },                       // finish and send what was heard
    abort: () => { cancelled = true; try { rec.abort(); } catch { /* already stopped */ } },   // throw it away
  };
}
