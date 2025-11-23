import os
import json
import re

DATA_DIR = "data"


# --------------------- HELPER FUNCTIONS ---------------------

def load_json(path):
    """Load JSON safely."""
    if not os.path.exists(path):
        print(f"[WARN] File not found: {path}")
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[ERROR] Failed to load {path}: {e}")
        return []


def clean_text(text):
    """Clean unwanted characters, newlines, spacing."""
    if not isinstance(text, str):
        return text

    text = text.replace("\n", " ")
    text = re.sub(r"\s+", " ", text)
    text = text.strip()
    return text


def dedupe_list(items):
    """Remove duplicate dictionaries based on string value."""
    seen = set()
    unique = []

    for item in items:
        key = json.dumps(item, sort_keys=True)
        if key not in seen:
            seen.add(key)
            unique.append(item)

    return unique


# --------------------- MAIN CLEANING PROCESS ---------------------

def clean_dataset():
    print("\n============================")
    print(" CLEANING SCRAPED GMU DATA ")
    print("============================\n")

    # ------------------ Load All Scraped Files ------------------

    programs = load_json(os.path.join(DATA_DIR, "programs.json"))
    academic_assessment = load_json(os.path.join(DATA_DIR, "academic_assessment.json"))
    program_fee = load_json(os.path.join(DATA_DIR, "program_fee.json"))
    contacts = load_json(os.path.join(DATA_DIR, "contacts.json"))
    faculty = load_json(os.path.join(DATA_DIR, "faculty.json"))
    governance = load_json(os.path.join(DATA_DIR, "governance.json"))
    phd_supervisors = load_json(os.path.join(DATA_DIR, "phd_supervisors.json"))

    # ------------------ Clean Programs ------------------

    for p in programs:
        p["faculty"] = clean_text(p.get("faculty", ""))
        p["program_name"] = clean_text(p.get("program_name", ""))
        p["source_url"] = clean_text(p.get("source_url", ""))

    programs = dedupe_list(programs)

    # ------------------ Clean Academic Assessment ------------------

    for a in academic_assessment:
        a["content"] = clean_text(a.get("content", ""))
        a["source_url"] = clean_text(a.get("source_url", ""))

    # ------------------ Clean Program Fee ------------------

    for f in program_fee:
        f["content"] = clean_text(f.get("content", ""))
        f["source_url"] = clean_text(f.get("source_url", ""))

    # ------------------ Clean Contacts ------------------

    if isinstance(contacts, dict):
        contacts = [contacts]  # make it list for consistency

    for c in contacts:
        c["raw_text"] = clean_text(c.get("raw_text", ""))
        c["source_url"] = clean_text(c.get("source_url", ""))

    # ------------------ Clean Faculty ------------------

    for fac in faculty:
        fac["department"] = clean_text(fac.get("department", ""))
        fac["details"] = clean_text(fac.get("details", ""))
        fac["source_url"] = clean_text(fac.get("source_url", ""))

    faculty = dedupe_list(faculty)

    # ------------------ Clean Governance / RIC ------------------

    for g in governance:
        g["columns"] = [clean_text(x) for x in g.get("columns", [])]
        g["source_url"] = clean_text(g.get("source_url", ""))

    governance = dedupe_list(governance)

    # ------------------ Clean PhD Supervisors ------------------

    for s in phd_supervisors:
        s["columns"] = [clean_text(x) for x in s.get("columns", [])]
        s["source_url"] = clean_text(s.get("source_url", ""))

    phd_supervisors = dedupe_list(phd_supervisors)

    # ------------------ Merge Everything ------------------

    cleaned_dataset = {
        "programs": programs,
        "academic_assessment": academic_assessment,
        "program_fee": program_fee,
        "contacts": contacts,
        "faculty": faculty,
        "governance": governance,
        "phd_supervisors": phd_supervisors,
    }

    # ------------------ Save Cleaned Output ------------------

    output_path = os.path.join(DATA_DIR, "cleaned_data.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(cleaned_dataset, f, indent=2, ensure_ascii=False)

    print("[DONE] Cleaned dataset saved → data/cleaned_data.json\n")


# --------------------- RUN DIRECTLY ---------------------

if __name__ == "__main__":
    clean_dataset()
