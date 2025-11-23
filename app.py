import os
import json
import datetime

from dotenv import load_dotenv
from flask import Flask, request, jsonify, render_template
from groq import Groq

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# ----------------- ENV & CLIENT -----------------

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise RuntimeError("GROQ_API_KEY missing in .env")

client = Groq(api_key=GROQ_API_KEY)


# ----------------- FLASK APP -----------------

app = Flask(__name__)


# ----------------- LOAD DATA -----------------

DATA_PATH = os.path.join("data", "faqs_final.json")

if not os.path.exists(DATA_PATH):
    raise FileNotFoundError("faqs_final.json missing")

FAQ_DATA = json.load(open(DATA_PATH, "r", encoding="utf-8"))

QUESTIONS = [x["question"] for x in FAQ_DATA]
ANSWERS = [x["answer"] for x in FAQ_DATA]

VECTORIZER = TfidfVectorizer(stop_words="english")
QUESTION_VECTORS = VECTORIZER.fit_transform(QUESTIONS)

SIMILARITY_THRESHOLD = 0.25


# ----------------- RETRIEVAL -----------------

def retrieve_relevant_answers(user_query, top_k=3):
    if not user_query.strip():
        return []

    user_vec = VECTORIZER.transform([user_query])
    sims = cosine_similarity(user_vec, QUESTION_VECTORS)[0]

    top_indices = sims.argsort()[::-1][:top_k]

    results = []
    for idx in top_indices:
        score = float(sims[idx])
        if score > 0:
            results.append({
                "question": QUESTIONS[idx],
                "answer": ANSWERS[idx],
                "score": score
            })
    return results


# ----------------- GROQ (LLM CALL) -----------------

def groq_chat(messages):
    """Return Llama output text."""
    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=messages,
        temperature=0.7,
        max_tokens=500
    )
    return completion.choices[0].message.content  # FIXED!


# ----------------- GMU ANSWER WITH CONTEXT -----------------

def answer_with_context(user_query, retrieved):
    context = "\n\n".join(
        [f"Q: {x['question']}\nA: {x['answer']}" for x in retrieved]
    )

    system_message = (
        "You are a friendly but professional human-like assistant with humurous touch of comedy for GM University (GMU). "
        "Use ONLY the provided context for GMU-specific facts. "
        "Keep the tone natural and smooth,make sure you keep the talk humurous(use emojis) ."
    )

    user_prompt = f"""
User question:
{user_query}

GMU Context:
{context}

Answer naturally and clearly using only this information.
"""

    return groq_chat([
        {"role": "system", "content": system_message},
        {"role": "user", "content": user_prompt},
    ])


# ----------------- GENERAL ANSWER WHEN NO CONTEXT -----------------

def answer_without_context(user_query):
    system_message = (
        "You are a helpful, friendly, professional GM University (GMU) assistant. "
        "If the question requires exact GMU facts you don’t know, give a general explanation "
        "and politely recommend checking the official GMU website. "
        "Always speak in a natural, human-like tone , make sure you keep it humurous of comedy use emojis  ."
    )

    return groq_chat([
        {"role": "system", "content": system_message},
        {"role": "user", "content": user_query},
    ])


# ----------------- HYBRID LOGIC -----------------

def generate_hybrid_response(user_query, retrieved):
    if retrieved and retrieved[0]["score"] >= SIMILARITY_THRESHOLD:
        return answer_with_context(user_query, retrieved)

    return answer_without_context(user_query)


# ----------------- LOGGING -----------------

def log_chat(user, bot):
    os.makedirs("logs", exist_ok=True)
    path = "logs/chat_logs.json"

    entry = {
        "timestamp": datetime.datetime.now().isoformat(),
        "user": user,
        "bot": bot
    }

    logs = []
    if os.path.exists(path):
        try:
            logs = json.load(open(path, "r", encoding="utf-8"))
        except:
            logs = []

    logs.append(entry)
    json.dump(logs, open(path, "w", encoding="utf-8"), indent=2)


# ----------------- ROUTES -----------------

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(force=True)
    message = data.get("message", "").strip()

    if not message:
        return jsonify({"reply": "Please type something so I can help you."})

    retrieved = retrieve_relevant_answers(message)

    reply = generate_hybrid_response(message, retrieved)
    log_chat(message, reply)

    return jsonify({"reply": reply})


# ----------------- RUN -----------------

if __name__ == "__main__":
    app.run(debug=True)
