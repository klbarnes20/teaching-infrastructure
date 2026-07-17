# Teaching Systems

## Purpose

Teaching Systems is a collection of shared infrastructure for managing university courses, generating teaching materials, and reducing repetitive work.

The guiding principle is to maintain a **single source of truth** so that course information only needs to be entered once. From that shared data model, multiple teaching artifacts—including syllabi, Brightspace pages, calendars, and task lists—can be generated automatically.

The project is designed around a clear separation between configuration, business logic, and output generation, making it easy to maintain and extend over time.

---

# Architecture

```text
Source Data
───────────
Course YAML
Term YAML
Section CSV
Policy Documents

        │
        ▼

Loaders
────────
loaders.py

        │
        ▼

Teaching Model
──────────────
teaching_model.py

Course
Section
Schedule
Course Term

        │
        ▼

Generators
──────────
Brightspace
Syllabus
Todoist
Calendar
...

        │
        ▼

Generated Outputs
```

---

# Source Data

Source data defines the teaching environment and should be edited directly. All generated outputs originate from these files.

---

## Course YAML

Course YAML files define information that remains relatively stable across offerings of a course.

Examples include:

* Course title
* Course code
* Course description
* Learning outcomes
* Weekly instructional plan
* Readings
* Assessments
* Course policies
* Textbook information
* Notion links
* Course-specific settings

Examples:

```text
MOS2320.yaml
MOS3321.yaml
MOS1033.yaml
```

---

## Term YAML

Term YAML files define dates and events shared across all courses in a particular academic term.

Examples include:

* Term name
* First day of classes
* Last instructional day
* Holidays
* Reading week
* Exam period

Examples:

```text
F2026.yaml
W2027.yaml
```

---

## Section CSV

Section CSV files define the logistics for each individual course offering.

Examples include:

* Section number
* Meeting day
* Meeting time
* Classroom location
* Delivery mode
* Midterm information
* Instructor assignment

Examples:

```text
f2026_sections.csv
w2027_sections.csv
```

---

## Policy Documents

Shared policy documents provide standardized text used across multiple teaching materials.

Examples include:

* FASS Appendix
* Academic integrity policies
* Accessibility statements
* University-required syllabus language

---

# Shared Modules

Shared modules provide reusable functionality used throughout the project.

---

## `loaders.py`

### Purpose

Load source data into Python objects.

### Responsibilities

* Read Course YAML files
* Read Term YAML files
* Read Section CSV files
* Load policy documents
* Return Python dictionaries and lists

### Should

* Read files from disk
* Parse configuration data

### Should Not

* Build schedules
* Apply business logic
* Generate output

---

## `teaching_model.py`

### Purpose

Construct and manage the teaching data model.

### Responsibilities

* Build section objects
* Build schedules
* Build course terms
* Merge instructional content with calendar dates
* Apply holidays and reading weeks
* Insert midterms
* Map assignment due dates
* Validate schedules
* Provide helper and accessor functions

### Core Objects

```text
Raw Section
      │
      ▼
Section
      │
      ▼
Schedule
      │
      ▼
Course Term
```

This module represents the heart of the teaching infrastructure. All generators consume these objects rather than rebuilding schedules independently.

---

## Helper Modules

Helper modules provide reusable functionality without depending on the teaching model.

### `date_helpers.py`

Shared utilities for working with dates.

Examples include:

* Date parsing
* Date formatting
* Relative date calculations
* Academic calendar utilities

---

### `html_helpers.py`

Reusable HTML generation utilities.

Examples include:

* Tables
* Headings
* Lists
* Formatting helpers
* HTML escaping

---

### `markdown_helpers.py`

Reusable Markdown generation utilities.

Examples include:

* Heading generation
* Lists
* Checklists
* Common Markdown formatting

---

Additional helper modules should provide reusable functionality rather than contain generator-specific business logic.

---

# Teaching Model

The teaching model represents the complete state of a course offering after all source data has been combined.

It is the central object used throughout the teaching infrastructure.

The teaching model combines:

```text
Course YAML
      +
Term YAML
      +
Section CSV
```

into a reusable representation of a course offering.

The model consists of four primary objects:

```text
Raw Section
      │
      ▼
Section
      │
      ▼
Schedule
      │
      ▼
Course Term
```

These objects provide:

* Dated instructional meetings
* Stable instructional week numbers
* Holiday handling
* Reading week support
* Midterm insertion
* Assignment due-date mapping
* Shared metadata across sections

Internally, dates are stored as native Python `date` objects and are formatted only when generating outputs.

---

# Templates

Templates define the appearance of generated documents while keeping content separate from presentation.

Examples include:

* Syllabus template
* Email templates
* Announcement templates
* Exam templates
* Future report templates

---

# Generators

Generators transform the teaching model into instructor-facing artifacts.

Generators should consume the teaching model rather than recreate schedules or business logic.

Current generators include:

* Brightspace Generator
* Syllabus Generator
* Todoist Generator
* Academic Calendar Generator

Planned generators include:

* Exam Generator
* Announcement Generator
* Assignment Generator
* Weekly Brief Generator

Generators should:

* Contain minimal hard-coded information
* Pull information from the teaching model whenever possible
* Focus solely on presentation and formatting

---

# Generated Outputs

Generated outputs are disposable artifacts produced automatically by generators.

Examples include:

* Syllabi
* Brightspace pages
* Todoist imports
* Academic calendars
* Assignment instructions
* Weekly teaching briefs
* Future announcements

Generated outputs should never be edited manually.

Instead, update the source data and regenerate the output.

---

# Single Source of Truth

| Information          | Source                |
| -------------------- | --------------------- |
| Course information   | Course YAML           |
| Term dates           | Term YAML             |
| Section logistics    | Section CSV           |
| University policies  | Policy documents      |
| Teaching model       | `teaching_model.py`   |
| Brightspace pages    | Brightspace Generator |
| Syllabi              | Syllabus Generator    |
| Todoist tasks        | Todoist Generator     |
| Academic calendars   | Calendar Generator    |
| Teaching reflections | Notion                |

---

# Design Principles

* Maintain a single source of truth.
* Separate configuration from business logic.
* Build a reusable teaching model before generating outputs.
* Keep loaders responsible only for loading data.
* Keep helper modules independent of the teaching model whenever practical.
* Treat generated outputs as disposable artifacts that can always be regenerated.
* Prefer automation over duplicated manual work.
* Use native Python data types internally and defer formatting until output generation.
* Favor small, focused modules with clear responsibilities.
* Design generators as presentation layers over the teaching model rather than independent systems.
