# TODO:
# Update preview_schedule to use master_schedule
# rather than config["schedule"]

# IMPORTS AND CONSTANTS
from datetime import timedelta, datetime
import pandas as pd
import csv
#from data.configs import *
from shared.loaders import *
from itertools import groupby

WEEKDAY_NAMES = {
    0: "Monday",
    1: "Tuesday",
    2: "Wednesday",
    3: "Thursday",
    4: "Friday",
    5: "Saturday",
    6: "Sunday"
} 

############ GENERIC HELPERS 
def date_range(start, end):
    return pd.date_range(pd.to_datetime(start), pd.to_datetime(end), freq="D")
 
def make_week_label(row):
    if pd.notna(row["instruction_week"]):
        return f"Week {int(row['instruction_week'])}"
    if "Break" in row["day_types"] and "Reading Week" in row["special_dates"]:
        return "Reading Week"
    if "Break" in row["day_types"]:
        return "Break"
    if "Exam Period" in row["day_types"]:
        return "Exam Period"
    if "Study Day" in row["day_types"]:
        return "Study Day"
    return "NA"

def load_term(term_id):
    return load_yaml(f"data/terms/{term_id}.yaml")

###### SCHEDULE BUILDERS 

def build_meeting_metadata(date_info, config):
    return {
        "date": date_info["date"],
        "date_str": date_info["date"].strftime("%A, %B %d, %Y"),
        "is_holiday": date_info["is_holiday"],
        "holiday_label": date_info["label"],
        "class_weekday": config["class_weekday"],
        "class_time": config["class_time"],
        "location": config["location"],
    }

def build_section(section_info): 
    return {
        **section_info["course"],
        **section_info["term"],
        "instructor": section_info["instructor"]["name"],
        "email": section_info["instructor"]["email"],
        "office": section_info["instructor"]["office"], 
        "office_hours": section_info["instructor"]["office_hours"],

        "section": section_info["section"],
        "class_weekday": section_info["weekday"],
        "class_time": section_info["time"],
        "location": section_info["location"], 
        "course_policies": section_info.get("course_policies", {}),

        "midterm": section_info.get("midterm", {}),
        
        "meetings": [
    {
        "section": section_info["section"],
        "class_weekday": section_info["weekday"],
        "class_time": section_info["time"],
        "location": section_info["location"],
    },
],
    }
    
def build_course_term(schedules):
    first = schedules[0]

    return {
        "id": f"{first['course_code']}_{first['term']}", 
        "course_code": first["course_code"],
        "term": first["term"],
        "schedules": schedules,
    }

def get_meetings(course_term):
    meetings = []

    for schedule in course_term["schedules"]:
        meetings.extend(schedule["meetings"])

    return meetings 

def get_primary_schedule(course_term):
    return course_term["schedules"][0]

def build_all_sections(sections_file="data/f2026_sections.csv"):
    course_lookup = load_courses()

    raw_sections = load_sections_from_csv(
        sections_file,
        course_lookup,
    )

    return [build_section(section) for section in raw_sections]

def build_all_course_schedules(sections_file="data/f2026_sections.csv"):
    sections = build_all_sections(sections_file)

    return [
        build_master_schedule(section)
        for section in sections
    ]

def build_all_course_terms(sections_file="data/f2026_sections.csv"):
    schedules = build_all_course_schedules(sections_file)

    schedules.sort(
        key=lambda s: (
            s["course_code"],
            s["term"]
        )
    )

    return [
        build_course_term(list(group))
        for _, group in groupby(
            schedules, 
            key=lambda s: (
                s["course_code"],
                s["term"]
            )
        )
    ]

def generate_class_schedule(config):
    start = config["start_date"]
    end = config["end_date"]
    
    schedule_dates = []
    current = start
    
    while current <= end:
        if current.weekday() == config["class_weekday"]:

            is_holiday = False
            label = None

            for holiday in config["holidays"]:
                h_start = holiday["start"]
                h_end = holiday["end"]

                if h_start <= current <= h_end:
                    is_holiday = True
                    label = holiday["label"]
                    break

            schedule_dates.append({
                "date": current,
                "time": config["class_time"],
                "location": config["location"],
                "is_holiday": is_holiday,
                "label": label
            })

        current += timedelta(days=1)
    
    return schedule_dates

def build_master_schedule(config):

    schedule_dates = generate_class_schedule(config)

    weeks = []
    yaml_week_index = 0

    midterm_week = config.get("midterm", {}).get("week")
    midterm_week = int(midterm_week) if midterm_week not in (None, "", "TBD") else None
    has_midterm = config.get("has_midterm", False)

    for meeting_num, date_info in enumerate(schedule_dates, start=1):

        if has_midterm and midterm_week == meeting_num:
            week_data = {
                "week": None,
                **build_meeting_metadata(date_info, config), 
                "type": "midterm",
                "topic": "Midterm Exam",
                "readings": None,
                "assignments": None,
                "lab": None,
                "notes": None
            }

            weeks.append(week_data)
            continue

        if yaml_week_index >= len(config["weeks"]):
            break

        week_config = config["weeks"][yaml_week_index]

        week_data = {
            **build_meeting_metadata(date_info, config),
            **week_config
        }

        if "type" not in week_data:
            week_data["type"] = "instruction"

        weeks.append(week_data)
        yaml_week_index += 1

    return {
        **config,
        "weeks": weeks
    }
########## SCHEDULE UTILITIES 

def map_assignment_due_dates(schedule):
    due_info = {}

    for row in schedule:
        assignments = row.get("assignments") or []

        for assignment in assignments:
            due_info[assignment] = {
                "date": row["date"],
                "week": row["week"]
            }

    return due_info


