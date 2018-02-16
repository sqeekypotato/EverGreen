from pandas import read_csv
from io import StringIO

# takes the file, fixes it and returns a dataframe
def fixQuotesForCSV(file):
    tempdata = StringIO()
    for line in file:
        line = line.decode('utf-8')
        line = line.replace(r' "', r" '")
        line = line.replace(r'" ', r"' ")
        tempdata.write(line)
    finaldata = StringIO(tempdata.getvalue())
    df = read_csv(finaldata, header=None, sep=',', quotechar='"')
    return df.to_json()

# converts a float to an int
def convertToInt(numString):
    try:
        x = float(numString)
        x = x*100
        x = int(x)
        return x
    except:
        return 0

# returns a dict that has the format dict['recordNumber']['tag'] = tagValue
def buildTagDict(resultsDict):
    returnDict = {}
    for transKey, value in resultsDict.items():
        if value:
            if transKey != 'csrfmiddlewaretoken':
                temp = transKey.split("_")
                type = temp[0]
                record = str(temp[1])
                if record not in returnDict.keys():
                    returnDict[record] = {}
                    returnDict[record][type] = value
                else:
                    returnDict[record][type] = value

    return returnDict