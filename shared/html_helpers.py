def table_row(label, value):
    return f"""
    <tr>
        <th style="text-align: left; padding: 4px 20px 4px 0;">{label}</th>
        <td style="text-align: left; padding: 4px 0;">{value}</td>
    </tr>
    """