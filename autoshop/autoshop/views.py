from django.shortcuts import render
from django import views
from django.contrib.contenttypes.models import ContentType
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate,login
from utils.basket_recalculation import basket_recalculation
from .models import Product, Customer, Cart,Notification, Cart_product, PrivacyPolicy
from .mixins import CartMixin, NotificationsMixin
from .forms import LoginForm, RegistrationForm, OrderForm
from django.views.generic import TemplateView
from django.db import transaction
# Create your views here.

class BaseView(CartMixin,NotificationsMixin, views.View):


    def get(self,request,*args,**kwargs):
        products = Product.objects.all().order_by('-id')
        #print(self.cart)
        context = {
            'products': products,
            'cart': self.cart,
            'notifications': self.notifications(request.user)
        }
        return render(request, 'base.html', context)


class PrivacyPolicyView(NotificationsMixin,views.View):
    def get(self, request):
        privacy_policy = PrivacyPolicy.objects.first()
        context = {
            'privacy_policy': privacy_policy,
            'notifications': self.notifications(request.user)
        }
        return render(request, 'privacy_policy.html', context)

class ProductDetailView(NotificationsMixin,CartMixin, views.generic.DetailView):
    model = Product
    template_name = 'product/product_detail.html'
    slug_url_kwarg = 'product_slug'
    context_object_name = 'product'


class LoginView(views.View):
    def get(self, request, *args, **kwargs):
        #Обработка GET-запроса для отображения формы входа
        form = LoginForm(request.POST or None)
        context = {
            "form": form
        }
        #Отрисовка страницы с переданным контекстом
        return render(request, 'login.html', context)

    def post(self, request, *args, **kwargs):
        #Обработка POST-запроса после отправки формы входа
        form = LoginForm(request.POST or None)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            user = authenticate(username=username, password=password)
            if user:
                #Перенаправление на главную после аутентификации
                login(request, user)
                return HttpResponseRedirect('/')
        context = {
            'form': form
        }
        #Отрисовка страницы с переданным контекстом
        return render(request, "login.html", context)


class RegistrationView(views.View):
    def get(self, request, *args, **kwargs):
        form = RegistrationForm(request.POST or None)
        context = {
            "form":form
        }
        return render(request, 'registration.html', context)


    def post(self, request, *args, **kwargs):
        form = RegistrationForm(request.POST or None)
        if form.is_valid():
            new_user = form.save(commit=False)
            new_user.username = form.cleaned_data["username"]
            new_user.email = form.cleaned_data["email"]
            new_user.first_name = form.cleaned_data["first_name"]
            new_user.last_name = form.cleaned_data["last_name"]
            new_user.save()
            new_user.set_password(form.cleaned_data["password"])
            new_user.save()
            Customer.objects.create(
                user = new_user,
                phone = form.cleaned_data["phone"],
                address= form.cleaned_data["address"]
            )
            user  = authenticate(username=form.cleaned_data["username"], password=form.cleaned_data["password"])
            login(request, user)
            return HttpResponseRedirect('/')
        context = {
            "form" : form
        }
        return render(request,'registration.html', context)

class CartView(NotificationsMixin,CartMixin, views.View):
    def get(self,request, *args, **kwargs):
        return render(request, 'cart.html', {"cart": self.cart,'notifications': self.notifications(request.user)}, )

class AccountView(NotificationsMixin,CartMixin, views.View):
    def get(self, request, *args, **kwargs):
        customer = Customer.objects.get(user=request.user)
        context = {
            "customer": customer,
            "cart" : self.cart,
            'notifications': self.notifications(request.user)
        }
        return render(request, 'account.html', context)

class Add_to_CartView(CartMixin, views.View):

    def get(self, request, *args, **kwargs):

        # /product/ct_model/slug/

        ct_model, product_slug = kwargs.get("ct_model"), kwargs.get("slug")
        content_type = ContentType.objects.get(model=ct_model)
        product = content_type.model_class().objects.get(slug=product_slug)
        cart_product, created = Cart_product.objects.get_or_create(
            user=self.cart.owner, cart=self.cart, content_type=content_type, object_id=product.id)
        if created:
            self.cart.products.add(cart_product)

        basket_recalculation(self.cart)

        messages.add_message(request, messages.INFO, "Товар добавлен.")

        #Перенаправление на предыдущюю страницу
        return HttpResponseRedirect(request.META["HTTP_REFERER"])

