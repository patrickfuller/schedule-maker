#!/usr/bin/env python
"""

Main file for making schedules.

v1.0 - Peter Winter
v2.0 - Patrick Fuller, patrickfuller@gmail.com, 22 Oct 12

"""

import numpy as np
from random import choice, shuffle
from itertools import product
import re
import os
import subprocess

# For clarity, I separated the logic into multiple files
import file_io
import algorithms

# Read the input file for parameters
recruits = file_io.get_recruit_preferences()
professors = file_io.get_professor_availability()
overrides = file_io.get_manual_overrides()
travel_weights = file_io.get_travel_weights()

# Find recruitless professors and students requesting weird people
requests = set([prof for recruit in recruits for prof in recruit["preferences"]])
available = set([professor["name"] for professor in professors])

# Print the professors without recruits
print "\nUnrequested professors:"
for recruitless_professor in available - requests:
    print "    %s" % recruitless_professor
 
# Print the requested professors who weren't in the .xlsx file
print "\nRequested professors not on schedule:"
for missing_professor in requests - available:
    print "    %s" % missing_professor

# Remove unavailable professors from the list
unavailable = list(requests - available)
professors = filter(lambda p: p["name"] not in unavailable, professors)

# Remove them from recruit preferences, as well
for recruit in recruits:
    recruit["preferences"] = list(set(recruit["preferences"]) - set(unavailable))

# Sort professors by flyness (a tribute to flyest_prof)
for professor in professors:
    professor["recruits"] = [recruit["name"] for recruit in recruits if
                             professor["name"] in recruit["preferences"]]
professors.sort(key=lambda p: len(p["recruits"]), reverse=True)

# Print the matched professors
print "\nMatched professors (sorted by number of requests):"
for professor in professors:
    print "    " + professor["name"].ljust(15) + ", ".join(professor["recruits"])
    
# Run the algorithm
algorithm = algorithms.RandomizedAlgorithm(professors, recruits, 
                                           travel_weights, overrides)
professors, recruits = algorithm.run(iterations=1000)
print algorithm.generate_test_results()

# Sort by name for output
professors.sort(key=lambda p: p["name"])
recruits.sort(key=lambda r: r["name"].split(' ')[1])

# Write an excel doc containing the schedule
print("\nGenerating output files...")
file_io.write_schedule_xlsx(professors, recruits, "../generated_schedule.xlsx")

# Specify and create a folder for the .tex files
tex_directory = "../output_latex"
if not os.path.exists(tex_directory):
    os.makedirs(tex_directory)
os.chdir(tex_directory)

# Add .tex files to the folder and subprocess a .pdf converter
for i, recruit in enumerate(recruits):
    filepath = "%s.tex" % re.sub(" ", "_", recruit["name"])
    file_io.write_tex_file(recruit, filepath, panel_activity_first=(i%2==0))
    subprocess.call(["pdflatex", "-interaction=batchmode", filepath])
    
# Clean up the latex-to-pdf mess
pdf_directory = "../output_pdf"
if not os.path.exists(pdf_directory):
    os.makedirs(pdf_directory)
for filename in os.listdir(tex_directory):
    filetype = filename.split(".")[-1]
    # Move .pdfs to their own directory
    if filetype == "pdf":
        os.rename("%s/%s" % (os.getcwd(), filename), 
                  "%s/%s/%s" % (os.getcwd(), pdf_directory, filename))
    # Remove these log files
    elif filetype in ["aux", "log"]:
        os.remove("%s/%s" % (os.getcwd(), filename))

print("\nDone!")
