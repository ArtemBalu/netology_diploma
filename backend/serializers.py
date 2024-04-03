from rest_framework import serializers
from models import User, Shop, Category, Product, ProductInfo, ProductParameter, Order, OrderItem

class UserSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = User
        fields = ('id', 'adress', 'phone')
        read_only_fields = ('id')


class ShopSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True, many=True)

    class Meta:
        model = Shop
        fields = ('id', 'name', 'url', 'status', 'user')
        read_only_fields = ('id')


class CategorySerializer(serializers.ModelSerializer):
    shops = ShopSerializer(read_only=True, many=True)

    class Meta:
        model = Category
        fields = ('id', 'name', 'shop')
        read_only_fields = ('id')


class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True, many=True)

    class Meta:
        model = Product
        fields = ('id', 'name', 'category')
        read_only_fields = ('id')


class ProductInfoSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True, many=True)
    parameters = serializers.StringRelatedField(read_only=True, many=True)

    class Meta:
        model = ProductInfo
        fields = ('id', 'product', 'model', 'shop', 'name', 'description', 'quantity', 'price', 'recomended_price')
        read_only_fields = ('id')


class ProductParameterSerializer(serializers.ModelSerializer):
    product_info = ProductInfoSerializer(read_only=True, many=True)

    class Meta:
        model = ProductParameter
        fields = ()
        read_only_fields = ('id')
        

class OrderSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True, many=True)

    class Meta:
        model = Order
        fields = ('id', 'user', 'created_at', 'status')
        read_only_fields = ('id')


class OrderItemSerializer(serializers.ModelSerializer):
    order = OrderSerializer(read_only=True, many=True)
    product_info = ProductInfoSerializer(read_only=True, many=True)
    
    class Meta:
        model = OrderItem
        fields = ('id', 'order', 'product_info', 'quantity')
        read_only_fields = ('id')


class OrderItemCreateSerializer(serializers.ModelSerializer):
    pass