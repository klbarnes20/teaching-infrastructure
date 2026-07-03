# Teaching Systems

## Purpose

A collection of shared infrastructure for managing courses, generating teaching materials, and reducing repetitive work.

The goal is to maintain a single source of truth so that information only needs to be updated once and all downstream outputs remain synchronized.

---

# Architecture

```text
Course YAML
Term CSV
Section CSV
Policy Documents
        ↓
Loaders
        ↓
Master Schedule Builder
        ↓
Generators
        ↓
Generated Outputs
        ↓
Teaching & Notion
```

---

# Configuration (Source Data)

These files define the teaching environment and should be edited directly.

## Course YAML Files

Define information that remains relatively stable across offerings.

Examples:

- Course title
- Course description
- Learning outcomes
- Weekly topics
- Readings
- Assessments
- Policies
- Textbook information
- Notion links
- Course-specific settings

Examples:

```text
MOS2320.yaml
MOS3321.yaml
MOS1033.yaml
```

---

## Term CSV

Defines dates and events shared across all courses within an academic term.

Examples:

- First day of classes
- Last instructional day
- Reading week
- Holidays
- Exam periods

Examples:

```text
terms.csv
```

---

## Section CSV Files

Define the individual offerings for a specific term.

Examples:

- Section numbers
- Meeting days
- Meeting times
- Classroom locations
- Midterm dates
- Delivery mode

Examples:

```text
f2026_sections.csv
w2027_sections.csv
```

---

## Policy Documents

Shared policy text used when generating syllabi and other teaching materials.

Examples:

- FASS appendix
- Academic integrity policies
- Accessibility statements

---

# Shared Utilities

Reusable code that supports multiple generators.

## `loaders.py`

Responsible for reading and assembling source data.

Examples:

- Load course YAML files
- Load term CSV
- Load section CSV
- Build section configurations

---

## `schedule_utils.py`

Responsible for schedule construction.

Examples:

- Generate class meetings
- Apply holidays and reading weeks
- Insert midterms
- Merge dates with instructional content
- Build master schedules

---

## `course_schedule.py`

Acts as the orchestration layer between configuration and generators.

Examples:

- Build all course schedules
- Retrieve schedules by course and section
- Provide a single interface for generators

This file serves as the primary entry point for downstream systems.

---

## `dates.py`

Provides shared date and anchor calculations.

Examples:

- First class date
- Midterm date
- End of term
- Relative offsets for task generation

---

## `markdown.py`

Reusable Markdown helpers.

Examples:

- Heading generation
- Checklist formatting
- Markdown utilities

---

Additional helper modules should contain reusable functionality rather than generator-specific logic.

---

# Templates

Templates used when generating documents.

Examples:

- Syllabus template
- Future email templates
- Future announcement templates
- Future exam templates

---

# Generators

Generators transform completed schedules into teaching artifacts.

Generators should consume schedules rather than building schedules themselves.

## Current

- Syllabus Generator
- Todoist Generator
- Weekly Brief Generator
- Academic Calendar Generator

## Future

- Exam Generator
- Brightspace Generator
- Announcement Generator
- Assignment Generator

Generators should contain as little hard-coded information as possible. Most information should originate from configuration files and the schedule engine.

---

# Master Schedule

The master schedule is the central object used by all generators.

It combines:

```text
Course YAML
    +
Term CSV
    +
Section CSV
```

into a single schedule representation.

The master schedule is responsible for:

- Mapping instructional weeks to dates
- Skipping holidays and reading weeks
- Inserting midterms
- Providing course-specific dates
- Maintaining stable instructional week numbers across academic years

This object is the authoritative source of scheduling information.

---

# Generated Outputs

Files created automatically by generators.

Examples:

- Syllabi
- Todoist imports
- Weekly briefs
- Academic calendars
- Future Brightspace imports
- Future announcements

Generated files should not be edited manually. Instead, update the source configuration and regenerate.

---

# Source of Truth

| Information | Source |
|------------|--------|
| Course information | Course YAML |
| Term dates and holidays | `terms.csv` |
| Section logistics | Section CSV |
| University policies | Policy documents |
| Weekly schedule | Master Schedule |
| Teaching tasks | Todoist Generator |
| Weekly teaching brief | Weekly Brief Generator |
| Teaching reflections | Notion |

---

# Design Principles

- Enter information once whenever possible.
- Separate configuration from generation.
- Treat schedules as a reusable intermediate layer.
- Keep reusable code in shared helper modules.
- Treat generated outputs as disposable artifacts that can always be recreated.
- Prefer automation over duplicated manual work.
- Generators should consume schedules, not create them.