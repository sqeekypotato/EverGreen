from io import StringIO
import pandas as pd

import calendar

from .models import Transaction, Tags

# takes the file, fixes it and returns a dataframe
def fixQuotesForCSV(file):
    tempdata = StringIO()
    for line in file:
        line = line.decode('utf-8')
        line = line.replace(r' "', r" '")
        line = line.replace(r'" ', r"' ")
        tempdata.write(line)
    finaldata = StringIO(tempdata.getvalue())
    df = pd.read_csv(finaldata, header=None, sep=',', quotechar='"')
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

# adds dataframe to the account
def add_df_to_account(dataframe, request, userAccount, dateLocation, creditLocation, debitLocation, descripLocation):

    dataframe[dateLocation] = pd.to_datetime(dataframe[dateLocation])  # changes string to date format
    dataframe = dataframe.fillna(0)  # replaces NaN with 0
    records_added = 0
    for index, row in dataframe.iterrows():
        credit = row[creditLocation] # these set choose the proper columns in case of different layouts
        debit = row[debitLocation]
        credit = convertToInt(credit)
        debit = convertToInt(debit)
        monthNum = row[dateLocation].month
        year = row[dateLocation].year
        monthName = calendar.month_abbr[monthNum]
        if debit < 0:
            debit = debit * -1
        balance = userAccount.balance + credit - debit
        date = row[dateLocation].to_pydatetime().date()
        description = row[descripLocation]
        trans = Transaction(
            user=request.user,
            account=userAccount,
            balance=balance,
            date=date,
            description=description,
            credit=credit,
            debit=debit,
            monthNum=monthNum,
            monthName=monthName,
            year=year
        )
        trans.save()  # adds record to the database
        records_added += 1

    return records_added

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
def fixList(list):
    import numpy as np
    result = []
    for i in list:
        result.append(i.decode("utf-8"))
    return result

# takes a dataframe and returns multiple dicts that can be converted to json
def prepare_table(df, interval):
    # general income chart
    credit_vals = df.groupby([interval])['credit'].sum()
    debit_vals = df.groupby([interval])['debit'].sum()
    monthName = df.groupby([interval])['monthName'].unique().astype(str)
    balance_vals = df.groupby([interval])['balance'].median()
    labels = credit_vals.index.tolist()
    labels = [str(x) for x in labels]

    # category chart
    cat_list = df.category.unique()
    cat_dict = {}
    for category in cat_list:
        result = df.loc[df['category'] == category, 'debit'].sum()
        result = result * -1 #this is put in so the chart shows posative values.  It didn't like negative ones
        cat_dict[category] = result
    cat_labels = [str(x) for x in cat_list]

    # tag chart
    tag_list = df.tag.unique()
    tag_dict = {}
    for tag in tag_list:
        result = df.loc[df['tag'] == tag, 'debit'].sum()
        result = result*-1 #this is put in so the chart shows posative values.  It didn't like negative ones
        tag_dict[tag] = result
    tag_labels = [str(x) for x in tag_list]

    new_df = {'credits':credit_vals.tolist(),
              'debits':debit_vals.tolist(),
              'monthName':monthName.tolist(),
              'balance':balance_vals.tolist(),
              'labels':labels,
              'cat_labels':cat_labels,
              'cat_vals':cat_dict,
              'tag_labels':tag_labels,
              'tag_vals':tag_dict,
              }

    return new_df

# checks other records in the database and tags them
def check_other_records(**kwargs):
    print('new thread!')
    other_records = Transaction.objects.filter(description=kwargs['description'], category=None).all()
    print('{} records found to append category to'.format(len(other_records)))
    for record in other_records:
        print(record.id)
        record.category = kwargs['category']
        record.tag = kwargs['tag']
        record.save()
        print('{} id saved with cat {}'.format(record.id, record.category))

# checks if cat and tag are in database (as a pair) and if not, adds them
def add_tags_to_database(cat, tag, user):
    add_tag = True
    other_tags = Tags.objects.filter(category=cat).all()
    print('{} records found with {} category'.format(len(other_tags), cat))
    for record in other_tags:
        if record.tag == tag:
            add_tag = False
    if add_tag:
        new_tag = Tags(category=cat, tag=tag, user=user)
        new_tag.save()