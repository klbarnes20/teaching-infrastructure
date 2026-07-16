# Architecture
# TODO: Brightspace generators should receive merged-course configs rather than individual-section configs.
# TODO: Split Brightspace generators into separate page modules as the feature set grows.

# Content
# TODO: Render the course description and prerequisites.
# TODO: Decide what brief exam, participation, and term-project information belongs on the Course Information page.
# TODO: Keep detailed term-project instructions in a separate renderer.
# TODO: Render supports and resources.
# TODO: Add a downloadable syllabus link.

# Helpers
# TODO: Expand the shared HTML helper library.
# TODO: Consolidate presentation logic into shared helpers.
# TODO: Review escaping of user-supplied versus trusted HTML.
# TODO: Extract shared formatting logic only where duplicated.

# Output
# TODO: Test generated HTML inside Brightspace.
# TODO: Add validation for missing required config fields.
# TODO: Save generated files under outputs/brightspace/.

# Renderer Structure 
# def render_xxx(config):

#     # collect data

#     # return early if empty

#     # build intermediate html

#     html = section_heading(...)

#     html += ...

#     return html


from datetime import date
from html import escape


from shared.html_helpers import *
from shared.schedule_utils import map_assignment_due_dates

def generate_course_info(config):
    """Generate the Course Information HTML page."""
    
    sections = [
        render_course_basics,
        render_learning_outcomes,
        render_textbook,
        render_assessment_table,
        render_course_schedule,
        render_course_policies
        
    ]

    parts = []

    for section in sections: 
        html = section(config)
        if html: 
            parts.append(html)

    body = "\n<hr>\n".join(parts)

    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>Course Information</title>
</head>
<body>

{body}

</body>
</html>
"""


def render_course_basics(config):

    html = section_heading("Course Basics")
    
    html += """
    <table style="border-collapse: collapse; width: 100%;">
    """
    html += table_row(
        "Course",
        f"{config['course_code']} {config['course_name']}"
    )

    html += table_row("Instructor", config["instructor"])
    html += table_row("Email", config["email"])
    html += table_row("Office", config["office"])
    html += table_row("Office Hours", config["office_hours"])
    html += table_row("Section", config["section"])
    html += table_row("Class Time", config["class_time"])
    html += table_row("Location", config["location"])

    html += "</table>"

    return html


def render_learning_outcomes(config): 
    outcomes = config.get("learning_outcomes", [])

    if not outcomes: 
        return ""
    
    list_items = "\n".join(
        f"<li>{escape(str(outcome))}</li>"
        for outcome in outcomes
    )

    html = section_heading("Course Learning Outcomes")

    html += f"""
    <p>By the end of this course, you should be able to:</p>
    <ul>
        {list_items}
    </ul>
    """

    return html 


def render_textbook(config):
    textbook = config.get("textbook", {})

    if not textbook:
        return ""

    authors = ", ".join(textbook.get("authors", []))
    bookstore = textbook.get("bookstore", {})

    rows = [
        table_row("Title", escape(str(textbook.get("title", "")))),
        table_row("Author(s)", escape(authors)),
        table_row("Edition", escape(str(textbook.get("edition", "")))),
        table_row("Publisher", escape(str(textbook.get("publisher", "")))),
        table_row("Year", escape(str(textbook.get("year", "")))),
    ]

    if textbook.get("isbn"):
        rows.append(
            table_row("ISBN", escape(str(textbook["isbn"])))
        )

    purchase_html = ""

    if bookstore.get("price"):
        purchase_html += (
            f"<p><strong>Approximate price:</strong> "
            f"{escape(str(bookstore['price']))}</p>"
        )

    if bookstore.get("notes"):
        purchase_html += (
            f"<p>{escape(str(bookstore['notes']))}</p>"
        )

    if bookstore.get("link"):
        url = escape(str(bookstore["link"]), quote=True)
        purchase_html += (
            f'<p><a href="{url}" target="_blank">'
            "View the textbook at the bookstore"
            "</a></p>"
        )

    alternatives = textbook.get("alternatives", [])
    alternatives_html = ""

    if alternatives:
        items = "\n".join(
            f"<li>{escape(str(item))}</li>"
            for item in alternatives
        )

        alternatives_html = (
            subsection_heading("Other Options")
            + f"""
