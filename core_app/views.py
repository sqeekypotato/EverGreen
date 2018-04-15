from __future__ import unicode_literals

from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, authenticate
from django.http import HttpResponse, JsonResponse
from django.template import loader
from django.core.mail import EmailMessage
from django.views.generic import View
from django_pandas.io import read_frame

import pandas as pd
import calendar

from core_app.forms import ContactForm, UserForm, UploadFileForm, AccountSelectForm, YearForm
from core_app.models import BankAccounts, Transaction
from core_app.functions import fixQuotesForCSV, convertToInt, buildTagDict, prepareDataFrame, prepareTables

from .models import Transaction, Tags, UniversalTags

# Create your views here.
def home(request):
    message = 'Hello and welcome to Evergreen Financial!'
    template = loader.get_template('core_app/index.html')
    context = {
        'user':request.user,
        'message':message
    }
    return HttpResponse(template.render(context, request))

def main_page(request):
    if request.user.is_authenticated:
        template = loader.get_template('core_app/main.html')
        myTransactions = Transaction.objects.filter(user=request.user).all()
        df = read_frame(myTransactions)
        df = prepareDataFrame(df)
        creditList, debitList, balanceList, labelList, tagvar, catListNum, catListLabel = prepareTables(df, 'year')

        years = Transaction.objects.values_list('year', flat=True).filter(user=request.user).distinct()
        year_list = []
        for year in years:
            year_list.append((year, year)) #have to pass a tuple to the select form for choices
        yearForm = YearForm(years=year_list)

        context = {
            'yearForm':yearForm,
            'credit': creditList,
            'debit': debitList,
            'labels': labelList,
            'balance': balanceList,
            'categoryNum': catListNum,
            'catListLabel': catListLabel
        }
        return HttpResponse(template.render(context, request))
    else:
        return redirect('home')

