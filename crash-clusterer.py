# Authors: Ryan Lisnoff and Derek Brown
# Purpose: To try out different clustering algorithms on our crash data

import math
import datetime
# Returns the "distance" between two crashes.
#       0 if completely the same, 1 if completely different
# This is a measurement of similarity between crashes.
# Here we will consider 5 attributes:
#       Date, Time, Injuries, WeatherCondition, and Surface Condition
# Date and time are 25% of the score each, then the other three constitute the rest of the
# similarity measurement.
def CrashDistance(c1, c2):
    score = 0
    if c1.WeatherCondition == c2.WeatherCondition:
        score += (50/3)
    if c1.SurfaceCondition == c2.SurfaceConditions:
        score += (50/3)
    score += (50/3) * (math.fabs(c1.Injuries - c2.Injuries)/ max(c1.Injures, c2.Injuries))
    # multiply how close the dates are by the max score the dates can achieve
    #score += (25) * (1 - (DateDifference(c1.Date, c2.Date) / 182) * -1)) 
    #score += (25) * ()

# Returns the closest difference between two dates, regardless of year
def DateDifference(d1, d2):
    diff = d1-d2
    if diff.days > 182:    
        max_date = max(d1,d2)
        min_date = min(d1,d2)
        max_date += datetime.timedelta(-365)
        diff = min_date - max_date

    return diff

# Returns the difference between two times in minutes
# Max difference between two times is 1439 minutes
def TimeDifference(t1, t2):
    max_t = max(t1,t2)
    min_t = min(t1,t2)
    return ((max_t.hour * 60) + max_t.minute) - ((min_t.hour * 60) + min_t.minute)

t1 = datetime.time(0,0)
t2 = datetime.time(23,59)
print(TimeDifference(t1,t2))
