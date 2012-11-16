#!/usr/bin/env python
"""

Classes that algorithmically generate semi-optimized schedules from inputs.

v1.0 - Peter Winter
v2.0 - Patrick Fuller, patrickfuller@gmail.com, 22 Oct 12

"""

import numpy as np
from itertools import product
from random import shuffle
                           
class RandomizedAlgorithm:
    """
    Randomly iterating through students, professors, and time slots, this
    algorithm fills schedules analogous to how one would do it by hand. First,
    it gives students their preferences, then it fills in the blanks randomly.
    
    The algorithm iterates through this process a specified number of times,
    scoring the quality of each proposed schedule. The best one is returned.
    """

    def __init__(self, professors, recruits, travel_weights, overrides=[]):
        """ Converts the human-readable objects into iterable formats """
        # Fast-access integer index professor availability array
        self.availability = np.array([professor["is_available"] 
                            for professor in professors], dtype=np.int8)

        # Fast-access integer index recruit preferences array
        self.preferences = np.array([[professor["name"] in recruit["preferences"]
                           for recruit in recruits] for professor in professors],
                           dtype=np.int8)

        # Store lengths and ranges so we don't keep recalculating
        self.num_preferences = np.sum(self.preferences)
        self.num_professors = len(professors)
        self.num_recruits = len(recruits)
        self.num_slots = len(professors[0]["is_available"])
        self.prof_ints = range(self.num_professors)
        self.rec_ints = range(self.num_recruits)
        self.slot_ints = range(self.num_slots)
        
        # Initialize arrays for holding time-slot sorted information
        self.professors = professors
        self.recruits = recruits
        for recruit in self.recruits:
            recruit["slots"] = [None] * self.num_slots
        for professor in self.professors:
            professor["slots"] = [None] * self.num_slots
            
        # Setting up travel_weights to be a [prof_1, prof_2] lookup
        self.travel_weights = np.zeros((self.num_professors,)*2, dtype=np.int8)
        for p1, p2 in product(self.prof_ints, self.prof_ints):
            # Get corresponding clusters
            c1 = professors[p1]["cluster"]
            c2 = professors[p2]["cluster"]
            # Look up the travel weight between clusters and save
            self.travel_weights[p1, p2] = travel_weights[c1][c2]
        
        # Reverse search overrides for int representation
        self.overrides = []
        for override in overrides:
            for p in self.prof_ints:
                if professors[p]["name"] == override["professor"]:
                    break
            for r in self.rec_ints:
                if recruits[r]["name"] == override["recruit"]:
                    break
            s = override["slot"] - 1
            self.overrides.append((p, r, s))
        
    def run(self, iterations=100, free_recruit_slots=1):
        """ Generates a best schedule and returns updated objects """
        # Place generate_schedule in a generator
        generator = (self._generate_schedule(free_recruit_slots) 
                     for i in range(iterations))

        # Exhaust it and save the best schedule
        print "\nGenerating and testing candidate schedules..."
        best_score = 1000
        for schedule in generator:
            score = self._rank_schedule(schedule)
            if score < best_score:
                print "Schedule with score %d found" % score 
                self.schedule = schedule
                best_score = score
        return self._to_objects(self.schedule)
        
    def generate_test_results(self):
        """ Returns a string containing various metrics """
        
        # Generate a bunch of random data
        self.test = { "recruits": self.num_recruits,
                      # Number of fulfilled requests
                      "fulfilled": sum((self.preferences[p,r]
                                   and r in self.schedule[p, s, :] for p, r, s 
                                   in product(self.prof_ints, self.rec_ints, 
                                   self.slot_ints))),
                      # Total requests
                      "requested": self.num_preferences,
                      # Number of students meeting all requested professors
                      "all_met": sum([set(r["preferences"])<=set(r["slots"]) for r 
                                 in self.recruits]),
                      # Double meetings
                      "double_meetings": np.sum(self.schedule[:, :, 1] != -1),
                      # The most double meetings a recruit has
                      "max_double": max([np.sum(self.schedule[:, :, 1] == r) for r 
                                    in self.rec_ints]),
                      # Unfilled recuit slots
                      "recruit_unfilled": sum([not r["slots"][s] for s 
                                          in self.slot_ints for r 
                                          in self.recruits]),
                      # Total recruit slots
                      "recruit_slots": self.num_recruits * self.num_slots,
                      # Unfilled available professor slots
                      "prof_unfilled": sum([p["slots"][s] == None 
                                       and p["is_available"][s] for s
                                       in self.slot_ints for p 
                                       in self.professors]),
                      # Total professor slots
                      "prof_slots": sum([sum(p["is_available"]) for p 
                                    in self.professors])
                    }
        
        # Format string and return
        return ("\nTest Results:\n"
               "Number of recruits visiting this weekend: %(recruits)d\n"
               "Recruit requests fulfilled: %(fulfilled)d/%(requested)d\n"
               "Recruits meeting all requested profs: %(all_met)d\n"
               "Number of double meetings: %(double_meetings)d\n"
               "Most double meetings for a recruit: %(max_double)d\n"
               "Unfilled recruit slots: %(recruit_unfilled)d/%(recruit_slots)d\n"
               "Unfilled professor slots: %(prof_unfilled)d/%(prof_slots)d\n") \
               % self.test
                
    def _to_objects(self, schedule):
        """ Reads the array schedule and puts into human-readable objects """
        
        # Initialize arrays for holding time-slot sorted information
        for person in self.recruits + self.professors:
            person["slots"] = [""] * self.num_slots
        
        # Iterate through index accessors to int8 numpy array
        # This is for the primary schedule
        for p, s in product(self.prof_ints, self.slot_ints):
            r = schedule[p, s, 0]
            # -1 is used as a placeholder for empty slots
            if r == -1:
                continue
            # Fill "slots" lists of professors and recruits
            self.professors[p]["slots"][s] = self.recruits[r]["name"]
            self.recruits[r]["slots"][s] = self.professors[p]["name"]
            
        # This is for double meetings
        for p, s in product(self.prof_ints, self.slot_ints):
            r = schedule[p, s, 1]
            # -1 is used as a placeholder for empty slots
            if r == -1:
                continue
            # Fill "slots" lists of professors and recruits
            self.professors[p]["slots"][s] += ", " + self.recruits[r]["name"]
            self.recruits[r]["slots"][s] = self.professors[p]["name"]        
        
        return self.professors, self.recruits
        
    def _generate_schedule(self, free_recruit_slots):
        """ 
        Generates a schedule based off of random iteration. Incorporates
        double meetings.
        
        Returns a 3D numpy array of professor_indices x time_slots x 2
        """
        
        # These arrays are int representations of availabilites
        prof_avail = self.availability.copy()
        recruit_prefs = self.preferences.copy()
        recruit_avail = np.ones((self.num_recruits, self.num_slots), dtype=np.int8)
        
        # Initialize schedule as all -1's
        schedule = np.zeros((self.num_professors, self.num_slots, 2), 
                            dtype=np.int8) - 1
        
        # Useful functions, intended to help readability
        # Checks if professor and recruit are both available at a given slot
        both_available = lambda p, r, s: recruit_avail[r, s] and prof_avail[p, s]
        # Checks if a recruit has already been scheduled with a professor
        is_conflict = lambda p, r, s: r in schedule[p, :, :]
        # Checks if every available professor slot is booked
        professors_full = lambda: np.sum(prof_avail) == 0
        # Counts the number of open slots in a recruit's schedule
        recruit_full = lambda r: np.sum(recruit_avail[r,:]) <= free_recruit_slots
        
        def try_to_book(p, r, s, double_booking=False):
            """ If the slot doesn't conflict, book it by updating arrays """
            if both_available(p, r, s) and not is_conflict(p, r, s) \
            and not recruit_full(r):
                schedule[p, s, double_booking] = r
                recruit_prefs[p, r] = 0
                prof_avail[p, s] -= 1
                recruit_avail[r, s] = 0
        
        # Round 1: Book overrides
        for p, r, s in self.overrides:
            try_to_book(p, r, s)

        # Round 2: Randomly iterate through (professor, recruit, slot) combos
        # and book meetings preferred by recruits
        shuffle(self.prof_ints); shuffle(self.rec_ints); shuffle(self.slot_ints)
        for p, r, s in product(self.prof_ints, self.rec_ints, self.slot_ints):
            if recruit_prefs[p, r]:
                try_to_book(p, r, s)
        
        # Round 3: Fill remaining slots randomly, making sure that each recruit
        # has "free_recruit_slots" amount of free slots (for poster sessions)
        shuffle(self.prof_ints); shuffle(self.rec_ints); shuffle(self.slot_ints)
        for p, r, s in product(self.prof_ints, self.rec_ints, self.slot_ints):
            try_to_book(p, r, s)
            
        # Round 4: Double booking. Reset professor availability. Go by recruit 
        # preferences first.
        prof_avail = self.availability.copy()
        shuffle(self.prof_ints); shuffle(self.rec_ints); shuffle(self.slot_ints)
        for p, r, s in product(self.prof_ints, self.rec_ints, self.slot_ints):
            if recruit_prefs[p, r]:
                try_to_book(p, r, s, double_booking=True)
                
        # Round 5: Fill double booking slots until recruits are all full. Play
        # with "free_recruit_slots" to favor poster presentations over more
        # double bookings
        shuffle(self.prof_ints); shuffle(self.rec_ints); shuffle(self.slot_ints)
        for p, r, s in product(self.prof_ints, self.rec_ints, self.slot_ints):
            try_to_book(p, r, s, double_booking=True)
                
        return schedule
        
    def _generate_recruit_schedule(self, schedule):
        """ 
        Generates a numpy array recruit schedule from a double-meeting-enabled
        professor schedule data structure.
        
        Returns a 2D numpy array of recruit_indices x time_slots
        """
        recruit_schedule = np.zeros((self.num_recruits, self.num_slots), 
                           dtype=np.int8) - 1
        for p, s in product(self.prof_ints, self.slot_ints):
            # If recruit in either regular or double-booked schedule, add
            r = max(schedule[p, s, :])
            # Remember that -1 is the unbooked flag
            if r == -1:
                continue
            recruit_schedule[r, s] = p
        return recruit_schedule
        
    def _rank_schedule(self, schedule):
        """ Ranks schedule quality. Lower is better. """
        
        # Get the schedule from the recruits' perspective. It'll help.
        recruit_schedule = self._generate_recruit_schedule(schedule)
        
        # Count the number of scheduled preferences
        # The professor index p = recruit_schedule[r, s] 
        matched_prefs = sum((self.preferences[recruit_schedule[r, s], r]
                        for r, s in product(self.rec_ints, self.slot_ints)))
        unmatched_prefs = self.num_preferences - matched_prefs
        
        # If the recruit is traveling to/from a poster session, don't add travel
        # weight. Otherwise, look it up from the array.
        get_cost = lambda p1, p2: 0 if -1 in [p1, p2] else self.travel_weights[p1, p2]
        # For a recruit schedule as [p1, p2, ..., pn], get total travel cost
        recruit_cost = lambda r: reduce(get_cost, r)
        # Add up the total travel costs
        travel_cost = sum([recruit_cost(row) for row in recruit_schedule])
        
        # One student with too many double meetings sucks. Weight against that.
        most_doubles = max([np.sum(schedule[:, :, 1] == r) for r in self.rec_ints])
        
        return unmatched_prefs + travel_cost + most_doubles**2
