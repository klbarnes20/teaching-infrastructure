# LOADERS.PY 
# Responsible for reading files 

import csv
from pathlib import Path
import yaml

BASE_DIR = Path(__file__).resolve().parents[1]


def load_yaml(relative_path): 
    path = BASE_DIR / relative_path

    with open(path, "r", encoding="utf-8") as file: 
        return yaml.safe_load(file)

def load_term(term_id):
    try:
        return load_yaml(f"data/terms/{term_id}.yaml")
    except FileNotFoundError:
        raise FileNotFoundError(
            f"Could not find term configuration: data/terms/{term_id}.yaml"
        )

def load_sections_from_csv(filepath, course_lookup):

    sections = []

    with open(filepath, newline="", encoding="utf-8-sig") as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            section = {
                "course": course_lookup[row["course"]],
                "section": row["section"],
                "weekday": int(row["weekday"]),
                "time": row["time"],
                "location": row["location"],
                "term": load_term(row["term"]),

                "midterm": {
                    "week": int(row["midterm_week"]) if row["midterm_week"] else None,
                    "date": row["midterm_date"],
                    "time": row["midterm_time"],
                    "location": row["midterm_location"]
                }
            }

            sections.append(section)

    return sections
