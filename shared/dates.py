# =============================================================================
# date_helpers.py
#
# Purpose
# -------
# Shared utilities for parsing, formatting, and manipulating dates.
#
# Responsibilities
# ----------------
# - Parse date strings.
# - Format dates for display.
# - Provide reusable date calculations.
#
# This module SHOULD:
# - Work with dates.
# - Be reusable by any generator.
#
# This module should NOT:
# - Know anything about courses, schedules, or Brightspace.
# =============================================================================

from datetime import datetime


def parse_date(date_string):
    return datetime.strptime(date_string, "%Y-%m-%d")


def get_term_start(schedule):
    return schedule["weeks"][0]["date"]


def get_term_end(schedule):
    return schedule["weeks"][-1]["date"]


def calculate_midterm_date(schedule):
    for week in schedule["weeks"]:
        if week.get("type") == "midterm":
            return week["date"]

    return None


def get_anchor_date(schedule, anchor_name):
    anchors = {
        "first_class": get_term_start(schedule),
        "midterm_date": calculate_midterm_date(schedule),
        "term_end": get_term_end(schedule)
    }

    return anchors[anchor_name]