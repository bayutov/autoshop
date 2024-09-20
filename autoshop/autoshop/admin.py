from django.contrib import admin

# Register your models here.

from django.contrib.contenttypes.admin import GenericTabularInline
from .models import *


class ImageGalleryInline(GenericTabularInline):

    model = ImageGallery
    readonly_fields = ("image_url",)


admin.site.register(Product_type)
admin.site.register(Manufacturer)
admin.site.register(Product)
admin.site.register(ImageGallery)
admin.site.register(Cart)
admin.site.register(Cart_product)
admin.site.register(Order)
admin.site.register(Customer)
admin.site.register(Notification)
admin.site.register(PrivacyPolicy)

