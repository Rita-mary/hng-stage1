from django.urls import path
from .views import AnalyzedStringCreateView, StringRetrieveDestroyView, ListAnalyzedStringsView, NaturalLanguageFilterView

urlpatterns = [
    path('strings/', AnalyzedStringCreateView.as_view(), name='create-string'),
    path('strings/filter-by-natural-language', NaturalLanguageFilterView.as_view(), name='nl-filter'),
    path('strings/<str:value>/', StringRetrieveDestroyView.as_view(), name='get-string'),
    path('strings', ListAnalyzedStringsView.as_view(), name='list-strings'),
]