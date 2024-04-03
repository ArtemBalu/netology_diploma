from django.shortcuts import render
from models import *

from rest_framework.views import APIView
# Вход
# Регистрация
# Список товаров
# Корзина (просмотр, добавление, удаление)
# Контакты (просмотр, добавление, удаление)
# Подтверждение заказа
# Заказы просмотр списка

class UserRegistration(APIView):
    pass


class UserSignIn(APIView):
    pass


class ProductList(APIView):
    pass


class BasketView(APIView):
    pass


class ContactView(APIView):
    pass


class OrderConfirm(APIView):
    pass


class OrderView(APIView):
    pass