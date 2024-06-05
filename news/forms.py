from django import forms
from .models import APISettings

class APISettingsForm(forms.ModelForm):
    class Meta:
        model = APISettings
        fields = ['notion_token', 'notion_database_id', 'gemini_api_key']
        widgets = {
            'notion_token': forms.TextInput(attrs={'class': 'form-control custom-textbox'}),
            'notion_database_id': forms.TextInput(attrs={'class': 'form-control custom-textbox'}),
            'gemini_api_key': forms.TextInput(attrs={'class': 'form-control custom-textbox'}),
        }