from django import forms
from django.contrib.auth.models import User
from django.forms import ModelForm

from .models import Transaction

class ContactForm(forms.Form):
    contact_name = forms.CharField(required=True)
    contact_email = forms.EmailField(required=True)
    content = forms.CharField(
        required=True,
        widget=forms.Textarea
    )

class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    country = forms.CharField()
    state_province = forms.CharField()
    number_of_people = forms.IntegerField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'country', 'state_province', 'number_of_people']

class UploadFileForm(forms.Form):
    file = forms.FileField()

class AccountSelectForm(forms.Form):
    CHOICES = [
        ('EXMPL', 'Example')
    ]

    name = forms.CharField(label='Account Name' ,required=True)
    name.widget.attrs['class'] = 'form-control form-control-sm'
    balance = forms.DecimalField(label='Balance of Account' ,required=True)
    balance.widget.attrs['class'] = 'form-control form-control-sm'
    date = forms.ChoiceField(choices=CHOICES)
    date.label = "What column has the transaction's dates?"
    debit = forms.ChoiceField(choices=CHOICES)
    debit.label = 'What column has your debit values?'
    credit = forms.ChoiceField(choices=CHOICES)
    credit.label = 'What column has your credit values?'
    rows = forms.ChoiceField(choices=[(0,0),(1,1), (2,2), (3,3), (4,4), (5,5)])
    rows.widget.attrs['class'] = 'form-control form-control-sm'
    rows.label = 'What row do the transactions start?'
    description = forms.ChoiceField(choices=CHOICES)
    description.label = "What column is the description?"

    def __init__(self, custom_choices = None, *args):
        super(AccountSelectForm, self).__init__(*args)
        if custom_choices:
            self.fields['date'].choices = custom_choices
            self.fields['date'].widget.attrs['class'] = 'form-control form-control-sm'
            self.fields['debit'].choices = custom_choices
            self.fields['debit'].widget.attrs['class'] = 'form-control form-control-sm'
            self.fields['credit'].choices = custom_choices
            self.fields['credit'].widget.attrs['class'] = 'form-control form-control-sm'
            self.fields['description'].choices = custom_choices
            self.fields['description'].widget.attrs['class'] = 'form-control form-control-sm'

class YearForm(forms.Form):
    years = forms.ChoiceField(choices=[])

    def __init__(self, *args, **kwargs):
        years = kwargs.pop('years')
        super(YearForm, self).__init__(*args, **kwargs)
        self.fields['years'].choices = years
        self.fields['years'].widget.attrs['class'] = 'form-control form-control-sm'

class MonthForm(forms.Form):
    monthNum = forms.ChoiceField(choices=[])
    monthNum.label = "Month"

    def __init__(self, *args, **kwargs):
        monthNum = kwargs.pop('monthNum')
        super(MonthForm, self).__init__(*args, **kwargs)
        self.fields['monthNum'].choices = monthNum
        self.fields['monthNum'].widget.attrs['class'] = 'form-control form-control-sm'

class UploadToExistingAccount(forms.Form):
    file = forms.FileField()
    accountNames = forms.ChoiceField(choices=[])
    dupliactes = forms.BooleanField()

    def __init__(self, *args, **kwargs):
        accountNames = kwargs.pop('accountNames')
        super(UploadToExistingAccount, self).__init__(*args, **kwargs)
        self.fields['accountNames'].choices = accountNames
        self.fields['accountNames'].widget.attrs['class'] = 'form-control form-control-sm'

class CategorySelection(forms.Form):
    categories = forms.ChoiceField(choices=[])

    def __init__(self, *args, **kwargs):
        categories = kwargs.pop('categories')
        super(CategorySelection, self).__init__(*args, **kwargs)
        self.fields['categories'].choices = categories
        self.fields['categories'].widget.attrs['class'] = 'form-control form-control-sm'

class IncomeCategorySelection(forms.Form):
    income_categories = forms.ChoiceField(choices=[])

    def __init__(self, *args, **kwargs):
        income_categories = kwargs.pop('income_categories')
        super(IncomeCategorySelection, self).__init__(*args, **kwargs)
        self.fields['income_categories'].choices = income_categories
        self.fields['income_categories'].widget.attrs['class'] = 'form-control form-control-sm'
