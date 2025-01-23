from django.urls import path
from ExtractClausesApp.views import ExtractClauseViewSet


urlpatterns = [
    path('extract_clauses/', ExtractClauseViewSet.as_view({'post': 'extract_clauses_from_docs'}), name='extract_clauses_from_docs'),
    path('get_clauses/',  ExtractClauseViewSet.as_view({'get': 'get_clauses_from_docs'}), name='get_clauses_from_docs'),
    path('add_clauses/', ExtractClauseViewSet.as_view({'post': 'add_clauses_from_docs'}), name='add_clauses_from_docs'),
    path('validate_docs/',  ExtractClauseViewSet.as_view({'post': 'validate_supplier_docs'}), name='validate_supplier_docs'),
]
