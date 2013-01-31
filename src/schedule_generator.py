#!/usr/bin/env python
"""

Main file for making schedules.

v1.0 - Peter Winter
v2.0 - Patrick Fuller, patrickfuller@gmail.com, 22 Oct 12

"""

import re
import os
import subprocess

import file_io
import algorithms

import sys

# Give terminal-types the ability to set iterations externally
iterations = 100
for i, arg in enumerate(sys.argv):
    if arg == "--iterations":
        iterations = int(sys.argv[i + 1])

# All of these read from the input .xlsx file
recruits = file_io.get_recruit_preferences()
professors = file_io.get_professor_availability()
overrides = file_io.get_manual_overrides()
travel_weights = file_io.get_travel_weights()

# Find recruitless professors and students requesting weird people
requests = set([professor for recruit in recruits
               for professor in recruit["preferences"]]) - set([None])
available = set([professor["name"] for professor in professors])

# Print the professors without recruits and missing requested professors
unavailable = requests - available
print "\nUnrequested professors:\n    " + "\n    ".join(available - requests)
print "\nProfessors not on schedule:\n    " + "\n    ".join(unavailable)

# Remove unavailable professors from appropriate lists
professors = filter(lambda p: p["name"] not in unavailable, professors)
for recruit in recruits:
    recruit["preferences"] = set(recruit["preferences"]) - set(unavailable)

# Sort professors by flyness and print (a tribute to Peter's flyest_prof)
for professor in professors:
    professor["recruits"] = [recruit["name"] for recruit in recruits if
                             professor["name"] in recruit["preferences"]]
professors.sort(key=lambda p: len(p["recruits"]), reverse=True)

print "\nMatched professors (sorted by number of requests):"
for professor in professors:
    recruit_string = ", ".join(professor["recruits"])
    print "    " + professor["name"].ljust(15) + recruit_string

# Generate a schuedle. Change here to implement different algorithms.
algorithm = algorithms.RandomizedAlgorithm(professors, recruits,
                                           travel_weights, overrides)
professors, recruits = algorithm.run(iterations=iterations,
                                     free_recruit_slots=1)
print algorithm.generate_test_results()

# Sort by name for output
professors.sort(key=lambda p: p["name"])
recruits.sort(key=lambda r: r["name"].split(' ')[1])

# Write an excel doc containing the schedule
print("\nGenerating output spreadsheet...")
file_io.write_schedule_xlsx(professors, recruits, "../generated_schedule.xlsx")

print("\nDone!")
