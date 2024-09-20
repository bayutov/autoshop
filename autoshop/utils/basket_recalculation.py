from django.db import models

def basket_recalculation(cart):
    #Подсчёт финальной цены и иденетификаторов
    cart_data = cart.products.aggregate(models.Sum("final_price"), models.Count("id"))

    # Проверка наличия общей суммы цен продуктов
    if cart_data.get("final_price__sum"):
        cart.final_price = cart_data["final_price__sum"]

    else:
        cart.final_price = 0

    # Установка общего количества продуктов в корзине
    cart.total_products = cart_data["id__count"]
    cart.save()
