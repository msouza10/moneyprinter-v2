from django import forms
from .models import APISettings
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User

class APISettingsForm(forms.ModelForm):
    class Meta:
        model = APISettings
        fields = ['notion_token', 'notion_database_id', 'gemini_api_key', 'twitch_client_id', 'twitch_client_secret']
        widgets = {
            'notion_token': forms.TextInput(attrs={'class': 'form-control custom-textbox'}),
            'notion_database_id': forms.TextInput(attrs={'class': 'form-control custom-textbox'}),
            'gemini_api_key': forms.TextInput(attrs={'class': 'form-control custom-textbox'}),
            'twitch_client_id': forms.TextInput(attrs={'class': 'form-control custom-textbox'}),
            'twitch_client_secret': forms.TextInput(attrs={'class': 'form-control custom-textbox'}),
        }

class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))

class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'password1': forms.PasswordInput(attrs={'class': 'form-control'}),
            'password2': forms.PasswordInput(attrs={'class': 'form-control'}),
        }
