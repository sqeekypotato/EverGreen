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
import threading

from core_app.forms import ContactForm, UploadToExistingAccount, UploadFileForm, AccountSelectForm, YearForm, MonthForm
from core_app.models import BankAccounts, Transaction
from core_app.functions import fixQuotesForCSV, convertToInt, buildTagDict, prepareDataFrame, prepare_table,\
    check_other_records, add_tags_to_database, add_df_to_account

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

        years = Transaction.objects.values_list('year', flat=True).filter(user=request.user).distinct()
        year_list = [('All', 'All')]
        for year in years:
            year_list.append((year, year)) #have to pass a tuple to the select form for choices

        months = Transaction.objects.values_list('monthNum', flat=True).filter(user=request.user).distinct()
        month_list = [('All', 'All')]
        for month in months:
            month_list.append((month, month))

        yearForm = YearForm(years=year_list)
        monthForm = MonthForm(monthNum=month_list)

        context = {
            'yearForm':yearForm,
            'monthForm':monthForm
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
                credit = int(request.POST['credit'])
                debit = int(request.POST['debit'])
                my_date = int(request.POST['date'])
                description = int(request.POST['description'])


                records_added = add_df_to_account(dataframe, request, userAccount, my_date, credit, debit, description)

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

def upload_transactions(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            form = UploadFileForm(request.POST, request.FILES)
            if form.is_valid():
                userAccount = request._post['accountNames']
                df = fixQuotesForCSV(request.FILES['file'])
                dataframe = pd.read_json(df)
                dataframe = dataframe.reset_index(drop=True)
                account = BankAccounts.objects.filter(account_name=userAccount, user=request.user).first()

                records_added = add_df_to_account(dataframe, request, account, account.transDateCol,
                                                  account.transCreditCol, account.transDebitCol, account.transDescriptionCol)
                message = '{} records added to the database.  We are working on processing them now'.format(
                    records_added)

                template = loader.get_template('core_app/index.html')
                context = {
                    'user': request.user,
                    'message': message
                }
                return HttpResponse(template.render(context, request))

        template = loader.get_template('core_app/upload_transactions.html')
        accounts = BankAccounts.objects.values_list('account_name', flat=True).filter(user=request.user).distinct()
        account_list = []
        for account in accounts:
            account_list.append((account, account))  # have to pass a tuple to the select form for choices
        form = UploadToExistingAccount(accountNames=account_list)
        context = {
            'form': form,
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
                print('new loop in tags')
                temp_record = Transaction.objects.get(id=transNum)
                temp_record.tag = values['tag']
                temp_record.category = values['cat']
                temp_record.year = temp_record.date.year
                temp_record.monthNum = temp_record.date.month
                temp_record.monthName = temp_record.date.strftime("%b")
                temp_record.save()

                t = threading.Thread(target=check_other_records, kwargs={'description': temp_record.description,
                                                                         'category':temp_record.category,
                                                                         'tag':temp_record.tag})
                t.start()

                add_tags_to_database(temp_record.category, temp_record.tag, request.user)
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

def get_months(request):
    if request.user.is_authenticated:
        request_year = request._post['year']
        months = Transaction.objects.values_list('monthNum', flat=True).filter(user=request.user, year=request_year).distinct()
        month_list = ['All']
        for month in months:
            month_list.append(month)
        return JsonResponse(month_list, safe=False)

def transaction_processing(myTransactions, my_interval):
    df = read_frame(myTransactions)
    df = prepareDataFrame(df)
    result = prepare_table(df, my_interval)
    return result

def first_chart(request):
    if request.user.is_authenticated:
        myTransactions = Transaction.objects.filter(user=request.user).all()
        result = transaction_processing(myTransactions, 'year')
        return JsonResponse(result, safe=False)

def new_chart_data(request):
    if request.user.is_authenticated:
       if request._post['name'] == 'years':
           if request._post['value'] == 'All':
               myTransactions = Transaction.objects.filter(user=request.user).all()
               result = transaction_processing(myTransactions, 'year')
               return JsonResponse(result)
           else:
               request.session['year'] = request._post['value']
               myTransactions = Transaction.objects.filter(user=request.user, year=request._post['value']).all()
               result = transaction_processing(myTransactions, 'monthNum')
               return JsonResponse(result)

       if request._post['name'] == 'monthNum':
           if request._post['value'] == 'All':
               myTransactions = Transaction.objects.filter(user=request.user, year=request.session['year']).all()
               result = transaction_processing(myTransactions, 'monthNum')
               return JsonResponse(result)
           else:
               myTransactions = Transaction.objects.filter(user=request.user, monthNum=request._post['value'], year=request.session['year']).all()
               result = transaction_processing(myTransactions, 'day')
               return JsonResponse(result)

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

