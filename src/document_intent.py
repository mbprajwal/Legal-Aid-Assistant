DOCUMENT_KEYWORDS = {
    "fir": "fir",
    "file fir": "fir",
    "draft fir": "fir",
    "write fir": "fir",

    "rti": "rti",
    "rti application": "rti",
    "file rti": "rti",

    "legal notice": "legal_notice",
    "notice": "legal_notice",

    "police complaint": "complaint",
    "write complaint": "complaint",

    "tenant": "tenancy_complaint",
    "landlord": "tenancy_complaint",
    "rent dispute": "tenancy_complaint",

    "income certificate": "income_certificate",
    "income proof": "income_certificate",

    "caste certificate": "caste_certificate",
    "caste proof": "caste_certificate"
}

def detect_document_intent(text: str):
    text = text.lower()
    for key, template in DOCUMENT_KEYWORDS.items():
        if key in text:
            return template
    return None
