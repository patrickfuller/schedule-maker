#ChBE Recruitment Schedule Maker

**v1.0 by Peter Winter**
**v2.0 by Patrick Fuller**

A script to optimize recruit-professor meetup schedules over Northwestern Chemical Engineering recruitment weekends.

Usage
-----

* Update all the tabs in `schedule_input.xlsx`.
* Edit the words in `recruit_schedule_template.tex` to say what you want. It looks code-y, but the parts you want to edit should be easy to find.
* To generate a "best" schedule, run `schedule_generator.py`. You might need to get a coder friend to explain what that means.
* Go into the generated .xlsx file and edit the recruit schedule as you see fit. Specifically, look to match up non-requested professors to recruits by research field.
* After doing this, run `schedule_updater.py` to update the other tabs in the schedule spreadsheet.
* When happy with the schedule, run `pdf_generator.py` to create fancy schedules for all the recruits.

Dependencies
------------

* Python dependencies: `pip install numpy openpyxl`
* LaTeX dependency: `apt-get install texlive` (replace `apt-get` with `port` or `brew` if you have a mac or `yum` if you have a neck beard)

For developers
--------------

* The bulk of the logic is in `algorithms.py`. If you want to improve the approach, I think a smart brute force algorithm would work best. The current approach is a lazy attempt at that. Keep in mind that the solution space is not smooth, so things like genetic algorithms don't work too well (I tried).
* There's potential to improve the scoring of schedules.
* Runner schedules could be automatically generated fairly easily.
