from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import OrgUnit,Employee,ProcurementApplication

from .forms import CustomUserCreationForm, CustomUserChangeForm


class EmployeeAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = Employee
    list_display = ['email', 'username','role','org_unit',]


fields = list(EmployeeAdmin.fieldsets)
fields[0] = (None, {'fields': ('role','org_unit',)})
EmployeeAdmin.fieldsets = tuple(fields)

admin.site.register(Employee, EmployeeAdmin)

admin.site.register(OrgUnit)
admin.site.register(ProcurementApplication)

# Register your models here.
