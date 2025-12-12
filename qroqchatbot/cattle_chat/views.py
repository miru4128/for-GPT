# views.py
import os
import json
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.shortcuts import render

def chat_page(request):
    return render(request, "cattle_chat/chat.html")

# Choose either the embedding filter or keyword filter
from .embedding_filter import is_cattle_related as embedding_is_cattle

# from .keyword_filter import is_cattle_related as keyword_is_cattle 

# Groq client
from groq import Groq
GROQ_CLIENT = Groq(api_key=settings.GROQ_API_KEY)

SYSTEM_PROMPT = (
    "You are an expert in cattle management (nutrition, health, milk production, housing, breeding, "
    "and veterinary care). ONLY answer cattle-related queries. Respond clearly and concisely in Markdown. "
    "Structure answers with: 1) a one-line SUMMARY (bold) at the top, 2) short paragraphs, 3) bullet lists for steps "
    "or recommendations, and 4) a short PRACTICAL STEPS section when applicable. "
    "Use headings (##) and bullet points. If the user asks something outside cattle topics, reply: "
    "'I can only answer cattle-related queries.'"
)


@csrf_exempt
def chat_api(request):
    """
    POST JSON: {"message": "user text"}
    Response JSON: {"ok": True, "answer": "...", "score": 0.78}
    """
    if request.method != "POST":
        return HttpResponseBadRequest("Use POST.")

    try:
        data = json.loads(request.body)
        user_text = data.get("message", "").strip()
    except Exception:
        return HttpResponseBadRequest("Invalid JSON.")

    if not user_text:
        return JsonResponse({"ok": False, "error": "Empty message"}, status=400)

    # Check cattle-related using embedding filter
    related, score = embedding_is_cattle(user_text)  # returns (bool,score)
    if not related:
        return JsonResponse({
            "ok": False,
            "error": "non_cattle",
            "message": "I can only answer cattle-related queries. Please ask about cattle health, milk production, nutrition, or veterinary care.",
            "score": score
        }, status=200)

    # Build chat request (non-streaming for simplicity)
    try:
        completion = GROQ_CLIENT.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_text}
            ],
            stream=False  # synchronous
        )
        # The Groq SDK response shape may vary; adapt as needed. We'll assume completion.choices[0].message.content style.
        # If response shape is different, inspect completion in debugging prints.
        answer = ""
        # try common response formats:
        if hasattr(completion, "choices"):
            # e.g. completion.choices[0].message.content
            try:
                answer = completion.choices[0].message.content
            except Exception:
                # fallback: parse raw
                answer = str(completion)
        else:
            answer = str(completion)

        return JsonResponse({"ok": True, "answer": answer, "score": score})
    except Exception as e:
        return JsonResponse({"ok": False, "error": "model_error", "message": str(e)}, status=500)
