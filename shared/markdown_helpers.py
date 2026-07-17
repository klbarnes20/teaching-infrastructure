# =============================================================================
# markdown_helpers.py
#
# Purpose
# -------
# Shared utilities for generating Markdown.
#
# Responsibilities
# ----------------
# - Create common Markdown structures.
# - Standardize formatting across Markdown outputs.
#
# This module SHOULD:
# - Return Markdown strings.
#
# This module should NOT:
# - Load or build teaching data.
# =============================================================================

def add_heading(lines, heading):
    lines.append(f"## {heading}")
    lines.append("")

