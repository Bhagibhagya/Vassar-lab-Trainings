from django.urls import path,re_path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from . import views


schema_view = get_schema_view(
    openapi.Info(
        title="Library Management System API",
        default_version="v1",
        description="API documentation for the Library Management System",
        terms_of_service="https://www.example.com/terms/",
        contact=openapi.Contact(email="admin@example.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('authors/', views.AuthorListCreate.as_view(), name='author-list-create'),
    path('authors/<int:pk>/', views.AuthorDetail.as_view(), name='author-detail'),
    path('books/', views.BookListCreateView.as_view(), name='book-list-create'),
    path('books/<int:pk>/', views.BookDetail.as_view(), name='book-detail'),
    path('borrowers/', views.BorrowerListCreate.as_view(), name='borrower-list-create'),
    path('borrowers/<int:pk>/', views.BorrowerDetail.as_view(), name='borrower-detail'),
    path('borrowrecords/', views.BorrowRecordListCreate.as_view(), name='borrowrecord-list-create'),
    path('borrowrecords/<int:pk>/', views.BorrowRecordDetail.as_view(), name='borrowrecord-detail'),
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
