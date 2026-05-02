"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from src.api.products.views import ProductsView, AllProductsView, CategoriesView, CategoryView
from src.api.skus.views import SkusView
from src.api.invoices.views import InvoicesView, InvoiceAcceptView
from src.api.auth.views import RegisterView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('admin/', admin.site.urls),

    path('api/v1/reg/', RegisterView.as_view(), name='register'),
    path('api/v1/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/v1/login/refresh/', TokenRefreshView.as_view(), name='token_refresh'),


    path('api/v1/products/', ProductsView.as_view()),
    path('api/v1/products/<uuid:id>/', ProductsView.as_view()),
    path('api/v1/products/my/', AllProductsView.as_view()),
    path('api/v1/categories/', CategoriesView.as_view()),
    path('api/v1/categories/<uuid:id>', CategoryView.as_view()),

    path('api/v1/skus/', SkusView.as_view()),
    path('api/v1/skus/<uuid:id>/', SkusView.as_view()),

    path('api/v1/invoices/', InvoicesView.as_view()),
    path('api/v1/invoices/<uuid:id>/', InvoicesView.as_view()),
    path('api/v1/invoices/<uuid:id>/accept/', InvoiceAcceptView.as_view())
]