<ul>
{items}
</ul>
"""
        )

    html = section_heading("Textbook and Readings")

    html += f"""
<table style="border-collapse: collapse; width: 100%;">
{''.join(rows)}
</table>

{purchase_html}
{alternatives_html}
"""

    return html


def render_assessment_table(config):
    assignments = config.get("assignments", [])
    schedule = config.get("weeks", [])

    if not assignments:
        return ""

    due_info = map_assignment_due_dates(schedule)

    assignments = sorted(
        assignments,
        key=lambda item: due_info.get(item["name"], {}).get("week", 999),
    )

    rows = []
    total_weight = 0
    last_group = None

    for item in assignments:
        group = item.get("type", "Other")
        name = item["name"]
        weight = item["weight"]

        info = due_info.get(name, {})
        due = info.get("date", "—")
        week = info.get("week", "—")

        if isinstance(due, date):
            due = due.strftime("%B %d, %Y")

        if group == "Participation":
            due = "Ongoing"
            week = "—"

        group_label = "" if group == last_group else group
        last_group = group

        rows.append(
    data_row(
        escape(group_label),
        escape(name),
        f"{weight}%",
        escape(str(week)),
        escape(str(due)),
    )
)

        total_weight += weight

    rows.append(
        raw_data_row(
            "",
            "<strong>Total</strong>",
            f"<strong>{total_weight}%</strong>",
            "",
            "",
        )
    )

    html = section_heading("Evaluation and Assignments")

    html += f"""
<table style="border-collapse: collapse; width: 100%; table-layout: fixed;">
    <thead>
        {table_header(
    [
        "Component",
        "Item",
        "Weight",
        "Week",
        "Due",
    ],
    widths=[
        "18%",
        "42%",
        "10%",
        "10%",
        "20%",
    ],
)}
    </thead>
    <tbody>
        {''.join(rows)}
    </tbody>
</table>
"""

    return html


def render_course_policies(config):
    policies = config.get("course_policies", {})

    enabled_policies = sorted(
        (
            policy
            for policy in policies.values()
            if policy.get("enabled", True)
        ),
        key=lambda policy: policy.get("order", 999),
    )

    if not enabled_policies:
        return ""

    policy_sections = []

    for policy in enabled_policies:
        title = escape(str(policy.get("title", "")))

        bullet_items = "\n".join(
            f"<li>{escape(str(item))}</li>"
            for item in policy.get("text", [])
            if str(item).strip()
        )

        summary = policy.get("summary")
        summary_html = (
            f"<p>{escape(str(summary))}</p>"
            if summary
            else ""
        )

        policy_sections.append(
            f"""
{subsection_heading(title)}
{summary_html}
<ul>
{bullet_items}
</ul>
"""
        )

    html = section_heading("Course Policies")
    html += "".join(policy_sections)

    return html



def render_course_schedule(config):
    schedule = config.get("weeks", [])

    if not schedule:
        return ""

    headers = [
        "Week",
        "Date",
        "Topic",
        "Readings",
        "Assignments",
    ]

    rows = []

    for item in schedule:
        week = "" if item.get("week") is None else str(item["week"])
        date = item["date"].strftime("%b %d")
        topic = item.get("topic", "")

        readings = format_cell(item.get("readings"))
        assignments = format_cell(item.get("assignments"))

        rows.append(
            data_row(
                week,
                date,
                topic,
                readings,
                assignments,
            )
        )

    html = section_heading("Tentative Course Schedule")

    html += f"""
    <table style="
        border-collapse: collapse;
        width: 100%;
        table-layout: fixed;
    ">
        <thead>
            {table_header(
                headers,
                widths=[
                    "10%",
                    "12%",
                    "43%",
                    "15%",
                    "20%",
                ],
            )}
        </thead>
        <tbody>
            {"".join(rows)}
        </tbody>
    </table>
    """

    return html