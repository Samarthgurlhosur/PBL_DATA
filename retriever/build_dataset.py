import os
import json
import time
import requests
from bs4 import BeautifulSoup

BASE = "https://gmu.ac.in"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (GMU-Chatbot-Scraper; +https://gmu.ac.in)"
}

DATA_DIR = "data"
RAW_DIR = os.path.join(DATA_DIR, "raw_scraped")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(RAW_DIR, exist_ok=True)


# ------------------------------ HELPER FUNCTIONS ------------------------------

def fetch_page(url):
    """Download a page and return a BeautifulSoup object."""
    print(f"[FETCH] {url}")

    try:
        res = requests.get(url, headers=HEADERS, timeout=15)
        res.raise_for_status()
        return BeautifulSoup(res.text, "lxml")
    except Exception as e:
        print(f"[ERROR] Failed to fetch {url}: {e}")
        return None


def save_json(filename, data):
    path = os.path.join(DATA_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"[SAVED] {path} ({len(data)} records)")


# ------------------------------ SCRAPE PROGRAM TABLE ------------------------------

def parse_program_table(url, faculty_name):
    """Extract program names from a typical HTML table of GMU."""
    soup = fetch_page(url)
    if soup is None:
        return []

    table = soup.find("table")
    if not table:
        print(f"[WARN] No table found at {url}")
        return []

    rows = table.find_all("tr")
    programs = []

    for row in rows[1:]:  # skip header
        cols = [td.get_text(strip=True) for td in row.find_all("td")]
        if not cols:
            continue

        programs.append({
            "faculty": faculty_name,
            "program_name": cols[1] if len(cols) > 1 else "",
            "raw_columns": cols,
            "source_url": url
        })

    return programs


# ------------------------------ SCRAPE FACULTY LIST ------------------------------

def parse_faculty_page(url, dept_name):
    """Extract faculty names & details."""
    soup = fetch_page(url)
    if soup is None:
        return []

    faculty_entries = []

    # GMU typically uses simple <li> or <p> or card-grid structures. Adjust after inspecting.
    items = soup.find_all(["li", "p", "div"])

    for item in items:
        text = item.get_text(" ", strip=True)
        if not text:
            continue

        # A simple heuristic: look for names with "Dr" or capital letters
        if "Dr" in text or "Professor" in text or "Coordinator" in text:
            faculty_entries.append({
                "department": dept_name,
                "details": text,
                "source_url": url
            })

    return faculty_entries


# ----------------- SCRAPE RIC / GOVERNANCE -----------------

def parse_table_generic(url):
    """Extract any table-based page like Research Council or PhD Supervisors."""
    soup = fetch_page(url)
    if soup is None:
        return []

    table = soup.find("table")
    if not table:
        print(f"[WARN] No table found at: {url}")
        return []

    rows = table.find_all("tr")
    entries = []

    for row in rows[1:]:
        cols = [td.get_text(strip=True) for td in row.find_all("td")]
        if cols:
            entries.append({
                "columns": cols,
                "source_url": url
            })

    return entries


# ------------------------------ SCRAPE CONTACT INFO ------------------------------

def scrape_contact_page(url):
    soup = fetch_page(url)
    if soup is None:
        return {}

    text = soup.get_text(" ", strip=True)

    return {
        "raw_text": text,
        "source_url": url
    }


# ------------------------------ MASTER SCRAPER ------------------------------

def build_datasets():
    print("\n============================")
    print("  GMU DATASET SCRAPER")
    print("============================\n")

    # -------------------- 1. Program Pages --------------------
    program_pages = [
        ("Engineering (UG)", "https://gmu.ac.in/fetug"),
        ("Engineering (PG)", "https://gmu.ac.in/fetpg"),
        ("Commerce (UG)", "https://gmu.ac.in/fcitug"),
        ("Commerce (PG)", "https://gmu.ac.in/fcitpg"),
    ]

    all_programs = []
    for faculty_name, url in program_pages:
        all_programs.extend(parse_program_table(url, faculty_name))
        time.sleep(1)

    save_json("programs.json", all_programs)

    # -------------------- 2. Faculty Pages --------------------
    faculty_pages = {
        "CSE": "https://gmu.ac.in/csefaculty",
        "ECE": "https://gmu.ac.in/ecefaculty",
        "Mechanical": "https://gmu.ac.in/mechfaculty",
    }

    all_faculty = []
    for dept, url in faculty_pages.items():
        all_faculty.extend(parse_faculty_page(url, dept))
        time.sleep(1)

    save_json("faculty.json", all_faculty)

    # -------------------- 3. Research Council / Governance --------------------
    ric_url = "https://gmu.ac.in/academics_assessment"
    ric = parse_table_generic(ric_url)
    save_json("governance.json", ric)

    # -------------------- 4. PhD Supervisors --------------------
    phd_url = "https://gmu.ac.in/programfee"
    supervisors = parse_table_generic(phd_url)
    save_json("phd_supervisors.json", supervisors)

    # -------------------- 5. Contact Page --------------------
    contact_url = "https://gmu.ac.in/contact"
    contact = scrape_contact_page(contact_url)
    save_json("contacts.json", contact)

    print("\n============================")
    print("  SCRAPING COMPLETED")
    print("============================\n")


if __name__ == "__main__":
    build_datasets()
