# Authors: Ryan Lisnoff & Derek Brown
# Purpose: Transforms our crash data CSV into something WEKA can recognize

# Format of attributes in order:
# CaseNumber Numeric
# Municipality Nominal {}
# AtIntersection Numeric (0 is N, 1 is Y)
# Latitude Numeric
# Longitude Numeric
# Date Date
# Time Date
# CrashType Nominal {}
# Injuries Numeric
# Fatalities Numeric
# NumVehicles Numeric
# AccidentType Nominal {}
# CollisionType Nominal {}
# TrafficCtrl Nominal {}
# LightCondition Numeric (Grade best to worst, 0 in middle is unknown)
# WeatherCondition Numeric (Grade best to worst, 0 in middle is unknown)
# RoadCondition Numeric (Grade best to worst)

# Takes ~60 seconds to run, be patient!
# If write=true, write out unique values
# Returns all possible values for each column, as well as the headers for the columns
# And all the data, that way we don't need to pass through twice
def GetHeadersUniqueValuesAndData(write):
    # These are the indexes that we want to look at unique values for
    # to potentially reduce them to numeric attributes
    indexes_of_interest = [3,11,15,16,17,18,19,20]
    data = []
    f = open("2015UpdateJan-Feb2010-March2013-Dec2014.csv")
    headers = next(f).split(',')
    uniques = [set() for i in range(len(headers))]
    print("Reading in values...")
    num_lines = 0
    next_prompt = 1000
    for line in f:
        if num_lines >= next_prompt:
            print("Read "+ str(num_lines) +" lines...")
            next_prompt += 1000
        values = line.split(',')
        data.append(values)
        for valIndex in range(len(values)):
            # Add to set for unique values
            if values[valIndex].strip() != "":
                uniques[valIndex] = uniques[valIndex].union([values[valIndex].strip()])
        num_lines += 1
    print("Reading done! Read in "+ str(num_lines) +" lines.")
    if(write):
        print("Writing out unique values...")
        for uIndex in range(len(uniques)):
            if uIndex in indexes_of_interest:
                # Output a file with unique vals for that attribute
                newFileName = "Unique_" + headers[uIndex]
                newFile = open(newFileName, 'w')
                for uniqueval in uniques[uIndex]:
                    newFile.write(uniqueval.strip() + "\n")
    f.close()
    
    return headers, uniques, data

# Converts set string to ARFF notation for WEKA
# This is used for nominal attributes
# set() -> string
def SetToARFFString(s):
    base_string = s.__str__()
    return base_string.replace("'","\"").replace(", ", ",")
    
# Writes initial header to ARFF file
# This includes initial comments, relation and attributes
# If you plan on skipping an attribute, make sure the @ATTRIBUTE here is commented out
def WriteHeaderBlock(file, headers, uniques):
    init_comments = "%1. Title: Car Crash Data\n%\n%2. Sources: Nicholas Livadas, Oct. 8, 2015\n%\n%3. Authors: Ryan Lisnoff & Derek Brown\n"
    relation = "@RELATION crash\n\n"
    skip_indeces = [0,1,2,3,4,5,6,7,8,11,15,16,17,18]
    attr_block = []

    # Now we need to make all the different attributes we plan to use
    # Skip QUERYID
    #attr_block.append("@ATTRIBUTE CaseNumber NUMERIC\n")
    # Skip REGN_CNTY_CDE
    #attr_block.append("@ATTRIBUTE Municipality " + SetToARFFString(uniques[3]) + "\n")
    # Skip MUNITYPE
    # Skip REF_MRKR
    #attr_block.append("@ATTRIBUTE AtIntersection {Y,N}\n")
    #attr_block.append("@ATTRIBUTE Latitude NUMERIC\n")
    #attr_block.append("@ATTRIBUTE Longitude NUMERIC\n")
    attr_block.append("@ATTRIBUTE Date date \"MM-dd\"\n")
    attr_block.append("@ATTRIBUTE Time date \"HH:mm\"\n")
    #attr_block.append("@ATTRIBUTE CrashType"+ SetToARFFString(uniques[11]) +"\n")
    attr_block.append("@ATTRIBUTE Injuries NUMERIC\n")
    attr_block.append("@ATTRIBUTE Fatalities NUMERIC\n")
    #attr_block.append("@ATTRIBUTE NumVehicles NUMERIC\n")
    #attr_block.append("@ATTRIBUTE AccidentType"+ SetToARFFString(uniques[15]) +"\n")
    #attr_block.append("@ATTRIBUTE CollisionType"+ SetToARFFString(uniques[16]) +"\n")
    # Skip TRAF_CNTL
    #attr_block.append("@ATTRIBUTE LightCondition"+ SetToARFFString(uniques[18]) +"\n")
    attr_block.append("@ATTRIBUTE WeatherCondition"+ SetToARFFString(uniques[19]) +"\n")
    attr_block.append("@ATTRIBUTE SurfaceCondition"+ SetToARFFString(uniques[20]) +"\n")
    
    file.write(init_comments)
    file.write(relation)
    for attr in attr_block:
        file.write(attr)

