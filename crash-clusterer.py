# Authors: Ryan Lisnoff and Derek Brown
# Purpose: To try out different clustering algorithms on our crash data

import math
import datetime
import random

###############################################################################
# Represents a single crash, used class instead of a simple list just because
# it makes the code much easier to read.
###############################################################################
class Crash:
    def __init__(self, wc, sc, inj, date, time):
        self.WeatherCondition = wc
        self.SurfaceCondition = sc
        self.Injuries = inj
        self.Date = date
        self.Time = time

    def __str__(self):
        return str(self.Date) + " @ " + str(self.Time) + " w/ " + str(self.Injuries) + " injuries. " + self.WeatherCondition + "," + self.SurfaceCondition + "."

###############################################################################
# Returns the "distance" between two crashes.
#       0 if completely the same, 1 if completely different
# This is a measurement of similarity between crashes.
# Here we will consider 5 attributes:
#       Date, Time, Injuries, WeatherCondition, and Surface Condition
# Date and time are 25% of the score each,
# then the other three constitute the rest of the similarity measurement.
###############################################################################
def CrashDistance(c1, c2):
    score = 0
    if c1.WeatherCondition == c2.WeatherCondition:
        score += (50/3)
    if c1.SurfaceCondition == c2.SurfaceCondition:
        score += (50/3)
    score += (50/3) * (math.fabs(c1.Injuries - c2.Injuries)/ max(c1.Injures, c2.Injuries))
    # Multiply how close the dates are by the max score the dates can achieve
    score += (25) * (1 - (DateDifference(c1.Date, c2.Date) / 182))
    # Do something similar with the time
    score += (25) * (1 - (TimeDifference(c1.Time, c2.Time) / 1439))
    # Divide by 100, get a measure of SIMILARITY. Thus, need to subtract from 1.
    return 1 - (score / 100)

###############################################################################
# Returns the closest difference between two dates, regardless of year
###############################################################################
def DateDifference(d1, d2):
    diff = d1-d2
    if diff.days > 182:    
        max_date = max(d1,d2)
        min_date = min(d1,d2)
        max_date += datetime.timedelta(-365)
        diff = min_date - max_date

    return diff

###############################################################################
# Returns the difference between two times in minutes
# Max difference between two times is 1439 minutes
###############################################################################
def TimeDifference(t1, t2):
    max_t = max(t1,t2)
    min_t = min(t1,t2)
    return ((max_t.hour * 60) + max_t.minute) - ((min_t.hour * 60) + min_t.minute)

###############################################################################
# Returns k many random crash prototypes
###############################################################################
def PickStartingPrototypes(k):

    # Seeding the random number generator
    random.seed("tingo")

    # Note: OTHER and FOG/SMOKE/SMOG are omitted because these occur very rarely
    weat_cons = ["CLOUDY","CLEAR","RAIN","SLEET/HAIL/FREEZING RAIN","UNKNOWN", "SNOW"]

    # Same with FLOODED WATER, MUDDY, and OTHER, these are very rarely recorded
    surf_cons = ["SNOW/ICE", "WET", "DRY", "SLUSH", "UNKNOWN"]

    # Start and end dates for random date generation, though year is never considered...
    start_date = datetime.date(2010, 1, 1).toordinal()
    end_date = datetime.date(2014, 12, 31).toordinal()

    # Start and end times, in minutes
    start_time = 0
    end_time = 1439

    min_injuries = 0
    max_injuries = 14

    prototypes = []
    for prot_index in range(k):
        weather_ix = random.randint(0, len(weat_cons)-1)
        surface_ix = random.randint(0, len(surf_cons)-1)
        rand_date = datetime.date.fromordinal(random.randint(start_date, end_date))
        rand_time_mins = random.randint(start_time, end_time)
        rand_time = datetime.time(math.floor(rand_time_mins / 60), rand_time_mins % 60)
        rand_inj = random.randint(min_injuries, max_injuries)
        c = Crash(weat_cons[weather_ix], surf_cons[surface_ix], rand_inj, rand_date, rand_time)
        prototypes.append(c)

    return prototypes


p = PickStartingPrototypes(2)
for c in p:
    print(c)
