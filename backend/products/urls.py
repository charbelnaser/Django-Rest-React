from django.urls import path
from . import views

urlpatterns = [
    path(
        "products/", views.ProductListCreateView.as_view(), name="product-list-create"
    ),
    path(
        "products/<int:pk>/",
        views.ProductRetrieveUpdateDestroyView.as_view(),
        name="product-detail",
    ),
    path("products/search/", views.ProductSearchView.as_view(), name="product-search"),
    path(
        "products/bulk-import/",
        views.ProductBulkImportView.as_view(),
        name="product-bulk-import",
    ),
]
