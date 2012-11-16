recruit-schedule-maker
======================

###v1.0 by Peter Winter, v2.0 by Patrick Fuller

A script to optimize recruit-professor meetup schedules over Northwestern Chemical Engineering recruitment weekends.

Usage
-----

* Update all the tabs in `schedule_input.xlsx`.
* Edit the words in `recruit_schedule_template.tex` to say what you want. It looks code-y, but the parts you want to edit should be easy to find.
* Run the .exe. If that doesn't exist, run `src/main.py`.

For developers
--------------

* Python dependencies: `pip install numpy openpyxl`
* LaTeX dependency: `apt-get install texlive` (replace `apt-get` with `port` or `brew` on mac)
* The bulk of the logic is in `algorithms.py`. If you want to improve the approach, I think a smart brute force algorithm would work best. The current approach is a lazy attempt at that. Keep in mind that the solution space is not smooth, so things like genetic algorithms don't work too well (I tried).
