# Authors: Ryan Lisnoff and Derek Brown
# Purpose: To try out different clustering algorithms on our crash data

import math
import datetime
import random
from collections import Counter
import matplotlib.pyplot as plt

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
        self.NearestPrototypeIX = None

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
    score += (50/3) * (math.fabs(c1.Injuries - c2.Injuries)/ max(c1.Injuries, c2.Injuries))
    # Multiply how close the dates are by the max score the dates can achieve
    score += (25) * (1 - (DateDifference(c1.Date, c2.Date) / 182))
    # Do something similar with the time
    score += (25) * (1 - (TimeDifference(c1.Time, c2.Time) / 1439))
    # Divide by 100, get a measure of SIMILARITY. Thus, need to subtract from 1.
    return 1 - (score / 100)

###############################################################################
# Returns the closest difference between two dates, regardless of year
# ---
# "Closest" example: Jan 1, Oct 1 have a difference of 10 months if you walk
# the calendar in one direction, and 2 months if you go in the other direction.
# This function will return the 2 month time period in this case.
###############################################################################
def DateDifference(d1, d2):
    # Set them to be the same year, since we don't care about year
    d1_fixed = datetime.date(2010, d1.month, d1.day)
    d2_fixed = datetime.date(2010, d2.month, d2.day)
    diff = d1_fixed-d2_fixed
    if diff.days > 182:    
        max_date = max(d1,d2)
        min_date = min(d1,d2)
        max_date += datetime.timedelta(-365)
        diff = min_date - max_date

    return diff.days

###############################################################################
# Returns the difference between two times in minutes
# Max difference between two times is 1439 minutes
###############################################################################
def TimeDifference(t1, t2):
    max_t = max(t1,t2)
    min_t = min(t1,t2)
    return ((max_t.hour * 60) + max_t.minute) - ((min_t.hour * 60) + min_t.minute)

###############################################################################
# Computes the "Average" crash within a cluster
# List<Crash> -> Crash
###############################################################################
def ComputeClusterMean(clust, CurrentCenter):
    if clust == []:
        return CurrentCenter
    
    weather = Counter([x.WeatherCondition for x in clust]).most_common(1)[0][0]
    surface = Counter([x.SurfaceCondition for x in clust]).most_common(1)[0][0]
    injuries =  math.ceil(sum([x.Injuries for x in clust]) / len(clust))
    date = datetime.date.fromordinal(math.ceil(sum([x.Date.toordinal() for x in clust]) / len(clust)))
    time_in_mins = math.ceil(((sum([x.Time.hour for x in clust]) * 60) + (sum([x.Time.minute for x in clust]))) / len(clust))
    time = datetime.time(math.floor(time_in_mins / 60), time_in_mins % 60)
    mean = Crash(weather, surface, injuries, date, time)

    return mean

###############################################################################
# Computes the prototypes for this clustering
# ListL<List<Crash>> -> List<Crash>
###############################################################################
def FindPrototypesForClustering(clustering, OriginalPrototypes):
    prototypes = []
    for i in range(len(clustering)):
        cluster = clustering[i]
        prototype = ComputeClusterMean(cluster, OriginalPrototypes[i])
        prototypes.append(prototype)

    return prototypes

###############################################################################
# Reads in crashes from file
# ASSUMES: csv is in format: Date,Time,Injuries,Fatalities,WeatherCondition,Surface Condition
# String -> List<Crash>
###############################################################################
def ReadInCrashes(filename):
    file = open(filename)
    file.__next__() # toss out the header
    crashes = []
    for line in file:
        data = line.split(',')
        date = datetime.date(2010, int(data[0].split('-')[0]), int(data[0].split('-')[1]))
        time = datetime.time(int(data[1].split(':')[0]), int(data[1].split(':')[1]))
        injuries = float(data[2])
        weat_con = data[4]
        surf_con = data[5]
        crash  = Crash(weat_con, surf_con, injuries, date, time)
        crashes.append(crash)

    return crashes

###############################################################################
# Assigns each crash a nearest prototype from the list of prototypes
# List<Crash> * List<Crash> -> List<Crash>
###############################################################################
def AssignNearestPrototypes(crashes, prototypes):
    for crash in crashes:
        closest_prototype_ix = None
        closest_prototype_distance = float('inf')
        for prototype_ix in range(len(prototypes)):
            dist_to_prototype = CrashDistance(crash, prototypes[prototype_ix])
            if (dist_to_prototype < closest_prototype_distance):
                closest_prototype_ix = prototype_ix
                closest_prototype_distance = dist_to_prototype

        crash.NearestPrototypeIX = closest_prototype_ix

    return crashes


# Recursively goes through the K-Means algorithm on a list of crashes until:
#   The SSE stays the same or gets worse, or
#   The SSE doesn't decrease by at least a certain amount
# List<Crash> * List<Crash>  * int -> List<Crash> , List<Crash>
###############################################################################
def CrashKMeans(crashes, prototypes, previous_sse):

    crashes = AssignNearestPrototypes(crashes, prototypes)
    cur_sse = ComputeSSE(crashes, prototypes)

    if cur_sse >= previous_sse or previous_sse - cur_sse < 1000:
        return crashes, prototypes
    
    clusters = SeparateClusters(crashes, len(prototypes))

    new_prototypes = FindPrototypesForClustering(clusters, prototypes)
    return CrashKMeans(crashes, new_prototypes, cur_sse)

###############################################################################
# Computes the SSE of this clustering by looking at each crash, figuring the
# distance between the crash and its cluster prototype, then adding the square
# of that to a sum.
# List<Crash> * List<Crash> -> int
###############################################################################
def ComputeSSE(crashes, prototypes):
    sse = 0
    for crash in crashes:
        prototype = prototypes[crash.NearestPrototypeIX]
        dist = CrashDistance(crash, prototype)
        sse += (dist ** 2)

    return sse

###############################################################################
# Returns k many random crash prototypes
###############################################################################
def PickStartingPrototypes(k):

    # Seeding the random number generator
    random.seed(None)

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
###############################################################################
# This takes the list of crashes that have been assigned to a cluster and
# creates a List<List<Crash>> that separates out the different crashes to the
# appropriate cluster.
# List<Crash> -> List<List<Crash>
###############################################################################
def SeparateClusters(Crashes, K):
    clusters = []
    for i in range(K):
        clusters.append([])
    
    for crash in Crashes:
        clusters[crash.NearestPrototypeIX].append(crash)
        
    return clusters

###############################################################################
# Graph the results from K-Means algorithm
# List<List<Crash>> -> None
###############################################################################
def GenerateGraph(Crashes):
    scatters = []
    colors = {0: 'r', 1: 'g'}
    for i in range(len(Crashes)):
        cluster = Crashes[i]
        x = []  # Date
        y = []  # Time
        
        for crash in cluster:
            x.append(crash.Date.toordinal())
            t = crash.Time.isoformat()
            (h, m, s) = t.split(":")
            timeNum = int(h) * 3600 + int(m) * 60 + int(s)
            y.append(timeNum)
            
        scatters.append(plt.scatter(x, y, c = colors[i]))
        
    plt.title("Clustered Crash Data")
    plt.xlabel("Date")
    plt.ylabel("Time")

    plt.show()

def main():
    crashes = ReadInCrashes("cleaned.csv")
    initial_prototypes = PickStartingPrototypes(2)
    clustering, prototypes = CrashKMeans(crashes, initial_prototypes, float('inf'))
    for prototype in prototypes:
        print(prototype)
        
    clusters = SeparateClusters(clustering, len(initial_prototypes))    
    GenerateGraph(clusters)

main()