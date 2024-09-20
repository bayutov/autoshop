from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.utils.safestring import mark_safe
from django.urls import reverse
from django.utils import timezone
from django.conf import settings
import operator
from django.utils.safestring import mark_safe
from utils import upload_function
from django.db.models.signals import pre_save, post_save

# Create your models here.


class PrivacyPolicy(models.Model):
    """Политика конфиденциальности"""

    title = models.CharField(max_length=100)
    content = models.TextField()

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Политика конфиденциальности"
        verbose_name_plural = "Политики конфиденциальности"


class Manufacturer(models.Model):
    """Производитель"""

    name = models.CharField(max_length=100, verbose_name="Производитель")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Производитель"
        verbose_name_plural = "Производители"

class Product_type(models.Model):
    """Тип товара"""

    name = models.CharField(max_length=100, verbose_name="Тип товара")
    slug = models.SlugField()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Тип товара"
        verbose_name_plural = "Тип товаров"

class Product(models.Model):
    """Продукт"""

    #Ссылка на модель типа товара
    type = models.ForeignKey(Product_type, on_delete=models.CASCADE, verbose_name="Тип товара")
    #Ссылка на модель производителя товара
    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.CASCADE, verbose_name="Производитель")
    name = models.CharField(max_length=100, verbose_name="Название товара")
    #Приставка для формирования URL
    slug = models.SlugField()
    description = models.TextField(verbose_name="Описание", blank=True)
    stock = models.IntegerField(default=1, verbose_name="Наличие на складе")
    price = models.DecimalField(max_digits=9, decimal_places=2, verbose_name="Цена")
    offer_of_the_week = models.BooleanField(default=False,verbose_name="Предложение недели")
    #Изображение товара
    image = models.ImageField(upload_to=upload_function,verbose_name="Изображение")
    #Отсутствие в наличии
    out_of_stock = models.BooleanField(default=False, verbose_name="Нет в наличии")

    def __str__(self):
        #Строка id|тип|название товара
        return f"{self.id} | {self.type.name} | {self.name}"

    @property #вызывается как атрибут
    def ct_model(self):
        #Название модели в виде строки
        return self._meta.model_name

    def get_absolute_url(self):
        #URL на товар
        return reverse('product_detail', kwargs={"product_slug": self.slug})

    class Meta:
        #Для отображения названий в админке
        verbose_name = "Товар"
        verbose_name_plural = "Товары"

