# =============================================================================
# 2. teaching_model.py
#
# Purpose
# -------
# Build and work with the teaching data model.
#
# Responsibilities
# ----------------
# - Build section objects from loaded configuration.
# - Build dated teaching schedules from sections.
# - Merge schedules into course_term objects.
# - Provide helper functions for navigating schedules.
# - Provide small utilities for working with schedule data.
#
# This module SHOULD:
# - Build objects.
# - Merge objects.
# - Provide helper functions for the teaching data model.
#
# This module should NOT:
# - Read files directly from disk.
# - Render HTML or other output.
# - Write generated files.
#
# Data Model
# ----------
#
# raw section
#      │
#      ▼
# build_section()
#      │
#      ▼
# section
#      │
#      ▼
# build_master_schedule()
#      │
#      ▼
# schedule
#      │
#      ▼
# build_course_term()
#      │
#      ▼
# course_term
#
# The resulting objects are used throughout the project by generators such as
# Brightspace, calendars, Todoist, and future outputs.
# =============================================================================

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


### Object Builders 

def build_section(section_info): 
    config = {
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
        }
    ],
}

    print(config["course_code"])
    print("RETURN has_midterm:", config.get("has_midterm"))
    print("RETURN midterm:", config.get("midterm"))

    return config
#     return {
#         **section_info["course"],
#         **section_info["term"],
#         "instructor": section_info["instructor"]["name"],
#         "email": section_info["instructor"]["email"],
#         "office": section_info["instructor"]["office"], 
#         "office_hours": section_info["instructor"]["office_hours"],

#         "section": section_info["section"],
#         "class_weekday": section_info["weekday"],
#         "class_time": section_info["time"],
#         "location": section_info["location"], 
#         "course_policies": section_info.get("course_policies", {}),

#         "midterm": section_info.get("midterm", {}),
#         "has_midterm": section_info.get("has_midterm", False),
        
#         "meetings": [
#     {
#         "section": section_info["section"],
#         "class_weekday": section_info["weekday"],
#         "class_time": section_info["time"],
#         "location": section_info["location"],
#     },
# ],
#     }

def build_master_schedule(config):
    
    schedule_dates = generate_class_schedule(config)

    weeks = []
    yaml_week_index = 0

    for date_info in schedule_dates:

        # Holiday row
        if date_info["is_holiday"]:
            weeks.append({
                **build_meeting_metadata(date_info, config),
                "week": None,
                "type": "holiday",
                "topic": date_info["label"],
                "readings": None,
                "assignments": None,
                "lab": None,
                "notes": None
            })
            continue

        # Stop if we've run out of instructional weeks
        if yaml_week_index >= len(config["weeks"]):
            break
        
        week_config = config["weeks"][yaml_week_index]

        week_data = {
            **build_meeting_metadata(date_info, config),
            **week_config
        }

        # Default to instruction if no type was supplied
        week_data.setdefault("type", "instruction")

        weeks.append(week_data)
        yaml_week_index += 1
        
    return {
        **config,
        "weeks": weeks
    }

def build_course_term(schedules):
    first = schedules[0]

    return {
        "id": f"{first['course_code']}_{first['term']}", 
        "course_code": first["course_code"],
        "term": first["term"],
        "schedules": schedules,
    }

### Object Collections 
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

### Accessors 

def get_meetings(course_term):
    meetings = []

    for schedule in course_term["schedules"]:
        meetings.extend(schedule["meetings"])

    return meetings 

def get_primary_schedule(course_term):
    return course_term["schedules"][0]

def get_schedule(course_code, section, schedules=None):
    if schedules is None:
        schedules = build_all_course_schedules()

    for schedule in schedules:
        if schedule["course_code"].replace(" ", "") == course_code.replace(" ", "") and schedule["section"] == section:
            return schedule

    raise ValueError(f"No schedule found for {course_code} section {section}")

### Schdule Generation

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
########## UTILITIES 

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


