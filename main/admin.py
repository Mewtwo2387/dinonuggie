from django.contrib import admin
from .models import Dinonuggies

# Register your models here.
class DinonuggiesAdmin(admin.ModelAdmin):
    list_display = ('user', 'count')

admin.site.register(Dinonuggies, DinonuggiesAdmin)