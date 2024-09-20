from django import views
from .models import Customer, Cart, Notification

class CartMixin(views.generic.detail.SingleObjectMixin, views.View):

    def dispatch(self, request, *args, **kwargs):
        cart = None
        #Для авторизованных пользователей
        if request.user.is_authenticated:
            customer = Customer.objects.filter(user=request.user).first()
            if not customer: #Создание объекта Customer для пользователя
                customer = Customer.objects.create(user=request.user)
            cart = Cart.objects.filter(owner=customer, in_order=False).first()
            if not cart:
                    cart = Cart.objects.create(owner=customer)

        self.cart = cart

        return super().dispatch(request, *args, **kwargs)


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cart'] = self.cart
        return context

class NotificationsMixin(views.generic.detail.SingleObjectMixin):

    @staticmethod
    def notifications(user):
        #Проверка, аутентифицирован ли пользователь
        if user.is_authenticated:
            #Получение всех уведомлений
            return Notification.objects.all(recipient=user.customer)
        #Для неавторизованного пользователя уведомления пусты
        return Notification.objects.none()

    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)
        context["notifications"] = self.notifications(self.request.user)
        return context