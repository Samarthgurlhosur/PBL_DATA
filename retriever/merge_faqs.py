import os
import json
import re

DATA_DIR = "data"


# ---------------------- HELPERS ----------------------

def load_json(path):
    if not os.path.exists(path):
        print(f"[WARN] File not found: {path}")
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[ERROR] Failed to load {path}: {e}")
        return []


def clean(text):
    if not isinstance(text, str):
        return ""
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def normalize_faq(faq):
    """Ensure each FAQ has the same clean structure"""
    return {
        "question": clean(faq.get("question", "")),
        "answer": clean(faq.get("answer", "")),
        "source": faq.get("source", "unknown")
    }


def faq_key(faq):
    """Used to detect duplicates"""
    q = clean(faq.get("question", "").lower())
    return q


# ---------------------- MAIN FUNCTION ----------------------

def merge_faqs():
    print("\n============================")
    print("   MERGING FAQ DATA FILES   ")
    print("============================\n")

    # Load manual and generated FAQ files
    manual_faqs = load_json(os.path.join(DATA_DIR, "faqs.json"))
    generated_faqs = load_json(os.path.join(DATA_DIR, "faqs_generated.json"))

    all_faqs = []

    # Normalize manual FAQs
    for item in manual_faqs:
        all_faqs.append(normalize_faq(item))

    # Normalize auto-generated FAQs
    for item in generated_faqs:
        all_faqs.append(normalize_faq(item))

    # Remove duplicates
    seen = set()
    unique_faqs = []

    for faq in all_faqs:
        key = faq_key(faq)
        if key not in seen:
            seen.add(key)
            unique_faqs.append(faq)

    # Save merged output
    output_path = os.path.join(DATA_DIR, "faqs_final.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(unique_faqs, f, indent=2, ensure_ascii=False)

    print(f"[DONE] Final FAQ file saved → {output_path}")
    print(f"[COUNT] Total FAQs in final dataset: {len(unique_faqs)}")
    print("\nUse faqs_final.json in your chatbot now!\n")


# ---------------------- RUN DIRECTLY ----------------------

if __name__ == "__main__":
    merge_faqs()
