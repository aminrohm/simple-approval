from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import Employee

class CustomUserCreationForm(UserCreationForm):

    class Meta:
        model = Employee
        fields = ('username', 'email','role','org_unit')

class CustomUserChangeForm(UserChangeForm):

    class Meta:
        model = Employee
        fields = ('username', 'email','role','org_unit')
