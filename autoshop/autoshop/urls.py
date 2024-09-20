from django.urls import path
from .views import BaseView, ProductDetailView,Delete_From_WishListView ,Make_Order_View ,Checkout_View,LoginView,Add_to_wish_list, RegistrationView, AccountView, CartView, Add_to_CartView, Delete_from_cart_View, Change_in_quantity_View, PrivacyPolicyView, DeeleteNotifView
from django.contrib.auth.views import LogoutView



urlpatterns = [
    path('privacy-policy/', PrivacyPolicyView.as_view(), name='privacy_policy'),
    # Корзина
    path('cart/', CartView.as_view(), name='cart'),
    path('add-to-cart/<str:ct_model>/<str:slug>/', Add_to_CartView.as_view(), name="add_to_cart"),
    path('remove-from-cart/<str:ct_model>/<str:slug>/', Delete_from_cart_View.as_view(), name="delete_from_cart"),
    path('change-qty/<str:ct_model>/<str:slug>/', Change_in_quantity_View.as_view(), name="change_qty"),
    #Главная
    path('', BaseView.as_view(), name="base"),
    #Список ожидания
    path('add-to-wishlist/<int:product_id>/', Add_to_wish_list.as_view(), name='add_to_wishlist'),
    path('delete-from-wishlist/<int:product_id>/', Delete_From_WishListView.as_view(), name='delete_from_wishlist'),
    #Заказ
    path('checkout/', Checkout_View.as_view(), name='checkout'),
    path('make-order/', Make_Order_View.as_view(), name='make-order'),
    #Очистка уведомлений
    path('delete-notifications/', DeeleteNotifView.as_view(), name='delete-notifications'),
    #Личный кабинет
    path('account/', AccountView.as_view(), name='account'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='/'), name='logout'),
    path('registration/', RegistrationView.as_view(), name='registration'),
    #Страница товара
    path('<str:product_slug>/', ProductDetailView.as_view(), name="product_detail")
]