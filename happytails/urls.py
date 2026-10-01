"""
URL configuration for happytails project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

from .import views
urlpatterns = [
    path('admin/', admin.site.urls),
    path('master/', views.Master,name='master'),
    path('', views.Index,name='index'),
    path('signup/',views.Signup,name='signup'),
    path('login/',views.Login,name='login'),
    path('aboutus/',views.Aboutus,name='aboutus'),
    path('contactus/',views.Contactus,name='contactus'),
    path('forgot/',views.Forgot,name='forgot'),

    # Forgot Password
    path('password-reset/',auth_views.PasswordResetView.as_view(template_name="registration/password_reset_form.html"),name='password_reset'),
    path('password-reset/done/',auth_views.PasswordResetDoneView.as_view(template_name="registration/password_reset_done.html"),name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name="registration/password_reset_confirm.html"), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name="registration/password_reset_complete.html"), name='password_reset_complete'),

    # Add to Cart
    path('cart/add/<int:id>/', views.cart_add, name='cart_add'),
    path('cart/item_clear/<int:id>/', views.item_clear, name='item_clear'),
    path('cart/item_increment/<int:id>/',views.item_increment, name='item_increment'),
    path('cart/item_decrement/<int:id>/',views.item_decrement, name='item_decrement'),
    path('cart/cart_clear/', views.cart_clear, name='cart_clear'),
    path('cart/cart_detail/', views.cart_detail, name='cart_detail'),

    path('checkout/',views.checkout,name='checkout'),

    path('order/',views.your_order,name='order'),

    #rozerpay
    path('pay/', views.payment_page, name='payment_page'),
    path('search/', views.search_products, name='search_products'),

]+static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