class Cart_product(models.Model):
    """Продукт корзины"""

    MODEL_CARTPRODUCT_DISPLAY_NAME_MAP = {
        "Product" : {"is_constructible" : True, "fields": ["name", "type.name"], "separator": ' - '}
    }

    user = models.ForeignKey("Customer", verbose_name="Покупатель", on_delete=models.CASCADE)
    cart = models.ForeignKey("Cart", verbose_name="Корзина", on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")
    qty = models.PositiveIntegerField(default=1) #кол-во
    final_price = models.DecimalField(max_digits=9, decimal_places=2, verbose_name="Общая цена")

    def __str__(self):
        return f"Товар: {self.content_object.name} (для корзины)"

    def save(self, *args, **kwargs):
        self.final_price = self.qty * self.content_object.price
        super().save(*args, **kwargs)

    @property
    def display_the_name(self):
        model_fields = self.MODEL_CARTPRODUCT_DISPLAY_NAME_MAP.get(self.content_object.__class__._meta.model_name.capitalize())
        if model_fields and model_fields["is_constructible"]:
            display_name = model_fields["separator"].join(
                [operator.attrgetter(field)(self.content_object) for field in model_fields["fields"]])
            return display_name
        if model_fields and not model_fields["is_constructible"]:
            display_name = operator.attrgetter(model_fields["field"])(self.content_object)
            return display_name

        return self.content_object

    class Meta:
        verbose_name = "Товар в корзине"
        verbose_name_plural = "Товары в корзине"

class Cart(models.Model):
    """Корзина"""

    owner = models.ForeignKey("Customer", verbose_name="Покупатель", on_delete=models.CASCADE)
    products = models.ManyToManyField(Cart_product, blank=True, related_name="related_cart", verbose_name="Продукты для корзины")
    total_products = models.IntegerField(default=0, verbose_name="Общее колличество товара")
    final_price = models.DecimalField(max_digits=9, decimal_places=2,verbose_name="Общая цена", null=True, blank=True)
    in_order = models.BooleanField(default=False)
    for_anonymous_user = models.BooleanField(default=False)

    def __str__(self):
        return str(self.id)

    def products_in_cart(self):
        return [c.content_object for c in self.products.all()]

    class Meta:
        verbose_name = "Корзина"
        verbose_name_plural = "Корзины"

class Order(models.Model):
    """Заказ пользователя"""

    STATUS_NEW = "new"
    STATUS_IN_PROGRESS = "in_progress"
    STATUS_READY = "is_ready"
    STATUS_COMPLETED = "completed"

    BUYING_TYPE_SELF = "self"
    BUYING_TYPE_DELIVERY = "delivery"

    STATUS_CHOCES = (
        (STATUS_NEW, "Новый заказ"),
        (STATUS_IN_PROGRESS, "Заказ в обработке"),
        (STATUS_READY, "Заказ готов"),
        (STATUS_COMPLETED, "Заказ выполнен")
    )

    BUYING_TYPE_CHOICES = (
        (BUYING_TYPE_SELF, "Самовывоз"),
        (BUYING_TYPE_DELIVERY, "Доставка")
    )

    customer = models.ForeignKey("Customer", verbose_name="Покупатель",related_name="orders", on_delete=models.CASCADE)
    first_name = models.CharField(max_length=200, verbose_name="Имя")
    last_name = models.CharField(max_length=200, verbose_name="Фамилия")
    phone = models.CharField(max_length=20, verbose_name="Телефон")
    cart = models.ForeignKey(Cart, verbose_name="Корзина",null=True,blank=True, on_delete=models.CASCADE)
    address = models.CharField(max_length=2000,verbose_name="Адрес", null=True,blank=True)
    status = models.CharField(max_length=100,verbose_name="Статус заказа", choices=STATUS_CHOCES, default=STATUS_NEW)
    buying_type = models.CharField(max_length=100, verbose_name="Тип заказа", choices=BUYING_TYPE_CHOICES)
    comment = models.TextField(verbose_name="Комментарий к заказу", null=True, blank=True)
    created_at = models.DateField(verbose_name="Дата создания заказа", auto_now=True)
    order_date = models.DateField(verbose_name="Дата получения заказа", default=timezone.now)

    def __str__(self):
        return str(self.id)

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"

class Customer(models.Model):
    """Покупатель"""

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Пользователь")
    is_active = models.BooleanField(default=True, verbose_name="Активный")
    customer_orders = models.ManyToManyField(Order, blank=True, verbose_name="Заказы покупателя", related_name="related_customer")
    wishlist = models.ManyToManyField(Product, blank=True, verbose_name="Список ожидания")
    phone = models.CharField(max_length=20, verbose_name="Номер телефона")
    address = models.TextField(null=True, blank=True, verbose_name="Адрес")

    def __str__(self):
        return f"{self.user.username}"

    class Meta:
        verbose_name = "Покупатель"
        verbose_name_plural = "Покупатели"

class Manage_Notification(models.Manager):
    def get_queryset(self):
        return super().get_queryset()

    def all(self, recipient):
        return self.get_queryset().filter(recipient=recipient, read=False)

    def make_all_read(self, recipient):
        qs = self.get_queryset().filter(recipient=recipient, read=False)
        qs.update(read=True)


class Notification(models.Model):
    """Уведомление"""

    recipient = models.ForeignKey(Customer, on_delete=models.CASCADE, verbose_name="Получатель")
    text = models.TextField()
    read = models.BooleanField(default=False)
    objects = Manage_Notification()

    def __str__(self):
        return f"Уведомление для {self.recipient.user.username} | id={self.id}"

    class Meta:
        verbose_name = "Уведомление"
        verbose_name_plural = "Уведомления"
























class ImageGallery(models.Model):
    """Галерея изображений"""

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")
    image = models.ImageField(upload_to=upload_function)
    use_is_slider = models.BooleanField(default=False)


    def image_url(self):
        return mark_safe(f'<image src="{self.image.url}" width="auto" height="200px"')

    def __str__(self):
        return f"Изображение для {self.content_object}"

    class Meta:
        verbose_name = "Галерея изображений"
        verbose_name_plural = "Галерея изображений"

def check_prev_qty(instance, **kwargs):
    try:
        product = Product.objects.get(id=instance.id)

    except Product.DoesNotExist:
        return None

    if not product.stock:
        instance.out_of_stock = True
    else:
        instance.out_of_stock = False

def send_notification(instance, **kwargs):
    # Есть ли товар в наличии и ранее был отсутствующим
    if instance.stock and instance.out_of_stock:
        # Получение всех пользователей, у которых данный товар находится в листе ожидания
        customers = Customer.objects.filter(wishlist__in=[instance])
        # Есть ли пользователи, ожидающие данный товар
        if customers.count():
            for i in customers:
                Notification.objects.create(recipient=i, text=mark_safe(f'Позиция <a href="{instance.get_absolute_url()}">{instance.name}</a>,' f'которую вы добавили в лист ожидания, появилась в наличии.'))
                # Удаление товара из листа ожидания пользователя
                i.wishlist.remove(instance)
post_save.connect(send_notification, sender=Product)
pre_save.connect(check_prev_qty,sender=Product)