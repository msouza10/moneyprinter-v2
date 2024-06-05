from django.db import models

class APISettings(models.Model):
    notion_token = models.CharField(max_length=255, blank=True, null=True)
    notion_database_id = models.CharField(max_length=255, blank=True, null=True)
    gemini_api_key = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return "API Settings"