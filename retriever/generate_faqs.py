import os
import json
import re

DATA_DIR = "data"


# ---------------------- HELPERS ----------------------

def load_json(path):
    if not os.path.exists(path):
        print(f"[WARN] File not found: {path}")
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[ERROR] Failed to load {path}: {e}")
        return None


def clean(text):
    if not isinstance(text, str):
        return ""
    text = re.sub(r"\s+", " ", text)
    return text.strip()


# ---------------------- FAQ GENERATORS ----------------------

def faq_from_programs(programs):
    faqs = []

    for item in programs:
        program = clean(item.get("program_name", ""))
        faculty = clean(item.get("faculty", ""))

        if program:
            faqs.append({
                "question": f"What programs are offered under {faculty}?",
                "answer": f"{program} is offered under {faculty} at GM University.",
                "source": "programs"
            })

    return faqs


def faq_from_academic_assessment(assessment_list):
    faqs = []

    for item in assessment_list:
        text = clean(item.get("content", ""))
        if not text:
            continue

        faqs.append({
            "question": "How does GMU conduct academic assessments?",
            "answer": text,
            "source": "academic_assessment"
        })

    return faqs


def faq_from_program_fee(fee_list):
    faqs = []

    for item in fee_list:
        text = clean(item.get("content", ""))
        if not text:
            continue

        faqs.append({
            "question": "What is the fee structure of GM University?",
            "answer": text,
            "source": "program_fee"
        })

    return faqs


def faq_from_contacts(contacts):
    faqs = []

    for item in contacts:
        text = clean(item.get("raw_text", ""))
        if not text:
            continue

        faqs.append({
            "question": "How can I contact GM University?",
            "answer": text,
            "source": "contact"
        })

    return faqs


def faq_from_faculty(faculty_list):
    faqs = []

    for item in faculty_list:
        dept = clean(item.get("department", ""))
        details = clean(item.get("details", ""))

        if dept and details:
            faqs.append({
                "question": f"Who are the faculty in the {dept} department?",
                "answer": f"{details}",
                "source": "faculty"
            })

    return faqs


def faq_from_governance(gov_list):
    faqs = []

    for item in gov_list:
        cols = item.get("columns", [])
        if len(cols) >= 2:
            faqs.append({
                "question": f"What governance details are available at GMU?",
                "answer": " | ".join(cols),
                "source": "governance"
            })

    return faqs


def faq_from_phd_supervisors(phd_list):
    faqs = []

    for item in phd_list:
        cols = item.get("columns", [])
        if len(cols) >= 2:
            faqs.append({
                "question": "Who are the PhD supervisors at GMU?",
                "answer": " | ".join(cols),
                "source": "phd_supervisors"
            })

    return faqs


# ---------------------- MASTER FUNCTION ----------------------

def generate_faqs():
    print("\n============================")
    print("  GENERATING AUTOMATIC FAQS")
    print("============================\n")

    cleaned_path = os.path.join(DATA_DIR, "cleaned_data.json")
    cleaned_data = load_json(cleaned_path)

    if not cleaned_data:
        print("[ERROR] cleaned_data.json missing. Run clean_dataset.py first.")
        return

    # Extract sections
    programs = cleaned_data.get("programs", [])
    academic_assessment = cleaned_data.get("academic_assessment", [])
    program_fee = cleaned_data.get("program_fee", [])
    contacts = cleaned_data.get("contacts", [])
    faculty = cleaned_data.get("faculty", [])
    governance = cleaned_data.get("governance", [])
    phd_supervisors = cleaned_data.get("phd_supervisors", [])

    faqs = []

    # Generate section-wise FAQs
    faqs.extend(faq_from_programs(programs))
    faqs.extend(faq_from_academic_assessment(academic_assessment))
    faqs.extend(faq_from_program_fee(program_fee))
    faqs.extend(faq_from_contacts(contacts))
    faqs.extend(faq_from_faculty(faculty))
    faqs.extend(faq_from_governance(governance))
    faqs.extend(faq_from_phd_supervisors(phd_supervisors))

    # Save output
    output_path = os.path.join(DATA_DIR, "faqs_generated.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(faqs, f, indent=2, ensure_ascii=False)

    print(f"[DONE] FAQs generated → {output_path}")
    print(f"[COUNT] Total FAQs created: {len(faqs)}")


# ---------------------- RUN DIRECTLY ----------------------

if __name__ == "__main__":
    generate_faqs()
