from __future__ import unicode_literals

from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, authenticate
from django.http import HttpResponse, JsonResponse
from django.template import loader
from django.core.mail import EmailMessage
from django.views.generic import View

import pandas as pd
import calendar

from core_app.forms import ContactForm, UserForm, UploadFileForm, AccountSelectForm
from core_app.models import BankAccounts, Transaction
from core_app.functions import fixQuotesForCSV, convertToInt



# Create your views here.
def home(request):

    template = loader.get_template('core_app/index.html')
    context = {
        'user':request.user
    }
    return HttpResponse(template.render(context, request))

def main_page(request):
    if request.user.is_authenticated:
        template = loader.get_template('core_app/main.html')
        context = {

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

# def redirect_details(request): #this is required to ensure that account_details starts with a GET request
#     if request.user.is_authenticated:
#         return redirect('account_details')
#     else:
#         return redirect('home')

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
            form = AccountSelectForm(request.POST)
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
                    trans.save()
                    print(trans)
        form = AccountSelectForm()

        template = loader.get_template('core_app/account_details.html')
        context = {
            'form':form,
            'df':df,
            'html':html
        }
        return HttpResponse(template.render(context, request))
    else:
        return redirect('home')

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

