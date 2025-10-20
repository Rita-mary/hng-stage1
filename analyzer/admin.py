from django.contrib import admin
from .models import AnalyzedString
# Register your models here.

@admin.register(AnalyzedString)
class AnalyzedStringAdmin(admin.ModelAdmin):
    list_display = ('id', 'value', 'length', 'is_palindrome', 'unique_characters', 'word_count', 'created_at')
    search_fields = ('value',)
    list_filter = ('is_palindrome',)
    readonly_fields = ('created_at',)