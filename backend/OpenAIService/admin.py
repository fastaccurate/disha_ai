from django.contrib import admin
from .models import PromptTemplate, LLMConfigName

admin.site.register(PromptTemplate)
admin.site.register(LLMConfigName)
