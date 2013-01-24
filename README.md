#ChBE Recruitment Schedule Maker

**v1.0 by Peter Winter**
**v2.0 by Patrick Fuller**

A script to optimize recruit-professor meetup schedules over Northwestern Chemical Engineering recruitment weekends.

Usage
-----

* Update all the tabs in `schedule_input.xlsx`.
* Edit the words in `recruit_schedule_template.tex` to say what you want. It looks code-y, but the parts you want to edit should be easy to find.
* Run `python src/main.py`. You might need to get a coder friend to explain what that means.

For developers
--------------

* Python dependencies: `pip install numpy openpyxl`
* LaTeX dependency: `apt-get install texlive` (replace `apt-get` with `port` or `brew` if you have a mac or `yum` if you have a neck beard)
* The bulk of the logic is in `algorithms.py`. If you want to improve the approach, I think a smart brute force algorithm would work best. The current approach is a lazy attempt at that. Keep in mind that the solution space is not smooth, so things like genetic algorithms don't work too well (I tried).
* There's potential to improve the scoring of schedules.
* Runner schedules could be automatically generated fairly easily.
