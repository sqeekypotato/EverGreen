from django import forms
from django.contrib.auth.models import User

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
    balance = forms.DecimalField(label='Balance of Account' ,required=True)
    date = forms.ChoiceField(choices=CHOICES)
    debit = forms.ChoiceField(choices=CHOICES)
    credit = forms.ChoiceField(choices=CHOICES)
    rows = forms.ChoiceField(choices=[(0,0),(1,1), (2,2), (3,3), (4,4), (5,5)])
    description = forms.ChoiceField(choices=CHOICES)

    def __init__(self, custom_choices = None, *args):
        super(AccountSelectForm, self).__init__(*args)
        if custom_choices:
            self.fields['date'].choices = custom_choices
            self.fields['debit'].choices = custom_choices
            self.fields['credit'].choices = custom_choices
            self.fields['description'].choices = custom_choices

class YearForm(forms.Form):
    years = forms.ChoiceField(choices=[])

    def __init__(self, *args, **kwargs):
        years = kwargs.pop('years')
        super(YearForm, self).__init__(*args, **kwargs)
        self.fields['years'].choices = years


class MonthForm(forms.Form):
    monthNum = forms.ChoiceField(choices=[])

    def __init__(self, *args, **kwargs):
        monthNum = kwargs.pop('monthNum')
        super(MonthForm, self).__init__(*args, **kwargs)
        self.fields['monthNum'].choices = monthNum