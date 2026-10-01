"""All user-facing words. Simple spoken Tamil first, English second.

Have a native Tamil speaker review the Tamil strings before a public launch.
"""

STATUS_OPTIONS = [
    {"value": "widow", "icon": "🕯️", "label": {"ta": "கணவர் இறந்துவிட்டார்", "en": "My husband passed away"}},
    {"value": "deserted", "icon": "🚪", "label": {"ta": "கணவர் என்னை விட்டுப் பிரிந்துவிட்டார்", "en": "My husband left me"}},
    {"value": "divorced", "icon": "⚖️", "label": {"ta": "விவாகரத்து அல்லது நீதிமன்றப் பிரிவு", "en": "Divorced or court-separated"}},
    {"value": "unmarried", "icon": "👩", "label": {"ta": "எனக்குத் திருமணம் ஆகவில்லை", "en": "I never married"}},
    {"value": "married", "icon": "🏠", "label": {"ta": "கணவருடன் வாழ்கிறேன்", "en": "I live with my husband"}},
]

M = {
    "welcome": {
        "ta": "வணக்கம்! நான் சகி. அரசு மாத ஓய்வூதியம் உங்களுக்குக் கிடைக்குமா என்று பார்க்கலாம். உங்கள் நிலைமை என்ன? பேசுங்கள், அல்லது ஒரு படத்தைத் தொடுங்கள்.",
        "en": "Hello! I am Sakhi. Let us see if you can get a monthly government pension. What is your situation? Speak, or touch a picture.",
    },
    "ask_situation": {
        "ta": "உங்கள் நிலைமை என்ன? பேசுங்கள், அல்லது ஒரு படத்தைத் தொடுங்கள்.",
        "en": "What is your situation? Speak, or touch a picture.",
    },
    "ask_age": {
        "ta": "உங்களுக்கு எத்தனை வயது? சொல்லுங்கள், அல்லது பொத்தான்களால் தேர்ந்தெடுங்கள்.",
        "en": "How old are you? Say it, or choose with the buttons.",
    },
    "ask_years": {
        "ta": "உங்கள் கணவர் உங்களை விட்டுப் பிரிந்து எத்தனை ஆண்டுகள் ஆகின்றன?",
        "en": "How many years has it been since your husband left you?",
    },
    "ask_assets": {
        "ta": "உங்களிடம் ஒரு லட்சம் ரூபாய்க்கு மேல் மதிப்புள்ள நிலம், வீடு அல்லது சொத்து இருக்கிறதா? அரசு இலவசமாகக் கொடுத்த வீடு கணக்கில் வராது.",
        "en": "Do you own land, a house or property worth more than one lakh rupees? A free house given by the government does not count.",
    },
    "ack": {"ta": "சரி.", "en": "Okay."},
    "not_understood": {
        "ta": "மன்னிக்கவும், எனக்குப் புரியவில்லை.",
        "en": "Sorry, I did not understand.",
    },
    "married": {
        "ta": "இந்த ஓய்வூதியங்கள் கணவரின் ஆதரவு இல்லாத பெண்களுக்கானவை. வேறு அரசு உதவிகள் பற்றி அருகிலுள்ள இ-சேவை மையத்தில் கேளுங்கள்.",
        "en": "These pensions are for women who do not have a husband's support. Ask at your nearest e-Sevai centre about other government help.",
    },
    "match": {
        "ta": "நல்ல செய்தி! {scheme} உங்களுக்குக் கிடைக்கலாம். மாதம் {amount} ரூபாய். இறுதி முடிவை அரசு அதிகாரிகள் எடுப்பார்கள். இந்த ஆவணங்களைத் தயார் செய்து, அருகிலுள்ள இ-சேவை மையத்திற்குச் செல்லுங்கள்.",
        "en": "Good news! You may get the {scheme}. It is {amount} rupees a month. The government officer makes the final decision. Get these documents ready and go to your nearest e-Sevai centre.",
    },
    "not_age": {
        "ta": "மன்னிக்கவும், இந்தத் திட்டத்திற்குக் குறைந்தது {min} வயது வேண்டும். இன்னும் {n} ஆண்டுகளில் நீங்கள் விண்ணப்பிக்கலாம்.",
        "en": "Sorry, this scheme needs you to be at least {min} years old. You can apply in {n} years.",
    },
    "not_years": {
        "ta": "கணவர் பிரிந்து குறைந்தது {min} ஆண்டுகள் ஆக வேண்டும். ஆனால் நீதிமன்றத்தின் பிரிவுச் சான்றிதழ் அல்லது விவாகரத்து இருந்தால் இப்போதே விண்ணப்பிக்கலாம். இ-சேவை மையத்தில் கேளுங்கள்.",
        "en": "Your husband must have left at least {min} years ago. But if you have a court separation certificate or a divorce, you can apply now. Ask at the e-Sevai centre.",
    },
    "not_assets": {
        "ta": "ஒரு லட்சம் ரூபாய்க்கு மேல் சொத்து இருந்தால் இந்த ஓய்வூதியம் பொதுவாகக் கிடைக்காது. ஆனால் மதிப்பை அதிகாரிகள் பார்த்து முடிவு செய்வார்கள். சந்தேகம் இருந்தால் இ-சேவை மையத்தில் கேளுங்கள்.",
        "en": "With property worth more than one lakh rupees, this pension is usually not given. But the officer checks the value and decides. If unsure, ask at the e-Sevai centre.",
    },
    "headline_match": {"ta": "நீங்கள் விண்ணப்பிக்கலாம்", "en": "You can apply"},
    "headline_no": {"ta": "இப்போது தகுதி இல்லை", "en": "Not eligible right now"},
    "headline_na": {"ta": "இந்தத் திட்டம் பொருந்தாது", "en": "This scheme does not apply"},
    "step1": {"ta": "இந்த ஆவணங்களைத் தயார் செய்யுங்கள்", "en": "Get these documents ready"},
    "step2": {"ta": "அருகிலுள்ள இ-சேவை மையத்திற்குச் செல்லுங்கள்", "en": "Go to your nearest e-Sevai centre"},
    "step3": {"ta": "இந்தத் தாளைக் காட்டுங்கள். அதிகாரிகள் உங்கள் தகுதியை உறுதிசெய்வார்கள்", "en": "Show this page. The officer will confirm your eligibility"},
    "amount_per_month": {"ta": "மாதம் ₹{amount}", "en": "₹{amount} per month"},
    "share_title": {"ta": "சகி - எனக்கான ஓய்வூதிய வழிகாட்டி", "en": "Sakhi - my pension guide"},
    "share_docs": {"ta": "தேவையான ஆவணங்கள்:", "en": "Documents needed:"},
    "share_go": {"ta": "அருகிலுள்ள இ-சேவை மையத்திற்குச் செல்லுங்கள். இறுதி முடிவு அரசு அதிகாரிகளுடையது.", "en": "Go to your nearest e-Sevai centre. The final decision is made by government officers."},
}

CHIP = {
    "age": {"ta": "{v} வயது", "en": "{v} years old"},
    "years": {"ta": "{v} ஆண்டுகள் ஆகிறது", "en": "{v} years since he left"},
    "assets_no": {"ta": "சொத்து: ₹1 லட்சத்துக்கு குறைவு", "en": "Property: under ₹1 lakh"},
    "assets_yes": {"ta": "சொத்து: ₹1 லட்சத்துக்கு மேல்", "en": "Property: over ₹1 lakh"},
}


def t(key: str, lang: str, **kw) -> str:
    return M[key][lang].format(**kw) if kw else M[key][lang]
