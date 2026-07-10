from data.configs import COURSE_LOOKUP
from shared.loaders import *
from shared.schedule_utils import *


def build_all_course_schedules(
    sections_file="data/f2026_sections.csv",
):
    sections = load_sections_from_csv(
        sections_file,
        COURSE_LOOKUP
    )

    schedules = []

    for section in sections:
        section = build_section(section)
        schedule = build_master_schedule(section)
        schedules.append(schedule)

    return schedules


def get_schedule(course_code, section, schedules=None):
    if schedules is None:
        schedules = build_all_course_schedules()

    for schedule in schedules:
        if schedule["course_code"].replace(" ", "") == course_code.replace(" ", "") and schedule["section"] == section:
            return schedule

    raise ValueError(f"No schedule found for {course_code} section {section}")