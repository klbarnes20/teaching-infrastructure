from html import escape

### Headers 

def section_heading(title):
    return f"""
    <h2 style="
        margin-top: 0;
        margin-bottom: 16px;
        padding-bottom: 6px;
        border-bottom: 2px solid #d9d9d9;
    ">
        {title}
    </h2>
    """

def subsection_heading(title):
    return f"""
    <h3 style="
        margin-top: 24px;
        margin-bottom: 8px;
    ">
        {title}
    </h3>
    """

def table_row(label, value):
    return f"""
    <tr>
        <th style="
            text-align: left;
            vertical-align: top;
            width: 180px;
            padding: 6px 12px 6px 0;
            font-weight: 500;
        ">
            {label}
        </th>
        <td style="
            text-align: left;
            padding-right: 36px;
            border-bottom: 1px solid #e5e5e5;
        ">
            {value}
        </td>
    </tr>
    """


def table_header(headers, widths=None):
    cells = []

    for i, header in enumerate(headers):
        style = [
            "text-align: left;",
            "padding: 8px;",
            "border-bottom: 2px solid #d9d9d9;",
        ]

        if widths:
            style.append(f"width: {widths[i]};")

        cells.append(
            f'<th style="{" ".join(style)}">{escape(header)}</th>'
        )

    return f"""
    <tr>
        {''.join(cells)}
    </tr>
    """


def data_row(*values):
    cells = []

    for value in values:
        cells.append(
            f"""
<td style="
    padding: 8px;
    border-bottom: 1px solid #eeeeee;
    vertical-align: top;
">
    {escape(str(value))}
</td>
"""
        )

    return f"""
    <tr>
        {''.join(cells)}
    </tr>
    """

def format_cell(value):
    if value is None:
        return ""
    if isinstance(value, list):
        return ", ".join(value)
    return str(value)

def raw_data_row(*values):
    cells = []

    for value in values:
        cells.append(
            f"""
<td style="
    padding: 8px;
    border-bottom: 1px solid #eeeeee;
    vertical-align: top;
">
    {value}
</td>
"""
        )

    return f"""
    <tr>
        {''.join(cells)}
    </tr>
    """