def newAccount(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            form = UploadFileForm(request.POST, request.FILES)
            if form.is_valid():
                request.session['df'] = fixQuotesForCSV(request.FILES['file'])
                return redirect('account_details')
        else:
            form = UploadFileForm()
        return render(request, 'core_app/new_account.html', {'form': form})
    else:
        return redirect('home')

def account_details(request):
    if request.user.is_authenticated:
        dataframe = request.session.get('df', None)
        dataframe = pd.read_json(dataframe)
        dataframe = dataframe.reset_index(drop=True)
        df = dataframe.head(10).values.tolist()
        html = dataframe.head(10).to_html()

        # this is done to populate the dropdown menu for the forms
        tempCol = range(0, len(df[0]))
        columnNum = []
        for i in tempCol:
            j = i
            columnNum.append((i, j))

        if request.method == 'POST':
            form = AccountSelectForm(columnNum, request.POST)
            if form.is_valid():
                # sets up users account
                userAccount = BankAccounts()
                userAccount.user = request.user
                userAccount.account_name = request.POST['name']
                userAccount.balance = convertToInt(request.POST['balance'])
                userAccount.startRow = int(request.POST['rows'])
                userAccount.transDateCol = int(request.POST['date'])
                userAccount.transCreditCol = int(request.POST['credit'])
                userAccount.transDebitCol = int(request.POST['debit'])
                userAccount.transDescriptionCol = request.POST['description']
                userAccount.save()

                # adds transactions to account
                dataframe[int(request.POST['date'])] = pd.to_datetime(dataframe[int(request.POST['date'])]) #changes string to date format
                dataframe = dataframe.fillna(0) #replaces NaN with 0
                records_added = 0
                for index, row in dataframe.iterrows():
                    credit = row[int(request.POST['credit'])]
                    debit = row[int(request.POST['debit'])]
                    credit = convertToInt(credit)
                    debit = convertToInt(debit)
                    monthNum = row[int(request.POST['date'])].month
                    year = row[int(request.POST['date'])].year
                    monthName = calendar.month_abbr[monthNum]
                    if debit < 0:
                        debit = debit * -1
                    balance = userAccount.balance + credit - debit
                    date = row[int(request.POST['date'])].to_pydatetime().date()
                    description = row[int(request.POST['description'])]
                    trans = Transaction(
                                        user=request.user,
                                        account=userAccount,
                                        balance=balance,
                                        date=date,
                                        description =description ,
                                        credit= credit,
                                        debit = debit,
                                        monthNum = monthNum,
                                        monthName = monthName,
                                        year = year
                                        )
                    trans.save() #adds record to the database
                    records_added += 1



                message = '{} records added to the database.  We are working on processing them now'.format(records_added)

                template = loader.get_template('core_app/index.html')
                context = {
                    'user': request.user,
                    'message': message
                }
                return HttpResponse(template.render(context, request))

        form = AccountSelectForm(columnNum)

        template = loader.get_template('core_app/account_details.html')
        context = {
            'form':form,
            'df':df,
            'html':html
        }
        return HttpResponse(template.render(context, request))
    else:
        return redirect('home')

def tags(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            form_dict = request._post
            tagDict = buildTagDict(form_dict)

            for transNum, values in tagDict.items():
                temp_record = Transaction.objects.get(id=transNum)
                temp_record.tag = values['tag']
                temp_record.category = values['cat']
                temp_record.year = temp_record.date.year
                temp_record.monthNum = temp_record.date.month
                temp_record.monthName = temp_record.date.strftime("%b")
                temp_record.save()

                return redirect('tags')


        trans = Transaction.objects.all().filter(user=request.user, tag=None)[:20] #gets twenty records
        cats = Tags.objects.distinct().values_list('category', flat=True)
        tempcats = UniversalTags.objects.distinct().values_list('category', flat=True)
        cats1 = list(cats)
        tempcats1 = list(tempcats)
        cats1 += tempcats1
        cats1.sort()

        tableList=[]
        for i in trans:
            temp_list = [i.id, i.date, i.description, float(i.credit)/100, float(i.debit)/100]
            tableList.append(temp_list)

        template = loader.get_template('core_app/tags.html')
        context = {
            'tableList' : tableList,
            'category' : cats1
        }
        print(cats1)
        return HttpResponse(template.render(context, request))
    else:
        message = 'Please login first!'
        template = loader.get_template('core_app/index.html')
        context = {
            'user': request.user,
            'message': message
        }
        return HttpResponse(template.render(context, request))

def get_tag(request):
    if request.user.is_authenticated:
        category = request._post['category']
        number = request._post['number']
        number = number.replace('cat', '#tag_option')

        userTagsQuery = Tags.objects.filter(category=category)
        uniTagQuery = UniversalTags.objects.filter(category=category)
        temp_list = []
        for item in userTagsQuery:
            if item.tag not in temp_list:
                temp_list.append(item.tag)
        for item in uniTagQuery:
            if item.tag not in temp_list:
                temp_list.append(item.tag)
        temp_list.sort()
        result = {'tags': temp_list, 'number':number}

        return JsonResponse(result)

# ________________ Ajax request _______________________________

def income_chart(request):
    pass

# __________________Generic Pages______________________________
def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            print('login successful')
            return redirect('main_page')
    else:
        form = UserCreationForm()
    return render(request, 'core_app/signup.html', {'form': form})

def contact(request):
    form_class = ContactForm

    if request.method == 'POST':
        form = form_class(data=request.POST)

        if form.is_valid():
            contact_name = request.POST.get('contact_name', '')
            contact_email = request.POST.get('contact_email', '')
            form_content = request.POST.get('content', '')

            # Email the profile with the
            # contact information

        ctx = {
            'contact_name': contact_name,
            'contact_email': contact_email,
            'form_content': form_content,
        }
        message = loader.render_to_string('core_app/contact_template.html', ctx)
        msg = EmailMessage("New contact form submission", form_content, headers = {'Reply-To': contact_email }, to=['info@carcostcalculator.ca'])
        msg.content_subtype = 'html'
        msg.send()
        return redirect('contact')


    return render(request, 'core_app/contact.html', {
        'form': form_class,
    })

def handler404(request):
    template = loader.get_template('core_app/404.html')
    context = {}
    return HttpResponse(template.render(context, request))

def handler500(request, template_name='404.html'):
    template = loader.get_template('core_app/500.html')
    context ={}
    return HttpResponse(template.render(context, request))

