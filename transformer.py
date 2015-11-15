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
    for line in f:
        values = line.split(',')
        data.append(values)
        for valIndex in range(len(values)):
            # Add to set for unique values
            if values[valIndex].strip() != "":
                uniques[valIndex] = uniques[valIndex].union([values[valIndex].strip()])
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
def WriteHeaderBlock(file, headers, uniques):
    init_comments = "%1. Title: Car Crash Data\n%\n%2. Sources: Nicholas Livadas, Oct. 8, 2015\n%\n%3. Authors: Ryan Lisnoff & Derek Brown\n"
    relation = "@RELATION crash\n\n"
    
    attr_block = []

    # Now we need to make all the different attributes we plan to use
    # Skip QUERYID
    attr_block.append("@ATTRIBUTE CaseNumber NUMERIC\n")
    # Skip REGN_CNTY_CDE
    attr_block.append("@ATTRIBUTE Municipality " + SetToARFFString(uniques[3]) + "\n")
    # Skip MUNITYPE
    # Skip REF_MRKR
    attr_block.append("@ATTRIBUTE AtIntersection {Y,N}\n")
    attr_block.append("@ATTRIBUTE Latitude NUMERIC\n")
    attr_block.append("@ATTRIBUTE Longitude NUMERIC\n")
    attr_block.append("@ATTRIBUTE Date date \"yyyy-MM-dd\"\n")
    attr_block.append("@ATTRIBUTE Time date \"HH:mm\"\n")
    attr_block.append("@ATTRIBUTE CrashType"+ SetToARFFString(uniques[11]) +"\n")
    attr_block.append("@ATTRIBUTE Injuries NUMERIC\n")
    attr_block.append("@ATTRIBUTE Fatalities NUMERIC\n")
    attr_block.append("@ATTRIBUTE NumVehicles NUMERIC\n")
    attr_block.append("@ATTRIBUTE AccidentType"+ SetToARFFString(uniques[15]) +"\n")
    attr_block.append("@ATTRIBUTE CollisionType"+ SetToARFFString(uniques[16]) +"\n")
    # Skip TRAF_CNTL
    attr_block.append("@ATTRIBUTE LightCondition"+ SetToARFFString(uniques[18]) +"\n")
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

# Here is where the datapoints are formatted so that WEKA
# can parse them according to the attributes we defined.
# list<list<>> -> list<string>
def FormatData(data):
    formatted = []
    skip_indeces = [0,2,4,5,17]
    numeric_indeces = [1,7,8,12,13,14]
    for point in data:
        datastring = ""
        for attrIndex in range(len(point)):
            if attrIndex == 9: # Date
                date = point[attrIndex].split('/')
                year = str(int(date[2]) + 2000)
                if(int(date[0]) < 10):
                    month = "0" + date[0]
                else:
                    month = date[0]
                day = date[1]
                datastring += year + "-" + month + "-" + day + ","
            elif attrIndex == 10: # Time
                if point[attrIndex] == "":
                    datastring += "00:00," # If time wasn't recorded, we will make it midnight.
                else:
                    datastring += point[attrIndex] + ","
            elif attrIndex == 20: # No comma
                datastring += "\"" + point[attrIndex].strip() + "\"\n"
            else:
                if attrIndex not in skip_indeces:
                    if attrIndex in numeric_indeces:
                        datastring += point[attrIndex] + ","
                    else:
                        datastring += "\"" + point[attrIndex] + "\","
                
        formatted.append(datastring)
                
    return formatted
    
def TransformToArff():
    headers, uniques, datapoints = GetHeadersUniqueValuesAndData(False)
    arff = open("crashes.arff", "w")
    WriteHeaderBlock(arff, headers, uniques)
    formatted_data = FormatData(datapoints)
    WriteDataBlock(arff, formatted_data)
    arff.close()

TransformToArff()
