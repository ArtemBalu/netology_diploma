from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from models import *


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User
    list_display = (
        'email', 'first_name', 'last_name', 
        'username', 'is_staff', 'date_joined',
        'type', 'company', 'position',
        'adress', 'phone'
        )


@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    model = Shop


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    model = Category


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    model = Product


@admin.register(ProductInfo)
class ProductInfoAdmin(admin.ModelAdmin):
    model = ProductInfo


@admin.register(Parameter)
class ParameterAdmin(admin.ModelAdmin):
    model = Parameter


@admin.register(ProductParameter)
class ProductParameterAdmin(admin.ModelAdmin):
    model = ProductParameter


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    model = Order


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    model = OrderItem


@admin.register(ConfirmEmailToken)
class ConfirmEmailTokenAdmin(admin.ModelAdmin):
    model = ConfirmEmailToken
    list_display = ('user', 'key', 'created_at',)