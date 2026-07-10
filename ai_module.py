import re

def find_responsible_person(sentence):
    patterns = [
        r'The\s+([A-Za-z\s]+?)\s+(?:must|shall|should|is responsible for|will)',
        r'([A-Za-z\s]+?)\s+(?:must|shall|should|is responsible for|will)'
    ]

    for pattern in patterns:
        match = re.search(pattern, sentence, re.IGNORECASE)
        if match:
            person = match.group(1).strip()
            return person

    return "Not specified"


def extract_obligations(contract_text):
    obligations = []

    date_pattern = r'\b\d{1,2}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}\b'
    dates = re.findall(date_pattern, contract_text)

    payment_date = dates[0] if len(dates) > 0 else "Not found"
    renewal_date = dates[1] if len(dates) > 1 else "Not found"

    sentences = re.split(r'[.!?]', contract_text)

    for sentence in sentences:
        text = sentence.lower()

        if "payment" in text or "pay" in text:
            obligations.append({
                "type": "Payment",
                "due_date": payment_date,
                "responsible_person": find_responsible_person(sentence),
                "risk": "Medium",
                "summary": "Payment must be completed before due date."
            })

        if "renew" in text:
            obligations.append({
                "type": "Renewal",
                "due_date": renewal_date,
                "responsible_person": find_responsible_person(sentence),
                "risk": "High",
                "summary": "Contract renewal requires attention."
            })

        if "notice" in text:
            obligations.append({
                "type": "Notice Period",
                "due_date": "30 days notice",
                "responsible_person": find_responsible_person(sentence),
                "risk": "Medium",
                "summary": "Termination requires advance notice."
            })

    return obligations