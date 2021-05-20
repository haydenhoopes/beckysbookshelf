from django.contrib import admin
from .models import (Books, Authors, Topics, Publishers, Series, 
                Conditions, CoverType, SmallShelfSigns, Customers,
                Transactions)

  
admin.site.register(Books)
admin.site.register(Authors)
admin.site.register(Topics)
admin.site.register(Publishers)
admin.site.register(Series)
admin.site.register(Conditions)
admin.site.register(CoverType)
admin.site.register(SmallShelfSigns)
admin.site.register(Customers)
admin.site.register(Transactions)