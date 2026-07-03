import csv
from pathlib import Path
import yaml

BASE_DIR = Path(__file__).resolve().parents[1]


def load_yaml(relative_path): 
    path = BASE_DIR / relative_path

    with open(path, "r", encoding="utf-8") as file: 
        return yaml.safe_load(file)


def load_sections_from_csv(filepath, course_lookup, terms_filepath):
    terms = load_terms_from_csv(terms_filepath)

    sections = []

    with open(filepath, newline="", encoding="utf-8-sig") as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            section = {
                "course": course_lookup[row["course"]],
                "term": terms[row["term"]],
                "section": row["section"],
                "weekday": int(row["weekday"]),
                "time": row["time"],
                "location": row["location"],

                "midterm": {
                    "week": int(row["midterm_week"]) if row["midterm_week"] else None,
                    "date": row["midterm_date"],
                    "time": row["midterm_time"],
                    "location": row["midterm_location"]
                }
            }

            sections.append(section)

    return sections

def load_terms_from_csv(filepath):

    terms = {}

    with open(filepath, newline='', encoding='utf-8-sig') as csvfile:

        reader = csv.DictReader(csvfile)

        for row in reader:

            terms[row["term"]] = {
                "start_date": row["start_date"],
                "end_date": row["end_date"],
                "term": row["term"],
                "holidays": parse_holidays(row["holidays"])
            }

    return terms

def parse_holidays(holiday_string):

    holidays = []

    if not holiday_string:
        return holidays

    entries = holiday_string.split(";")

    for entry in entries:

        start, end, label = entry.split("|")

        holidays.append({
            "start": start,
            "end": end,
            "label": label
        })

    return holidays

def build_section_config(section_info): 
    return {
        **section_info["course"],
        **section_info["term"],

        "section": section_info["section"],
        "class_weekday": section_info["weekday"],
        "class_time": section_info["time"],
        "location": section_info["location"], 

        "midterm": section_info.get("midterm", {})
    }