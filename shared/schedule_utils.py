# TODO:
# Update preview_schedule to use master_schedule
# rather than config["schedule"]

# IMPORTS AND CONSTANTS
from datetime import timedelta, datetime
import pandas as pd
import csv
from data.configs import *

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

######### CSV LOADERS 
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



###### SCHEDULE BUILDERS 

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

def generate_class_schedule(start_date, end_date, class_weekday, holidays, class_time, location):
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d") 
    
    schedule_dates = []
    current = start
    
    while current <= end:
        if current.weekday() == class_weekday:

            is_holiday = False
            label = None

            for holiday in holidays:
                h_start = datetime.strptime(holiday["start"], "%Y-%m-%d")
                h_end = datetime.strptime(holiday["end"], "%Y-%m-%d")

                if h_start <= current <= h_end:
                    is_holiday = True
                    label = holiday["label"]
                    break

            schedule_dates.append({
                "date": current,
                "time": class_time,
                "location": location,
                "is_holiday": is_holiday,
                "label": label
            })

        current += timedelta(days=1)
    
    return schedule_dates

def build_master_schedule(config):

    schedule_dates = generate_class_schedule(
        config["start_date"],
        config["end_date"],
        config["class_weekday"],
        config["holidays"], 
        config["class_time"],
        config["location"]
    )

    weeks = []
    yaml_week_index = 0

    midterm_week = config.get("midterm", {}).get("week")
    midterm_week = int(midterm_week) if midterm_week not in (None, "", "TBD") else None
    has_midterm = config.get("has_midterm", False)

    for meeting_num, date_info in enumerate(schedule_dates, start=1):

        if has_midterm and midterm_week == meeting_num:
            week_data = {
                "week": None,
                "date": date_info["date"],
                "date_str": date_info["date"].strftime("%A, %B %d, %Y"),
                "is_holiday": date_info["is_holiday"],
                "holiday_label": date_info["label"],
                "class_weekday": config["class_weekday"],
                "class_time": config["class_time"],
                "location": config["location"],
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
            "date": date_info["date"],
            "date_str": date_info["date"].strftime("%A, %B %d, %Y"),
            "is_holiday": date_info["is_holiday"],
            "holiday_label": date_info["label"],
            "class_weekday": config["class_weekday"],
            "class_time": config["class_time"],
            "location": config["location"],
            **week_config
        }

        if "type" not in week_data:
            week_data["type"] = "instruction"

        weeks.append(week_data)
        yaml_week_index += 1

    return {
        **config,
        "weeks": weeks
        # "course_code": config["course_code"],
        # "course_name": config["course_name"],
        # "section": config["section"],
        # "term": config["term"],
        # "weeks": weeks,
        # "class_weekday": config["class_weekday"],
        # "class_time": config["class_time"],
        # "location": config["location"]
    }
########## SCHEDULE UTILITIES 

def map_assignment_due_dates(schedule, config):
    due_info = {}

    for row in schedule:
        notes = row.get("notes", "")
        if not notes:
            continue

        for assignment in config.get("assignments", []):
            name = assignment["name"]
            if name in notes:
                due_info[name] = {
                    "date": row["date"],
                    "week": row["week"]
                }

    return due_info


#### DISPLAY / DEBUG FUNCTIONS 
def preview_schedule(config, successes=None, warnings=None, errors=None):


    print("\n" + "="*70)

    print(f"{config['course_code']} - {config['course_name']}")
    print(f"Section: {config['section']}")
    print(f"Time: {config['class_time']}")
    print(f"Weekday: {WEEKDAY_NAMES[config['class_weekday']]}")
    print(f"Location: {config['location']}")
    print(f"Term: {config['term']}")

    print("\n" + "-" * 70)
    print("\nVALIDATION")

    if successes:
        for s in successes:
            print(f"✔ {s}")

    if warnings:
        for w in warnings:
            print(f"⚠ {w}")

    if errors:
        for e in errors:
            print(f"✖ {e}")

    print("\n" + "-" * 70)

    for row in config["schedule"]:

        week = row["week"]
        date = row["date"]
        topic = row["topic"]
        notes = row["notes"]

        print(f"Week {week:>2} | {date:<8} | {topic}")

        if notes:
            print(f"      ⚠ {notes}")
    
    print("=" * 70)

    