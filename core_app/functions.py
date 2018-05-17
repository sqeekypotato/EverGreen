from io import StringIO
import pandas as pd
import calendar
import datetime
from django_pandas.io import read_frame

from .models import Transaction, Tags, UniversalTags, UserRule, BankAccounts

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

    first_run(user=request.user)

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
    dataframe['date'] = dataframe['date'].dt.date
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

    # getting the correct labels
    if interval == 'monthNum':
        tempName = df['monthName'].unique()
        labels = list(tempName)
    else:
        labels = debit_vals.index.tolist()
        labels = [str(x) for x in labels]

    balance_vals = df.groupby([interval])['balance'].median()
    balance_vals = balance_vals.round(2)


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
    print('OTHER RECORD CHECK')
    other_records = Transaction.objects.filter(description=kwargs['description'], category=None).all()
    print('{} records found to append category to'.format(len(other_records)))
    for record in other_records:
        record.category = kwargs['category']
        record.tag = kwargs['tag']
        if record.category == 'Transfer' and record.tag == 'Transfer':
            record.exclude_value = True
        record.save()

    # added this because I couldn't remember if check other records was used in more than one place and I am lazy

# added this because I was unsure all the places check other records was called and I needed a list
def check_other_records_list(**kwargs):
    for item in kwargs['value']:
        check_other_records(description=item['description'], category=item['category'], tag=item['tag'])

# checks if cat and tag are in database (as a pair) and if not, adds them
def add_tags_to_database(cat, tag, user):
    add_tag = True
    other_tags = Tags.objects.filter(category=cat, user=user).all()
    for record in other_tags:
        if record.tag == tag:
            add_tag = False
    if add_tag:
        new_tag = Tags(category=cat, tag=tag, user=user)
        new_tag.save()
        print('new tag added to database')

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
        , ["Transfer", 'Transfer']
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
    run_user_rules(kwargs['user']) #runs the user's rules

    # looking for transfers ________________________________________________________________________
    transactions = Transaction.objects.filter(user=kwargs['user'], category=None).all()
    compare_list = Transaction.objects.filter(user=kwargs['user'], category=None).exclude(credit='0').all()
    cat_list = Transaction.objects.filter(user=kwargs['user']).exclude(category=None).all()
    for item in transactions:
        for comparison in compare_list:
            if item.debit == comparison.credit and check_date(item.date,comparison.date) and item.account != comparison.account:
                x = item.exclude_value
                print('transfer match found!')
                item.exclude_value = True
                y = item.exclude_value
                item.save()
    # end of transfer search ___________________________________________________________________________________

    # taging matching transactions______________________________________________________________________________
        for transaction in transactions:
            print('checking transactions'
)
            match = Transaction.objects.filter(user=kwargs['user'], description=transaction.description).exclude(category=None).first()
            if match:
                transaction.tag = match.tag
                transaction.category = match.category
                item.save()
                break

# takes a list of single times and returns a tuple like this ('item', 'item').  Needed to prepare select dropdowns
def prepare_list_for_dropdown(query):
    item_list = []
    for item in query:
        item_list.append((item, item))  # have to pass a tuple to the select form for choices
    item_list.sort()
    year_list = [('All', 'All')] + item_list
    return year_list

def pretteyfy_numbers(number):
    if number:
        number = str(number)
        dollars, cents = number.split('.')
        cents = cents[:2]
        if len(cents) == 1:
            cents = '{}0'.format(cents)
        if len(dollars) > 6:
            part3 = dollars[-3:]
            part2 = dollars[-6:-3]
            part1 = dollars[:-6]
            num_string = part1 + ',' + part2 + ',' + part3
            return '${}.{}'.format(num_string, cents)
        elif len(dollars) <= 6 and len(dollars) > 3:
            part2 = dollars[-3:]
            part1 = dollars[:-3]
            num_string = part1 + ',' + part2
            return '${}.{}'.format(num_string, cents)
        elif len(dollars) <= 3:
            return '${}.{}'.format(dollars, cents)

