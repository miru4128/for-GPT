# keyword_filter.py
ALLOWED_KEYWORDS = [
    "cow", "cattle", "buffalo", "livestock", "dairy",
    "milk", "fodder", "feed", "veterinary", "vet", "doctor",
    "disease", "mastitis", "nutrition", "silage", "hay",
    "weather", "temperature", "heat stress", "breeding",
    "insemination", "calf", "calves", "udder", "milk yield", "milk production"
]

def is_cattle_related(query: str):
    q = query.lower()
    return any(k in q for k in ALLOWED_KEYWORDS)
