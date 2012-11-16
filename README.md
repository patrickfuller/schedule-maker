recruit-schedule-maker
======================

###v1.0 - Peter Winter
###v2.0 - Patrick Fuller, patrickfuller@gmail.com, 22 Oct 12

A script to optimize recruit-professor meetup schedules over Northwestern Chemical Engineering recruitment weekends.

For users:
    - Update all the tabs schedule_input.xlsx.
    - Edit the words in recruit_schedule_template.tex to say what you want. It
      looks code-y, but the parts you want to edit should be easy to find.
    - Run the .exe. If that doesn't exist, run main.py in src.

For developers:
    - The code is dependent on two python libraries: numpy and openpyxl. You
      can "pip install" both of these.
    - The pdf generation is dependent on pdflatex, which you can get with 
      "apt-get install texlive" (Linux) or "port install texlive" (Mac)
    - The bulk of the logic is in algorithms.py. If you want to improve the
      approach, I think a smart brute force algorithm would work best. The
      current approach is a lazy attempt at that. Keep in mind that the solution
      space is not smooth, so things like GA's don't work too well (I tried).
