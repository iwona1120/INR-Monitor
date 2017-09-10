from django.contrib import admin
from .models import User, UsedDrugs, TakenDrugs, Drug, INR, test


admin.site.register(User)
admin.site.register(UsedDrugs)
admin.site.register(TakenDrugs)
admin.site.register(INR)
admin.site.register(test)
admin.site.register(Drug)


# Register your models here.