class Delete_from_cart_View(CartMixin, views.View):
    def get(self,request, *args, **kwargs):
        ct_model, product_slug = kwargs.get("ct_model"), kwargs.get("slug")
        content_type = ContentType.objects.get(model=ct_model)
        product = content_type.model_class().objects.get(slug=product_slug)
        cart_product = Cart_product.objects.get(
            user=self.cart.owner, cart=self.cart, content_type=content_type, object_id=product.id)
        self.cart.products.remove(cart_product)
        cart_product.delete()
        basket_recalculation(self.cart)
        messages.add_message(request, messages.INFO, "Товар удалён.")

        #Перенаправление на предыдущюю страницу
        return HttpResponseRedirect(request.META["HTTP_REFERER"])

class Change_in_quantity_View(CartMixin, views.View):

    def post(self, request, *args, **kwargs):
        ct_model, product_slug = kwargs.get("ct_model"), kwargs.get("slug")
        content_type = ContentType.objects.get(model=ct_model)
        product = content_type.model_class().objects.get(slug=product_slug)
        cart_product = Cart_product.objects.get(
            user=self.cart.owner, cart=self.cart, content_type=content_type, object_id=product.id)

        qty = int(request.POST.get("qty"))
        cart_product.qty = qty
        cart_product.save()
        basket_recalculation(self.cart)
        messages.add_message(request, messages.INFO, "Количество товара изменено.")

        #Перенаправление на предыдущюю страницу
        return HttpResponseRedirect(request.META["HTTP_REFERER"])

class Add_to_wish_list(views.View):
    @staticmethod
    def get(request, *args, **kwargs):
        product = Product.objects.get(id=kwargs["product_id"])
        customer = Customer.objects.get(user=request.user)
        customer.wishlist.add(product)
        return HttpResponseRedirect(request.META['HTTP_REFERER'])

class DeeleteNotifView(views.View):
    def get(self, request,*args,**kwargs):
        Notification.objects.make_all_read(recipient=request.user.customer)
        return HttpResponseRedirect(request.META['HTTP_REFERER'])

class Delete_From_WishListView(views.View):
    @staticmethod
    def get(request, *args, **kwargs):
        product = Product.objects.get(id=kwargs['product_id'])
        customer = Customer.objects.get(user=request.user)
        customer.wishlist.remove(product)
        return HttpResponseRedirect(request.META['HTTP_REFERER'])

class Checkout_View(CartMixin, NotificationsMixin, views.View):
    def get(self, request, *args, **kwargs):
        form = OrderForm(request.POST or None)
        context = {
            "cart": self.cart,
            "form": form,
            "notifications": self.notifications(request.user)
        }
        return render(request, "checkout.html", context)

class Make_Order_View(CartMixin, views.View):
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        form = OrderForm(request.POST or None)
        customer = Customer.objects.get(user=request.user)
        if form.is_valid():
            out_of_stock = []
            more_than_on_stock = []
            out_of_stock_message = ''
            more_than_on_stock_message = ''
            for item in self.cart.products.all():
                if not item.content_object.stock:
                    out_of_stock.append(' - '.join([item.content_object.name]))
                if item.content_object.stock and item.content_object.stock < item.qty:
                    more_than_on_stock.append(
                        {'product': ' - '.join([item.content_object.name]),
                         'stock': item.content_object.stock, 'qty': item.qty}
                    )
            if out_of_stock:
                out_of_stock_products = ", ".join(out_of_stock)
                out_of_stock_message = f"Нет в наличии: {out_of_stock_products} \n"
            if more_than_on_stock:
                for item in more_than_on_stock:
                    more_than_on_stock_message += f"Недостаточно товара в наличии. Товар: {item['product']}. В наличии: {item['stock']}. В заказе: {item['qty']}\n"
            error_message = ''
            if out_of_stock:
                error_message = out_of_stock_message + '\n'
            if more_than_on_stock_message:
                error_message += more_than_on_stock_message + '\n'

            if error_message:
                messages.add_message(request, messages.INFO, error_message)
                return HttpResponseRedirect('/checkout/')
            new_order = form.save(commit=False)
            new_order.customer = customer
            new_order.first_name = form.cleaned_data["first_name"]
            new_order.last_name = form.cleaned_data["last_name"]
            new_order.phone = form.cleaned_data["phone"]
            new_order.address = form.cleaned_data["address"]
            new_order.buying_type = form.cleaned_data["buying_type"]
            new_order.order_date = form.cleaned_data["order_date"]
            new_order.comment = form.cleaned_data["comment"]
            new_order.save()


            self.cart.in_order = True
            self.cart.save()
            new_order.cart = self.cart
            new_order.save()
            customer.orders.add(new_order)
            for item in self.cart.products.all():
                item.content_object.stock -= item.qty
                item.content_object.save()

            messages.add_message(request, messages.INFO, "Заказ успешно оформлен! Ожидайте ответа от менеджера.")
            return HttpResponseRedirect('/')
        return HttpResponseRedirect('/checkout/')