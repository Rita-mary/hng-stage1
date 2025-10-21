from django.urls import path
from .views import ListCreateAnalyzedStringsView, StringRetrieveDestroyView, NaturalLanguageFilterView

urlpatterns = [
    path('strings/', ListCreateAnalyzedStringsView.as_view(), name='list-create-strings-slash'),
    path('strings', ListCreateAnalyzedStringsView.as_view(), name='list-strings'),
    path('strings/<str:value>', StringRetrieveDestroyView.as_view(), name='get-string'),
    path('strings/<str:value>/', StringRetrieveDestroyView.as_view(), name='get-string'),
    path('strings/filter-by-natural-language', NaturalLanguageFilterView.as_view(), name='nl-filter'),
]