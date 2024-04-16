from django.shortcuts import render
from rest_framework.request import Request
from rest_framework.response import Response
from django.contrib.auth.password_validation import validate_password
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from django.http import JsonResponse
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db import IntegrityError
from django.db.models import Q, Sum, F
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from ..strbool import strtobool
from requests import get

import ujson
import yaml

from models import *
from serializers import *


class UserRegistration(APIView):
    # вынес отдельно валидацию пароля, в случае успеха возврат None
    def password_checker(self, password):
        try:
            validate_password(password)
        except Exception:
            return JsonResponse({'Status': False, 'Error': Exception})
    # Метод POST, проверка пароля, сохранение данных пользователя через сериализатор
    def post(self, request: Request, *args, **kwargs):
        user_serializer = UserSerializer(data=request.data)
        if {'first_name', 'last_name', 'email', 'password', 'company', 'position'}.issubset(request.data):
            result = self.password_checker(request.data['password'])
            # Проверим result, если с паролем все ок, он должен быть None
            if not result:
                user = user_serializer.save()
                user.set_pasword(request.data['password'])
                user.save()
                return JsonResponse({'Status': True})
        else:
            return JsonResponse({'Status': False, 'Errors': 'Не указаны все необходимые аргументы!'})


class UserSignIn(APIView):
    # метод POST, создание токена аутентификации
    def post(self, request: Request, *args, **kwargs):
        if {'username', 'password'}.issubset(request.data):
            user = authenticate(request, username=request.data['username'], password=request.data['password'])
            if user is not None:
                if user.is_active:
                    token, _ = Token.objects.get_or_create(user=user)
                    return JsonResponse({'Status': True, 'Token': token.key})
            return JsonResponse({'Status': False, 'Errors': 'Авторизация не выполнена!'})
        return JsonResponse({'Status': False, 'Errors': 'Не указаны все необходимые аргументы!'})


class EmailConfirmView(APIView):
     # Метод POST, создание токена подтверждения почты
     def post(self, request: Request, *args, **kwargs):
        if {'email', 'token'}.issubset(request.data):
            token = ConfirmEmailToken.objects.filter(user__email=request.data['email'], key=request.data['token']).first()
            if token:
                token.user.is_active = True
                token.user.save()
                token.delete()
                return JsonResponse({'Status': True})
            else:
                return JsonResponse({'Status': False, 'Errors': 'Неправильно указан токен или email'})
        return JsonResponse({'Status': False, 'Errors': 'Не указаны все необходимые аргументы'})


class ProductSearchView(APIView):
    # Отображение спика доступных товаров. Использую стандартную фильтрацию и поиск по полям
    queryset = ProductInfo.objects.all()
    serializer_class = ProductInfoSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['category', 'shop']
    search_fields = ['description', 'model']
    ordering_fields = ['price']


