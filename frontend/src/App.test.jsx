import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import App from "./App.jsx";

vi.mock("./speech.js", () => ({
  unlockAudio: vi.fn(), recognitionSupported: () => false, speak: vi.fn(), stopSpeaking: vi.fn(),
  findVoice: vi.fn().mockResolvedValue({}), startListening: vi.fn(),
}));

const situation = {
  reply: "வணக்கம்! நான் சகி.", lang: "ta", profile: {}, understood: [], result: null,
  step: { id: "situation", slot: "marital_status", input: "choice",
    options: [{ value: "widow", icon: "🕯️", label: "கணவர் இறந்துவிட்டார்" }, { value: "married", icon: "🏠", label: "கணவருடன் வாழ்கிறேன்" }] },
};
const ageStep = { ...situation, reply: "சரி. உங்களுக்கு எத்தனை வயது?", profile: { marital_status: "widow" },
  understood: [{ slot: "marital_status", icon: "🕯️", text: "கணவர் இறந்துவிட்டார்" }],
  step: { id: "age", slot: "age", input: "number", min: 18, max: 100, default: 40 } };
const done = { ...ageStep, reply: "நல்ல செய்தி!", profile: { marital_status: "widow", age: 45, assets_over_limit: false },
  step: { id: "result", slot: null, input: "none" },
  result: { status: "potential_match", headline: "நீங்கள் விண்ணப்பிக்கலாம்", message: "நல்ல செய்தி!", verified_on: "2026-10-01",
    scheme: { id: "dwps", name: "ஆதரவற்ற விதவை ஓய்வூதியத் திட்டம்", short: "விதவை ஓய்வூதியம்", amount: "மாதம் ₹1,200" },
    documents: [{ key: "aadhaar", label: "ஆதார் அட்டை", icon: "🪪", ready: false }, { key: "bank_passbook", label: "வங்கிக் கணக்குப் புத்தகம்", icon: "🏦", ready: false }],
    steps: [{ icon: "📋", text: "ஆவணங்களைத் தயார் செய்யுங்கள்" }], share_text: "x", sources: [{ title: "Official", url: "https://example.org" }] } };

let calls;
beforeEach(() => {
  calls = [];
  globalThis.fetch = vi.fn(async (url, init) => {
    if (url === "/api/health") return { ok: true, json: async () => ({ tts: false }) };
    const body = JSON.parse(init.body);
    calls.push(body);
    const data = body.start ? situation : body.answer?.slot === "marital_status" ? ageStep : done;
    return { ok: true, json: async () => data };
  });
});

describe("Sakhi UI", () => {
  it("opens in Tamil with one big start button and sends nothing until tapped", async () => {
    render(<App />);
    expect(screen.getByText("தொடங்குங்கள்", { exact: false })).toBeTruthy();
    expect(calls).toHaveLength(0);
  });

  it("walks a widow through voice-free taps to a document checklist", async () => {
    const user = userEvent.setup();
    render(<App />);
    await user.click(screen.getByText("தொடங்குங்கள்", { exact: false }));
    await user.click(await screen.findByText("கணவர் இறந்துவிட்டார்", { selector: ".cLabel" }));
    await screen.findByText("40");
    await user.click(screen.getByLabelText("+5"));
    await user.click(screen.getByText("சரி", { exact: false, selector: ".primary" }));
    await screen.findByText("நீங்கள் விண்ணப்பிக்கலாம்");
    expect(calls.at(-1).answer).toEqual({ slot: "age", value: 45 });
    expect(calls.at(-1).pending).toBe("age");
    expect(document.querySelector(".schemeBox").textContent).toContain("மாதம் ₹1,200");

    await user.click(document.querySelector(".docs").querySelector("button"));   // tick Aadhaar
    expect(screen.getByText(/1\/2/)).toBeTruthy();
  });

  it("lets her tap a chip to change an earlier answer", async () => {
    const user = userEvent.setup();
    render(<App />);
    await user.click(screen.getByText("தொடங்குங்கள்", { exact: false }));
    await user.click(await screen.findByText("கணவர் இறந்துவிட்டார்", { selector: ".cLabel" }));
    await user.click(await screen.findByText("கணவர் இறந்துவிட்டார்", { selector: ".chips button", exact: false }));
    await waitFor(() => expect(calls.at(-1).ask).toBe("marital_status"));
  });

  it("shows a friendly Tamil error when the server is unreachable", async () => {
    globalThis.fetch = vi.fn(async (url) => { if (url === "/api/health") return { ok: true, json: async () => ({}) }; throw new Error("down"); });
    const user = userEvent.setup();
    render(<App />);
    await user.click(screen.getByText("தொடங்குங்கள்", { exact: false }));
    expect((await screen.findByRole("alert")).textContent).toContain("இணைப்பில் சிக்கல்");
  });

  it("switches to English", async () => {
    const user = userEvent.setup();
    render(<App />);
    await user.click(screen.getByText("English"));
    expect(screen.getByText("Start", { exact: false })).toBeTruthy();
  });
});
