#!/usr/bin/env python
"""

If a user manually edits the recruit schedule outputted by
`schedule_generator.py`, this will update the corresponding sheets.

"""
import os

import file_io

schedule_file = "../generated_schedule.xlsx"
recruits = file_io.read_schedule_xlsx(schedule_file)
os.remove(schedule_file)
recruit_prefs = file_io.get_recruit_preferences()
professors = file_io.get_professor_availability()

# Merge data structures here for cell coloring
for recruit in recruits:
    for preference in recruit_prefs:
        if preference["name"] == recruit["name"]:
            recruit["preferences"] = preference["preferences"]

# Initialize necessary data stores to allow index access
for professor in professors:
    professor["slots"] = [""] * len(recruits[0]["slots"])
for recruit in recruits:
    recruit["clusters"] = [None] * len(recruit["slots"])

# Map recruit schedule to a professor schedule
for recruit in recruits:
    for i, slot in enumerate(recruit["slots"]):
        for professor in professors:
            if professor["name"] == slot:
                professor["slots"][i] += recruit["name"] + ", "
                recruit["clusters"][i] = professor["cluster"]
                break

# Clean up trailing commas
for professor in professors:
    professor["slots"] = [s[:-2] if s else "" for s in professor["slots"]]

file_io.write_schedule_xlsx(professors, recruits, schedule_file)
