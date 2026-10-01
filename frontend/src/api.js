async function post(path, body) {
  const res = await fetch(path, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });
  if (!res.ok) throw new Error(res.status === 429 ? "busy" : "server");
  return res;
}

export const chat = async (body) => (await post("/api/chat", body)).json();
export const ttsBlob = async (text) => (await post("/api/tts", { text })).blob();

export async function health() {
  try {
    const res = await fetch("/api/health");
    return res.ok ? await res.json() : {};
  } catch {
    return {};
  }
}
