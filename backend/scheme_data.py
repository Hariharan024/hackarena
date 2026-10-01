"""Verified scheme data - the ONLY source of scheme facts in Sakhi.

Gemini never supplies or rewrites anything in this file.

Verified against the Tamil Nadu Commissionerate of Revenue Administration:
  - eligibility: https://www.cra.tn.gov.in/eleg_schemes.php
  - amount:      https://www.cra.tn.gov.in/about_schemes.php
                 (Rs.1,200/month for all non-disability pension schemes from Aug 2023)
Re-check both pages before every public demo. Amounts can change with a new government order.
"""

LAST_VERIFIED = "2026-10-01"
ASSET_LIMIT_RUPEES = 100000  # "Fixed assets not exceeding Rs.1,00,000"; waived if a free govt house was assigned

# key -> localized label + icon. Keys are what the API and the frontend use.
DOCUMENTS = {
    "aadhaar": {"ta": "ஆதார் அட்டை", "en": "Aadhaar card", "icon": "🪪"},
    "bank_passbook": {"ta": "வங்கிக் கணக்குப் புத்தகம்", "en": "Bank passbook", "icon": "🏦"},
    "address_proof": {"ta": "குடும்ப அட்டை அல்லது முகவரிச் சான்று", "en": "Ration/smart card or address proof", "icon": "🏠"},
    "photo": {"ta": "புகைப்படம்", "en": "Passport-size photo", "icon": "📷"},
    "identity_proof": {"ta": "அடையாளச் சான்று", "en": "Identity proof", "icon": "🆔"},
    "death_certificate": {"ta": "கணவரின் இறப்புச் சான்றிதழ்", "en": "Husband's death certificate", "icon": "📄"},
    "widow_certificate": {"ta": "கணவனை இழந்தோர் சான்றிதழ்", "en": "Widow certificate", "icon": "📄"},
    "court_order": {"ta": "நீதிமன்ற உத்தரவு (இருந்தால்)", "en": "Court order (if you have one)", "icon": "⚖️"},
    "aadhaar_consent": {"ta": "ஆதார் ஒப்புதல் படிவம்", "en": "Aadhaar consent form", "icon": "✍️"},
    "self_declaration": {"ta": "சுய உறுதிமொழி", "en": "Self-declaration", "icon": "📝"},
}

SOURCES = {
    "eligibility": {
        "title": {"ta": "தமிழ்நாடு வருவாய் நிர்வாகம் - தகுதி விதிகள்", "en": "Tamil Nadu Revenue Administration - eligibility"},
        "url": "https://www.cra.tn.gov.in/eleg_schemes.php",
    },
    "amount": {
        "title": {"ta": "தமிழ்நாடு வருவாய் நிர்வாகம் - ஓய்வூதியத் தொகை", "en": "Tamil Nadu Revenue Administration - pension amounts"},
        "url": "https://www.cra.tn.gov.in/about_schemes.php",
    },
    "esevai": {
        "title": {"ta": "தமிழ்நாடு இ-சேவை", "en": "Tamil Nadu e-Sevai"},
        "url": "https://tnesevai.tn.gov.in/Pages/ServiceList.aspx",
    },
}

SCHEMES = {
    "dwps": {
        "id": "dwps",
        "name": {"ta": "ஆதரவற்ற விதவை ஓய்வூதியத் திட்டம்", "en": "Destitute Widow Pension Scheme"},
        "short": {"ta": "விதவை ஓய்வூதியம்", "en": "Widow pension"},
        "amount": 1200,
        "marital_status": ["widow"],
        "age_min": 18,
        "deserted_years_min": None,
        "documents": ["aadhaar", "bank_passbook", "address_proof", "photo", "identity_proof",
                      "death_certificate", "widow_certificate", "aadhaar_consent", "self_declaration"],
    },
    "ddwps": {
        "id": "ddwps",
        "name": {"ta": "ஆதரவற்ற / கைவிடப்பட்ட பெண்கள் ஓய்வூதியத் திட்டம்", "en": "Destitute / Deserted Wives Pension Scheme"},
        "short": {"ta": "கைவிடப்பட்ட பெண்கள் ஓய்வூதியம்", "en": "Deserted wives pension"},
        "amount": 1200,
        # Official rule: legally divorced, OR deserted >= 5 years, OR has a court legal-separation certificate.
        "marital_status": ["deserted", "divorced"],
        "age_min": 30,
        "deserted_years_min": 5,  # applies to "deserted" only
        "documents": ["aadhaar", "bank_passbook", "address_proof", "photo", "identity_proof",
                      "court_order", "aadhaar_consent", "self_declaration"],
    },
    "uwps": {
        "id": "uwps",
        "name": {"ta": "50 வயதுக்கு மேற்பட்ட ஏழை திருமணமாகாத பெண்களுக்கான ஓய்வூதியம்", "en": "Pension to Poor Unmarried Women aged 50+"},
        "short": {"ta": "திருமணமாகாத பெண்கள் ஓய்வூதியம்", "en": "Unmarried women pension"},
        "amount": 1200,
        "marital_status": ["unmarried"],
        "age_min": 50,
        "deserted_years_min": None,
        "documents": ["aadhaar", "bank_passbook", "address_proof", "photo", "identity_proof",
                      "aadhaar_consent", "self_declaration"],
    },
}

SCHEME_FOR_STATUS = {
    "widow": "dwps",
    "deserted": "ddwps",
    "divorced": "ddwps",
    "unmarried": "uwps",
}
