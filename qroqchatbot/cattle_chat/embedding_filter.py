# embedding_filter.py
from sentence_transformers import SentenceTransformer, util
import numpy as np
from django.conf import settings

# load a small but good model (downloads on first run)
MODEL_NAME = "all-MiniLM-L6-v2"  # fast and accurate for semantic similarity
_model = None
_topic_embeddings = None

CATTLE_TOPIC_PROMPTS = [
    "cattle health and disease",
    "cow nutrition and feed",
    "buffalo milk production",
    "livestock housing and infrastructure",
    "veterinary support for cattle",
    "breeding and artificial insemination for cows",
    "mastitis in dairy cows",
    "calf care and management",
    "fodder and silage for cattle",
    "weather effects on dairy cattle",
    "dairy farm management"
]

def _load_model():
    global _model, _topic_embeddings
    if _model is None:
        _model = SentenceTransformer(MODEL_NAME)
    if _topic_embeddings is None:
        _topic_embeddings = _model.encode(CATTLE_TOPIC_PROMPTS, convert_to_tensor=True)
    return _model, _topic_embeddings

def is_cattle_related(query, threshold=None):
    """
    Returns (bool, score). True if semantically related to cattle topics.
    """
    model, topic_emb = _load_model()
    q_emb = model.encode(query, convert_to_tensor=True)
    # compute cosine similarities with all topic prompts
    scores = util.cos_sim(q_emb, topic_emb)[0].cpu().numpy()
    best = float(np.max(scores))
    if threshold is None:
        threshold = getattr(settings, "ALLOWED_SIMILARITY", 0.65)
    return best >= threshold, best
