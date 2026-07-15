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

def load_courses():
    """Load every course YAML file into a lookup dictionary."""
    courses_dir = BASE_DIR / "data" / "courses"

    return {
        path.stem.upper(): load_yaml(
            f"data/courses/{path.name}"
        )
        for path in courses_dir.glob("*.yaml")
    }


def load_term(term_id):
    try:
        return load_yaml(f"data/terms/{term_id}.yaml")
    except FileNotFoundError:
        raise FileNotFoundError(
            f"Could not find term configuration: data/terms/{term_id}.yaml"
        )
    
def load_instructor(instructor_id): 
    return load_yaml(f"data/instructors/{instructor_id}.yaml")

def load_course_policies():
    data = load_yaml("data/policies/common.yaml")
    return data["course_policies"]

def load_sections_from_csv(filepath, course_lookup):

    sections = []

    course_policies = load_course_policies()

    with open(filepath, newline="", encoding="utf-8-sig") as csvfile:
        reader = csv.DictReader(csvfile)

        course_policies = load_course_policies()

        for row in reader:
            section = {
                "course": course_lookup[row["course"]],
                "section": row["section"],
                "weekday": int(row["weekday"]),
                "time": row["time"],
                "location": row["location"],
                "term": load_term(row["term"]),
                "instructor": load_instructor(row["instructor"]),
                "course_policies": course_policies,

                "midterm": {
                    "week": int(row["midterm_week"]) if row["midterm_week"] else None,
                    "date": row["midterm_date"],
                    "time": row["midterm_time"],
                    "location": row["midterm_location"]
                }
            }

            sections.append(section)

    return sections

def format_textbook_citation(textbook):
    authors = textbook.get("authors", [])
    title = textbook.get("title", "")
    edition = textbook.get("edition", "")
    year = textbook.get("year", "")
    publisher = textbook.get("publisher", "")

    if not authors:
        author_text = ""
    elif len(authors) == 1:
        author_text = authors[0]
    elif len(authors) == 2:
        author_text = f"{authors[0]} & {authors[1]}"
    else:
        author_text = ", ".join(authors[:-1]) + f", & {authors[-1]}"

    citation = f"{author_text}. ({year}). {title}"

    if edition:
        citation += f" ({edition} edition)"

    if publisher:
        citation += f". {publisher}"

    return citation + "."