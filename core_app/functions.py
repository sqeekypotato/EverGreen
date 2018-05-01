from io import StringIO
import pandas as pd
import calendar
import datetime
from django_pandas.io import read_frame

from .models import Transaction, Tags, UniversalTags

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
    dataframe[['balance', 'credit', 'debit']] = dataframe[['balance', 'credit', 'debit']].astype(float)
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
    df.sort_values('date')
    credit_vals = df.groupby([interval])['credit'].sum()
    credit_vals = credit_vals.round(2)
    debit_vals = df.groupby([interval])['debit'].sum()
    debit_vals = debit_vals.round(2)
    monthName = df.groupby([interval])['monthName'].unique().astype(str)
    balance_vals = df.groupby([interval])['balance'].mean()
    balance_vals = balance_vals.round(2)
    labels = debit_vals.index.tolist()
    labels = [str(x) for x in labels]

    # for category charts
    cat_vals = df.groupby(['category'])['debit'].sum()
    cat_vals = cat_vals.apply(lambda x: x * -1)
    cat_vals = cat_vals.where(cat_vals > 0)
    cat_vals = cat_vals.dropna()
    cat_dict = cat_vals.to_dict()
    cat_labels = list(cat_dict.keys())

    # for income charts
    inc_vals = df.groupby(['category'])['credit'].sum()
    inc_vals = inc_vals.where(inc_vals > 0)
    inc_vals = inc_vals.dropna()
    inc_dict = inc_vals.to_dict()
    inc_labels = list(inc_dict.keys())

    new_df = {'credits':credit_vals.tolist(),
              'debits':debit_vals.tolist(),
              'monthName':monthName.tolist(),
              'balance':balance_vals.tolist(),
              'labels':labels,
              'cat_labels':cat_labels,
              'cat_vals':cat_dict,
              'inc_vals':inc_dict,
              'inc_labels':inc_labels
              }

    return new_df

# checks other records in the database and tags them
def check_other_records(**kwargs):
    other_records = Transaction.objects.filter(description=kwargs['description'], category=None).all()
    print('{} records found to append category to'.format(len(other_records)))
    for record in other_records:
        record.category = kwargs['category']
        record.tag = kwargs['tag']
        record.save()

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

# adds values to univeral tag database
def populate_universal_tags():
    taglist = [
        ['Tithing', 'Giving']
        , ['Offerings', 'Giving']
        , ['Charities', 'Giving']
        , ['Special Needs', 'Giving']
        , ['Groceries', 'Food']
        , ['Restaurants', 'Food']
        , ['Pet Food', 'Food']
        , ['Mortgage', 'Housing']
        , ['Rent', 'Housing']
        , ['Property Taxes', 'Housing']
        , ['Household Repairs', 'Housing']
        , ['HOA Dues', 'Housing']
        , ['Condo Fees', 'Housing']
        , ['Insurance', 'Housing']
        , ['Electricity', 'Utilities']
        , ['Water', 'Utilities']
        , ['Gas', 'Utilities']
        , ['Garbage', 'Utilities']
        , ['Phones', 'Utilities']
        , ['Cable', 'Utilities']
        , ['Internet', 'Utilities']
        , ["Adults' Clothing", 'Shopping']
        , ["Children's Clothing", 'Shopping']
        , ["Hobbies", 'Shopping']
        , ["Fuel", 'Transportation']
        , ["Tires", 'Transportation']
        , ["Oil Changes", 'Transportation']
        , ["Vehicle Maintenance", 'Transportation']
        , ["Parking Fees", 'Transportation']
        , ["Repairs", 'Transportation']
        , ["Licencing Fees", 'Transportation']
        , ["Vehicle Payments", 'Transportation']
        , ["Vehicle Insurance", 'Transportation']
        , ["Transit Fees", 'Transportation']
        , ["Primary Care", 'Medical']
        , ["Dental Care", 'Medical']
        , ["Specialty Care", 'Medical']
        , ["Medications", 'Medical']
        , ["Medical Devices", 'Medical']
        , ["Gym Memberships", 'Personal']
        , ["Hair Styling", 'Personal']
        , ["Babysitting", 'Personal']
        , ["Subscriptions", 'Personal']
        , ["Cosmetics", 'Personal']
        , ["Credit Card Fees", 'Financial']
        , ["Student Loan", 'Financial']
        , ["Line of Credit", 'Financial']
        , ["Expenses Reimbursement", 'Financial']
        , ["Games", 'Entertainment']
        , ["Cash", 'Entertainment']
        , ["Vacations", 'Entertainment']
        , ["Movies", 'Entertainment']
        , ["Shopping", 'Entertainment']
        , ["Paycheck", 'Income']
        , ["Dividends", 'Income']
        , ["Pension", 'Income']
    ]

    for i in taglist:
        record = UniversalTags(tag=i[0], category=i[1])
        record.save()

# takes 2 dates and returns true if they are a set time apart
def check_date(date1, date2):
    result = date1 - date2
    if result.days < 0:
        result = result * -1
    if result.days < 5:
        return True
    else:
        return False

# adds tags and looks for transfers the first time a new account is created is uploaded.
def first_run(**kwargs):
    print('first run!')
    # looking for transfers
    transactions = Transaction.objects.filter(user=kwargs['user'], category=None).all()
    compare_list = Transaction.objects.filter(user=kwargs['user'], category=None).exclude(credit='0').all()
    cat_list = Transaction.objects.filter(user=kwargs['user']).exclude(category=None).all()
    for item in transactions:
        for comparison in compare_list:
            if item.debit == comparison.credit and check_date(item.date,comparison.date) and item.account != compare_list.account:
                x = item.exclude_value
                print('transfer match found!')
                item.exclude_value = True
                y = item.exclude_value
                item.save()
        for category in cat_list:    # taging matching transactions
            if item.description == category.description:
                item.tag = category.tag
                item.category = category.category
                item.save()
                break

def prepare_list_for_dropdown(query):
    item_list = []
    for item in query:
        item_list.append((item, item))  # have to pass a tuple to the select form for choices
    item_list.sort()
    year_list = [('All', 'All')] + item_list
    return year_list

# take a category or tag and returns the previous years spending on it
def get_comparison(tag):
    print('hello')
    # now = datetime.datetime.now()
    # last_year = now - datetime.timedelta(weeks=52)
    # records = Transaction.objects.filter(tag=tag).all()
    # df = read_frame(records)
    # df = prepareDataFrame(df)
    #
    # now_credit_vals_year = df.groupby([now])['credit'].sum()