# take a category or tag and returns the previous year and previous month's spending on it
def get_comparison(tag, user):
    now = datetime.datetime.now()
    last_year = now.year - 1
    last_month = now.month - 1
    if last_month < 1:
        last_month = 12
        last_year -= last_year

    transactions = Transaction.objects.filter(user=user, tag=tag[1], category=tag[0]).all()
    df = read_frame(transactions)
    df = prepareDataFrame(df)
    if df['credit'].sum() != 0.0 or df['debit'].sum() != 0.0: # tests to make sure there are acutal values to report on or else it returns False which is caught later and not reported on
        last_month_df = df[(df.monthNum == last_month) & (df.year == now.year)]
        last_year_month_df = df[(df.monthNum == last_month) & (df.year == last_year)]
        ytd_df = df[(df.monthNum <= now.month) & (df.year == now.year)]
        last_ytd_df = df[(df.monthNum <= now.month) & (df.year == last_year)]

        def get_values(df):
            credit_vals = df['credit'].sum()
            debit_vals = df['debit'].sum()
            debit_vals = debit_vals * -1
            if credit_vals < 1:
                credit_vals = None
            if debit_vals < 1:
                debit_vals = None
            my_dict = {'credit':pretteyfy_numbers(credit_vals),
                       'debit':pretteyfy_numbers(debit_vals)}
            return my_dict

        last_month = get_values(last_month_df)
        last_year_month = get_values(last_year_month_df)
        ytd = get_values(ytd_df)
        last_ytd = get_values(last_ytd_df)

        return {'last_month':last_month,
                'last_year_month':last_year_month,
                'ytd':ytd,
                'last_ytd':last_ytd,}
    else:
        return False

# gets a list of tags that the user has requested analysis be run on
def get_comparison_tags(user):
    return_list = []
    other_tags = Tags.objects.filter(user=user, drill_down=True).all()
    for i in other_tags:
        return_list.append((i.category, i.tag))


    return return_list

# adds custom user rule to the database
def create_rule(user, detail, description, category, tag):
    new_rule = UserRule()
    new_rule.user = user
    new_rule.description = description
    new_rule.category = category
    new_rule.tag = tag
    if detail == 'begins_with':
        new_rule.begins_with = True
    elif detail == 'ends_with':
        new_rule.ends_with = True
    new_rule.save()
    run_user_rules(user)

# Goes through all the user rules that a user has created and runs them
def run_user_rules(user):
    rules = UserRule.objects.filter(user=user).all()
    record_count = 0
    for rule in rules:
        if rule.begins_with:
            transactions = Transaction.objects.filter(user=user, description__startswith=rule.description.strip(), category=None).all()
            for item in transactions:
                item.tag = rule.tag
                item.category = rule.category
                if item.category == 'Transfer' and item.tag == 'Transfer':
                    item.exclude_value = True
                item.save()
                record_count += 1
        elif rule.ends_with:
            transactions = Transaction.objects.filter(user=user, description__endswith=rule.description.strip(), category=None).all()
            for item in transactions:
                item.tag = rule.tag
                item.category = rule.category
                if item.category == 'Transfer' and item.tag == 'Transfer':
                    item.exclude_value = True
                item.save()
                record_count += 1
    print('Modified {} records using user rules'.format(record_count))

# When uploading a file to an existing account, this finds the last entry for the account based on date and then returns
# the dataframe that is being uploaded with all dates after that so there are no duplications.  Returns a dataframe
def check_for_dups(user, account, df):

    the_account = BankAccounts.objects.filter(account_name=account, user=user).first()
    last_transaction = Transaction.objects.order_by('-date').filter(user=user, account=the_account)[0]


    df[the_account.transDateCol] = pd.to_datetime(df[the_account.transDateCol])  # changes string to date format
    df = df.fillna(0)  # replaces NaN with 0

    df_1 = df[df[the_account.transDateCol] == last_transaction.date]
    row_num = 0
    credit_val = float(last_transaction.credit/100)
    debit_val = float(last_transaction.debit/100)

    merge_df = False

    for index, row in df_1.iterrows():
        if row[the_account.transDescriptionCol] == last_transaction.description:
            if row[the_account.transCreditCol] == credit_val:
                if row[the_account.transDebitCol] == debit_val:
                    row_num = index + 1
                    merge_df = True
    df_1 = df_1.loc[row_num:]
    df_2 = df[df[the_account.transDateCol] > last_transaction.date]

    if merge_df:
        return_df = df_1 + df_2
    else:
        return_df = df_2

    print('{} rows added to dataframe'.format(return_df.shape[0]))
    return return_df