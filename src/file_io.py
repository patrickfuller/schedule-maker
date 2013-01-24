#!/usr/bin/env python
"""

This file reads from the input .xlsx file and writes output files as
LaTeX and .pdf.

Initializing works in a few steps:
   Try importing openpyxl. If this fails, pip install openpyxl.
   Try opening ../schedule_input.xlsx.
   Assert that all needed sheets are available.
   Try opening ../recruit_schedule_template.tex.

v1.0 - Peter Winter
v2.0 - Patrick Fuller, patrickfuller@gmail.com, 22 Oct 12

"""

import re

# Load appropriate library and file on import
from openpyxl import Workbook
from openpyxl.reader.excel import load_workbook
wb = load_workbook(filename="../schedule_input.xlsx")

# If a sheet doesn't exist, openpyxl returns null. That's dumb. Throw an error.
sheets = ["Recruit Preferences", "Professor Availability",
          "Manual Overrides", "Travel Weights"]
if not set(sheets) <= set(wb.get_sheet_names()):
    raise Exception(("\n\nDon't rename the spreadsheet tabs!\n\n"
                     "The script expects:\n%s\n" % sheets))

# Also, load tex file here so the code will error if something's amiss
tex_template = open("../recruit_schedule_template.tex").read()


def get_recruit_preferences():
    """
    Gets the professor preferences of each recruit from the .xlsx document.
    Returns [{ name: "", preferences: [] }]
    """
    sheet = wb.get_sheet_by_name("Recruit Preferences")
    return [{"name": "%s %s" % (row[1].value, row[0].value),
             "preferences": [r.value for r in row[2:]]}
            for row in sheet.rows[1:]]


def get_professor_availability():
    """
    Gets the availabilities of professors from the .xlsx document
    Returns [{ name: "", cluster: "", is_available: [] }]
    """
    sheet = wb.get_sheet_by_name("Professor Availability")
    return [{"name": row[0].value,
             "cluster": row[1].value,
             "is_available": [r.value in ["Y", "y"] for r in row[2:]]}
            for row in sheet.rows[1:]]


def get_manual_overrides():
    """
    Gets unflexible (recruit, professor, slot) times to add as constraints.
    Returns [{ "recruit": "", "professor": "", "slot": # }]
    """
    sheet = wb.get_sheet_by_name("Manual Overrides")
    return [{"recruit": "%s %s" % (row[1].value, row[0].value),
             "professor": row[2].value,
             "slot": int(row[3].value)}
            for row in sheet.rows[1:]]


def get_travel_weights():
    """
    Gets the travel weight matrix from the .xlsx document
    Returns a nested dict, so d[cluster_1][cluster_2] = weight
    """
    sheet = wb.get_sheet_by_name("Travel Weights")
    columns = [cluster.value for cluster in sheet.rows[0][1:]]

    # Spelling this out, as a nested dictionary comprehension looks meh and
    # this isn't exactly a speed bottleneck
    weights = {}
    for row in sheet.rows[1:]:
        cluster = row[0].value
        costs = [int(cell.value) for cell in row[1:]]
        weights[cluster] = {col: cost for col, cost in zip(columns, costs)}
    return weights


def write_schedule_xlsx(professors, recruits, filepath):
    """
    Writes and saves a .xlsx spreadsheet containing three tabs - Professor
    Schedule, Recruit Schedule, and Recruit Clusters. The first two should be
    self explanatory, and the third helps for assigning runners.
    """

    # Make a workbook object and a row-1 header
    wb = Workbook()
    num_slots = len(professors[0]["slots"])
    header = [""] + ["Slot %d" % (s + 1) for s in range(num_slots)]

    # Make a sheet for the professor schedule
    ws = wb.create_sheet(index=0, title="Professor Schedule")
    ws.append(header)
    for professor in professors:
        ws.append([professor["name"]] + professor["slots"])

    # Make another sheet for the recruit schedule
    ws = wb.create_sheet(index=0, title="Recruit Schedule")
    ws.append(header)
    for recruit in recruits:
        ws.append([recruit["name"]] + recruit["slots"])

    # Make a final sheet showing recruit clusters (helps w/ assigning runners)
    ws = wb.create_sheet(index=0, title="Recruit Clusters")
    ws.append(header)
    for recruit in recruits:
        recruit["clusters"] = ["Poster"] * len(recruit["slots"])
        for i, slot in enumerate(recruit["slots"]):
            for professor in professors:
                if professor["name"] == slot:
                    recruit["clusters"][i] = professor["cluster"]
                    break
        ws.append([recruit["name"]] + recruit["clusters"])
    wb.save(filepath)


def write_tex_file(recruit, filepath, panel_activity_first):
    """Writes a .tex file containing a recruit's schedule."""
    # Copy the template object
    tex = tex_template[:]

    # Define replacement logic with a closure
    def tex_repl(match, panel_activity_first):
        """Uses python.re's MatchObject to parse patterns."""
        flag = match.group()[2:-1]
        # The name flag is easy enough
        if flag == "name":
            return recruit["name"]
        # All other flags come with numbers attached
        flag, num = flag.split("_")
        num = int(num) - 1
        # If it's an activity, it's Panel or MRSEC.
        if flag == "activity":
            # If (False, 1) or (True, 2), return MRSEC. Otherwise, panel
            return ("Tour of MRSEC" if panel_activity_first == num else
                    "Graduate Student Panel Discussion")
        # If it's a slot, extract the number and return that
        elif flag == "slot":
            prof = recruit["slots"][num]
            return "Meet with Professor " + prof if prof else "Poster session"
        # Exceptions for the assholes
        raise Exception("A given $(*) .tex flag is not supported!")

    # Iterate through and replace flags
    # This regex is saying "$(*)" with a lot of escaped characters
    tex = re.sub("\$\(\w+\)", lambda s: tex_repl(s, panel_activity_first), tex)

    with open(filepath, 'w') as outfile:
        outfile.write(tex)

if __name__ == "__main__":
    print get_recruit_preferences()
    print get_professor_availability()
    print get_manual_overrides()
    print get_travel_weights()