class BasketView(APIView):
    # Метод GET, отображение содержимого предварительного заказа (корзины)
    # Подсчет общей стоимости заказа (с исключением повторов)
    def get(self, request: Request, *args, **kwargs):
        # Проверка аутентификации
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)
        
        basket = Order.objects.filter(user = request.user.id, status = 'temporary').prefetch_related(
            'positions__product_info__product__category',
            'ordered_items__product_info__product__name').annotate(
            cost=Sum(F('positions__quantity') * F('positions__product_info__price'))).distinct()
        serializer = OrderSerializer(basket, many=True)
        return Response(serializer.data)

    # Метод POST, редактирование количества товара в корзине
    def post(self, request: Request, *args, **kwargs):
        # Проверка аутентификации
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)
        
        items_string = request.data.get('items')
        if items_string:
            try:
                items_dict = ujson.loads(items_string)
            except ValueError:
                return JsonResponse({'Status': False, 'Errors': 'Ошибка запроса'})
            else:
                basket, _ = Order.objects.get_or_create(user=request.user.id, status='temporary')
                for item in items_dict:
                    item.update({'order': basket.id})
                    serializer = OrderItemSerializer(data=item)
                    if serializer.is_valid():
                        try:
                            serializer.save()
                        except IntegrityError as error:
                            return JsonResponse({'Status': False, 'Errors': str(error)})
                    else:
                        return JsonResponse({'Status': False, 'Errors': serializer.errors})
                return JsonResponse({'Status': True})
        return JsonResponse({'Status': False, 'Errors': 'Не указаны все необходимые аргументы'})

    # Метод DELETE, удаление товара из корзины
    def delete(self, request: Request, *args, **kwargs):
        # Проверка аутентификации
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)

        items_string = request.data.get('items')
        if items_string:
            items_list = items_string.split(',')
            basket, _ = Order.objects.get_or_create(user=request.user.id, status='temporary')
            query = Q()
            objects_deleted = False
            for order_item_id in items_list:
                if order_item_id.isdigit():
                    query = query | Q(order=basket.id, id=order_item_id)
                    objects_deleted = True

            if objects_deleted:
                deleted_count = OrderItem.objects.filter(query).delete()[0]
                return JsonResponse({'Status': True, 'Удалено объектов': deleted_count})
        return JsonResponse({'Status': False, 'Errors': 'Не указаны все необходимые аргументы'})

    # Метод PUT, добавление товара в корзину
    def put(self, request: Request, *args, **kwargs):
        # Проверка аутентификации
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)

        items_string = request.data.get('items')
        if items_string:
            try:
                items_dict = ujson.loads(items_string)
            except ValueError:
                return JsonResponse({'Status': False, 'Errors': 'Ошибка запроса'})
            else:
                basket, _ = Order.objects.get_or_create(user=request.user.id, status='temporary')
                objects_updated = 0
                for order_item in items_dict:
                    if type(order_item['id']) == int and type(order_item['quantity']) == int:
                        objects_updated += OrderItem.objects.filter(order=basket.id, id=order_item['id']).update(
                            quantity=order_item['quantity'])

                return JsonResponse({'Status': True, 'Обновлено объектов': objects_updated})
        return JsonResponse({'Status': False, 'Errors': 'Не указаны все необходимые аргументы'})


class CategoryView(ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class ShopView(APIView):

    def get(self, request: Request, *args, **kwargs):
        shop = request.user.shop
        serializer = ShopSerializer(shop)
        return Response(serializer.data)

    def post(self, request: Request, *args, **kwargs):
        # Проверка аутентификации и того. что пользователь является продавцом (магазином)
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)
        if request.user.type != 'shop':
            return JsonResponse({'Status': False, 'Error': 'Пользователь должен иметь тип - магазин!'}, status=403)
            
        status = request.data.get('status')
        if status:
            try:
                Shop.objects.filter(user=request.user.id).update(status=strtobool(status))
                return JsonResponse({'Status': True})
            except ValueError as error:
                return JsonResponse({'Status': False, 'Errors': str(error)})
        return JsonResponse({'Status': False, 'Errors': 'Не указаны все необходимые аргументы'})


class AccountDetails(APIView):
    # Метод GET, позволяет получить данные пользователя, если он аутентифицирован
    def get(self, request: Request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    # Метод POST, редактирование профиля пользователя, если он аутентифицирован
    def post(self, request: Request, *args, **kwargs):
        # Проверка аутентификации
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)
        # Если меняется пароль, проверим его на сложность
        if 'password' in request.data:
            try:
                validate_password(request.data['password'])
            except Exception:
                return JsonResponse({'Status': False, 'Errors': Exception})
            else:
                request.user.set_password(request.data['password'])

        # Оставшиеся данные проверит сериализатор
        user_serializer = UserSerializer(request.user, data=request.data, partial=True)
        if user_serializer.is_valid():
            user_serializer.save()
            return JsonResponse({'Status': True})
        else:
            return JsonResponse({'Status': False, 'Errors': user_serializer.errors})