def WriteDataBlock(file, data):
    file.write("\n@DATA\n")
    for datapoint in data:
        file.write(datapoint)

# Either returns the time unchanged, or if it has AM/PM, convert to 24 hour
# WEKA needs it in format HH:mm
def ConvertTime(time):
    if(time == ""):
        return "00:00"
    check = time.split()
    if(len(check) > 1):
        hour,minute = check[0].split(':')[0],check[0].split(':')[1]
        if(check[1] == "AM"):
            if hour == "12":
                hour = "00"   
        else:
            if hour != "12":
                hourAsInt = int(hour) + 12
                hour = str(hourAsInt)
        return hour + ":" + minute

    return time

# Converts the slash style date into a date we can use
# Here we drop the year because we're not so interested in it
# WEKA needs it in form MM:dd
def ConvertDate(date):
    split_date = date.split('/')
    month = split_date[0]
    day = split_date[1]
    if(int(split_date[0]) < 10):
        if(len(split_date[0]) < 2):
            month = "0" + split_date[0]
    converted_date = month + "-" + day
    if converted_date == "02-29": # Weka doesn't like leap days
        converted_date = "02-28"

    return converted_date

# Here is where the datapoints are formatted so that WEKA
# can parse them according to the attributes we defined.
# Anything in skip_indeces must also be commented out in the @ATTRIBUTE section!
# list<list<>> -> list<string>
def FormatData(data):
    print("Cleaning data...")
    formatted = []
    skip_indeces = [0,1,2,3,4,5,6,7,8,11,14,15,16,17,18]
    numeric_indeces = [1,7,8,12,13,14]
    num_removed = 0
    for point in data:
        skip_this_point = False
        datastring = ""
        for attrIndex in range(len(point)):
            if attrIndex not in skip_indeces:
                if attrIndex == 9: # Date
                    datastring += ConvertDate(point[attrIndex]) + ","
                elif attrIndex == 10: # Time
                    datastring += ConvertTime(point[attrIndex]) + ","
                elif attrIndex == 20: # No comma
                    datastring += "\"" + point[attrIndex].strip() + "\"\n"
                elif attrIndex == 3 and point[attrIndex] == "":
                    skip_this_point = True
                    num_removed += 1
                    break
                else:
                    if attrIndex in numeric_indeces:
                        datastring += point[attrIndex] + ","
                    else:
                        datastring += "\"" + point[attrIndex] + "\","
                        
        if not skip_this_point:
            formatted.append(datastring)
    print("Cleaning done. Removed "+ str(num_removed) + " points. New Total points: "+ str(len(formatted)))    
    return formatted

# Writes the formatted data to a new CSV file
def WriteCleanCSV(data):
    print("Writing to cleaned CSV file")
    filename = "cleaned.csv"
    file = open(filename, "w")
    headers = ["Date", "Time", "Injuries", "Fatalities", "WeatherCondition", "Surface Condition"]
    for header_index in range(len(headers)):
        file.write(headers[header_index])
        if(header_index == len(headers) - 1):
            file.write("\n")
        else:
            file.write(",")

    for point_index in range(len(data)):
        file.write(str(data[point_index]))

    file.close()
    print("Finished writing to cleaned.csv")

def WriteARFF(headers, uniques, formatted_data):
    arff = open("crashes.arff", "w")
    WriteHeaderBlock(arff, headers, uniques)
    WriteDataBlock(arff, formatted_data)
    arff.close()
    print("Finished writing to crashes.arff...")
    
def Main():
    print("Starting transformer!")
    headers, uniques, datapoints = GetHeadersUniqueValuesAndData(False)
    formatted_data = FormatData(datapoints)
    WriteARFF(headers, uniques, formatted_data)
    WriteCleanCSV(formatted_data)
    print("Done!")
    
Main()
