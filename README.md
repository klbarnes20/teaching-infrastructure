# Teaching Systems

## Purpose

A collection of shared infrastructure for managing courses, generating teaching materials, and reducing repetitive work.

The goal is to maintain a single source of truth so that information only needs to be updated once and all downstream outputs remain synchronized.

---

# Architecture

```text
Course YAML
Term YAML
Section CSV
Policy Documents
        ↓
Loaders
        ↓
Course Offering Builder
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

Define information that remains relatively stable across course offerings.

Examples:

- Course title
- Course description
- Learning outcomes
- Weekly instructional plan
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

## Term YAML Files

Define dates and events shared across all courses within an academic term.

Examples:

- Term name
- First day of classes
- Last instructional day
- Holidays
- Reading week
- Exam period

Examples:

```text
F2026.yaml
W2027.yaml
```

---

## Section CSV Files

Define the individual offerings for a specific term.

Examples:

- Section numbers
- Meeting days
- Meeting times
- Classroom locations
- Midterm information
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

Reusable code supporting multiple generators.

## `loaders.py`

Responsible only for loading source data.

Examples:

- Load course YAML
- Load term YAML
- Load section CSV

Loaders should not contain business logic.

---

## `schedule_utils.py`

Responsible for constructing and validating schedules.

Examples:

- Build course offerings
- Generate class meetings
- Apply holidays and reading weeks
- Insert midterms
- Merge instructional content with calendar dates
- Validate schedules
- Build master schedules

---

## `course_schedule.py`

The orchestration layer for the scheduling pipeline.

Responsibilities:

- Load all source data
- Build course offerings
- Generate master schedules
- Provide a single interface for downstream generators

All generators should obtain schedules through this module rather than constructing schedules independently.

---

## `dates.py`

Shared date utilities.

Examples:

- Anchor dates
- Relative date calculations
- Date helper functions

---

## `markdown.py`

Reusable Markdown utilities.

Examples:

- Heading generation
- Checklist formatting
- Markdown helpers

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

Generators transform completed master schedules into teaching artifacts.

Generators should consume schedules rather than build schedules themselves.

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

Generators should contain as little hard-coded information as possible. Information should originate from the configuration files and master schedule.

---

# Master Schedule

The master schedule is the central object used throughout the teaching infrastructure.

It combines:

```text
Course YAML
      +
Term YAML
      +
Section CSV
```

into a complete course offering with dated instructional meetings.

The master schedule is responsible for:

- Mapping instructional weeks to calendar dates
- Preserving stable instructional week numbers
- Applying holidays and reading weeks
- Inserting midterms
- Providing assignment due dates
- Serving as the authoritative schedule consumed by all generators

Internally, dates are stored as native Python `date` objects and formatted only when generating outputs.

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

Generated files should never be edited manually. Update the source configuration and regenerate instead.

---

# Source of Truth

| Information | Source |
|------------|--------|
| Course information | Course YAML |
| Term dates, holidays, exam periods | Term YAML |
| Section logistics | Section CSV |
| University policies | Policy documents |
| Master schedule | Schedule engine |
| Teaching tasks | Todoist Generator |
| Weekly teaching brief | Weekly Brief Generator |
| Teaching reflections | Notion |

---

# Design Principles

- Enter information once whenever possible.
- Separate configuration from business logic.
- Treat schedules as reusable domain objects.
- Keep loaders responsible only for loading data.
- Keep reusable code in shared helper modules.
- Treat generated outputs as disposable artifacts that can always be recreated.
- Prefer automation over duplicated manual work.
- Generators should consume master schedules rather than create schedules themselves.
- Use native Python data types internally whenever possible and defer formatting until output generation.