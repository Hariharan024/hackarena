// Real UI against a real running backend:  SAKHI_E2E_URL=http://127.0.0.1:8000 npm test
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import App from "./App.jsx";

vi.mock("./speech.js", () => ({
  unlockAudio: vi.fn(), recognitionSupported: () => false, speak: vi.fn(), stopSpeaking: vi.fn(),
  findVoice: vi.fn().mockResolvedValue({}), startListening: vi.fn(),
}));

const base = process.env.SAKHI_E2E_URL;
const realFetch = globalThis.fetch;

describe.skipIf(!base)("end-to-end with the real backend", () => {
  beforeEach(() => { globalThis.fetch = (url, init) => realFetch(base + url, init); });
  afterEach(() => { globalThis.fetch = realFetch; });

  it("a deserted woman types in Tamil and reaches her checklist", async () => {
    const user = userEvent.setup();
    render(<App />);
    await user.click(screen.getByText("தொடங்குங்கள்", { exact: false }));
    const box = await screen.findByLabelText("இங்கே எழுதுங்கள்…");
    await user.type(box, "என் கணவர் என்னை விட்டுப் பிரிந்துவிட்டார், எனக்கு 38 வயது{Enter}");
    await screen.findByText("ஆண்டுகள்");                       // jumped straight to "how many years" - age was understood
    await user.click(screen.getByLabelText("+5"));              // 5 -> 10 years
    await user.click(screen.getByText("சரி", { exact: false, selector: ".primary" }));
    await user.click(await screen.findByText("இல்லை", { selector: ".cLabel" }));   // no property over 1 lakh
    await screen.findByText("நீங்கள் விண்ணப்பிக்கலாம்");
    expect(document.querySelector(".schemeBox").textContent).toContain("மாதம் ₹1,200");
    expect(document.querySelector(".docs").textContent).toContain("ஆதார் அட்டை");
  });

  it("a woman who is too young is told how long to wait, honestly", async () => {
    const user = userEvent.setup();
    render(<App />);
    await user.click(screen.getByText("தொடங்குங்கள்", { exact: false }));
    await user.click(await screen.findByText("எனக்குத் திருமணம் ஆகவில்லை", { selector: ".cLabel" }));
    await screen.findByText("வயது");
    for (let i = 0; i < 2; i++) await user.click(screen.getByLabelText("+5"));   // 40 -> 50 ... then back below
    await user.click(screen.getByLabelText("-5"));                               // 45
    await user.click(screen.getByText("சரி", { exact: false, selector: ".primary" }));
    await screen.findByText("இப்போது தகுதி இல்லை");
    expect(screen.getByText(/இன்னும் 5 ஆண்டுகளில்/)).toBeTruthy();
  });
});
