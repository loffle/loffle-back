import sys, inspect

from django.contrib import admin

# from loffle.models import Ticket, RaffleApply

# admin.site.register(Ticket)
# admin.site.register(RaffleApply)

import loffle.models

for model_name, model_cls in inspect.getmembers(sys.modules[loffle.models.__name__], inspect.isclass):
    if hasattr(model_cls, '_meta') and model_cls._meta.app_label == __package__:
        admin.site.register(model_cls)