class PartnerUpdate(APIView):
   
    def post(self, request: Request, *args, **kwargs):
        # Проверка аутентификации и того, что пользователь является продавцом (магазином)
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)
        if request.user.type != 'shop':
            return JsonResponse({'Status': False, 'Error': 'Пользователь должен иметь тип - магазин!'}, status=403)

        url = request.data.get('url')
        if url:
            validate_url = URLValidator()
            try:
                validate_url(url)
            except ValidationError as e:
                return JsonResponse({'Status': False, 'Error': str(e)})
            else:
                stream = get(url).content

                data = yaml.load(stream, Loader=yaml.Loader)

                shop, _ = Shop.objects.get_or_create(name=data['shop'], user_id=request.user.id)
                for category in data['categories']:
                    category_object, _ = Category.objects.get_or_create(id=category['id'], name=category['name'])
                    category_object.shops.add(shop.id)
                    category_object.save()
                ProductInfo.objects.filter(shop_id=shop.id).delete()
                for item in data['goods']:
                    product, _ = Product.objects.get_or_create(name=item['name'], category_id=item['category'])

                    product_info = ProductInfo.objects.create(product_id=product.id,
                                                              external_id=item['id'],
                                                              model=item['model'],
                                                              price=item['price'],
                                                              price_rrc=item['price_rrc'],
                                                              quantity=item['quantity'],
                                                              shop_id=shop.id)
                    for name, value in item['parameters'].items():
                        parameter_object, _ = Parameter.objects.get_or_create(name=name)
                        ProductParameter.objects.create(product_info_id=product_info.id,
                                                        parameter_id=parameter_object.id,
                                                        value=value)

                return JsonResponse({'Status': True})

        return JsonResponse({'Status': False, 'Errors': 'Не указаны все необходимые аргументы'})


class PartnerOrders(APIView):

    def get(self, request, *args, **kwargs):

        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)

        if request.user.type != 'shop':
            return JsonResponse({'Status': False, 'Error': 'Только для магазинов'}, status=403)

        order = Order.objects.filter(
            ordered_items__product_info__shop__user_id=request.user.id).exclude(state='basket').prefetch_related(
            'ordered_items__product_info__product__category',
            'ordered_items__product_info__product_parameters__parameter').select_related('contact').annotate(
            total_sum=Sum(F('ordered_items__quantity') * F('ordered_items__product_info__price'))).distinct()

        serializer = OrderSerializer(order, many=True)
        return Response(serializer.data)


class OrderView(APIView):
    # получить мои заказы
    def get(self, request, *args, **kwargs):

        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)
        order = Order.objects.filter(
            user_id=request.user.id).exclude(state='basket').prefetch_related(
            'ordered_items__product_info__product__category',
            'ordered_items__product_info__product_parameters__parameter').select_related('contact').annotate(
            total_sum=Sum(F('ordered_items__quantity') * F('ordered_items__product_info__price'))).distinct()

        serializer = OrderSerializer(order, many=True)
        return Response(serializer.data)

    # разместить заказ из корзины
    def post(self, request, *args, **kwargs):

        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)

        if {'id', 'contact'}.issubset(request.data):
            if request.data['id'].isdigit():
                try:
                    is_updated = Order.objects.filter(
                        user_id=request.user.id, id=request.data['id']).update(
                        contact_id=request.data['contact'],
                        state='new')
                except IntegrityError as error:
                    print(error)
                    return JsonResponse({'Status': False, 'Errors': 'Неправильно указаны аргументы'})
                else:
                    if is_updated:
                        # new order is a signal to email
                        new_order.send(sender=self.__class__, user_id=request.user.id)
                        return JsonResponse({'Status': True})

        return JsonResponse({'Status': False, 'Errors': 'Не указаны все необходимые аргументы'})
