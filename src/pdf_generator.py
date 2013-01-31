#!/usr/bin/env python
"""

Generates .pdf files for recruits from an .xlsx spreadsheet made with
`schedule_generator.py`

v1.0 - Peter Winter
v2.0 - Patrick Fuller, patrickfuller@gmail.com, 22 Oct 12

"""
import os
import subprocess
import re

import file_io

recruits = file_io.read_schedule_xlsx("../generated_schedule.xlsx")

# Specify and create a folder for the .tex files
tex_directory = "../output_latex"
if not os.path.exists(tex_directory):
    os.makedirs(tex_directory)
os.chdir(tex_directory)

# Add .tex files to the folder and subprocess a .pdf converter
for i, recruit in enumerate(recruits):
    filepath = "%s.tex" % re.sub(" ", "_", recruit["name"].lower())
    file_io.write_tex_file(recruit, filepath)
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
