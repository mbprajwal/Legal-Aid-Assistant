# DOCUMENT_KEYWORDS = {
#     "fir": "fir",
#     "file fir": "fir",
#     "draft fir": "fir",
#     "write fir": "fir",

#     "rti": "rti",
#     "rti application": "rti",
#     "file rti": "rti",

#     "legal notice": "legal_notice",
#     "notice": "legal_notice",

#     "police complaint": "complaint",
#     "write complaint": "complaint",

#     "tenant": "tenancy_complaint",
#     "landlord": "tenancy_complaint",
#     "rent dispute": "tenancy_complaint",

#     "income certificate": "income_certificate",
#     "income proof": "income_certificate",

#     "caste certificate": "caste_certificate",
#     "caste proof": "caste_certificate"
# }

# def detect_document_intent(text: str):
#     text = text.lower()
#     for key, template in DOCUMENT_KEYWORDS.items():
#         if key in text:
#             return template
#     return None

import re

DOCUMENT_KEYWORDS = {
    "fir": "fir_template",
    "rti": "rti_template",
    "legal notice": "legal_notice_template",
    "notice": "legal_notice_template",
    "complaint": "complaint_template",
}

ACTION_WORDS = [
    r"write",
    r"draft",
    r"prepare",
    r"generate",
    r"create",
    r"make",
    r"build",
    r"fill",
]

def detect_document_intent(query):
    q = query.lower()

    # condition 1: detect document type
    doc_type = None
    for word, template in DOCUMENT_KEYWORDS.items():
        if word in q:
            doc_type = template
            break

    if not doc_type:
        return None  # no document keywords at all

    # condition 2: detect user intention to generate document
    action_present = any(re.search(a, q) for a in ACTION_WORDS)

    if not action_present:
        return None  # user is NOT explicitly asking to create the document

    return doc_type
