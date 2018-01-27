# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

# Register your models here.

from .models import Tags, BankAccounts, Transaction, UniversalTags

admin.site.register(Tags)
admin.site.register(BankAccounts)
admin.site.register(Transaction)
admin.site.register(UniversalTags)

