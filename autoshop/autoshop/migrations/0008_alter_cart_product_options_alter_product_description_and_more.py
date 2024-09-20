# Generated by Django 4.2.1 on 2023-05-28 18:05

from django.db import migrations, models
import utils.uploading


class Migration(migrations.Migration):

    dependencies = [
        ('autoshop', '0007_alter_order_cart'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='cart_product',
            options={'verbose_name': 'Товар в корзине', 'verbose_name_plural': 'Товары в корзине'},
        ),
        migrations.AlterField(
            model_name='product',
            name='description',
            field=models.TextField(blank=True, verbose_name='Описание'),
        ),
        migrations.AlterField(
            model_name='product',
            name='image',
            field=models.ImageField(upload_to=utils.uploading.upload_function, verbose_name='Изображение'),
        ),
    ]
