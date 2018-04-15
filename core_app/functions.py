from pandas import read_csv
from io import StringIO
import pandas as pd

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

# takes the dataframe an prepares it for display
def prepareDataFrame(dataframe):
    dataframe['date'] = pd.to_datetime(dataframe['date'], format="%Y-%m-%d")

    # id, userID, account, balance, date, description, credit, debit, category, tag, MonthNum, MonthName, Year
    dataframe = dataframe.sort_values('date', ascending=True)
    dataframe['day'] = dataframe['date'].dt.day
    dataframe[['balance', 'credit', 'debit', 'year']] = dataframe[['balance', 'credit', 'debit', 'year']].astype(float)
    dataframe['credit'] = dataframe['credit'].apply(lambda x: x / 100)
    dataframe['debit'] = dataframe['debit'].apply(lambda x: x/-100)
    dataframe['balance'] = dataframe['balance'].apply(lambda x: x / 100)

    return dataframe

# changes data type from numpy.int64 to float so it can be displayed in json
# def fixList(list):
#     import numpy as np
#     result = []
#     for i in list:
#         result.append(i.item())
#     return result

# take an interval and returns the relevent dataframe
def prepareTables(df, interval):
    cdvar = df.groupby([interval])['credit', 'debit'].sum()
    balvar = df.groupby([interval])['balance'].median()
    labelsvar = cdvar.index.values.tolist()
    categoryvar = df.groupby(['category'])['credit', 'debit'].sum()
    tagvar = df.groupby(['tag'])['credit', 'debit'].sum()

    if interval == "MonthName":
        labelsvar = [i.encode('UTF8') for i in labelsvar]
    else:
        labelsvar = [int(i) for i in labelsvar]

    creditList = cdvar['credit'].tolist()
    debitList = cdvar['debit'].tolist()
    balanceList = balvar.tolist()
    labelList = labelsvar
    catListNum = categoryvar['debit'].tolist()
    catListNum = [i * -1 for i in catListNum]
    catListLabel = categoryvar.index.values.tolist()
    catListLabel = [i.encode('UTF8') for i in catListLabel]

    return creditList, debitList, balanceList, labelList, tagvar, catListNum, catListLabel