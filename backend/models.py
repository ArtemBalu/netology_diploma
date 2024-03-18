from django.db import models

# Create your models here.

class User(models.Model):
    USER_TYPE_CHOICES = (
        ('shop', 'Магазин'),
        ('buyer', 'Покупатель'),
        ('admin', 'Администратор'),
    )
    first_name = models.CharField(max_length=50, verbose_name='Имя')
    last_name = models.CharField(max_length=50, verbose_name='Фамилия')
    email = models.EmailField(unique=True, verbose_name='Электронная почта')
    type = models.CharField(verbose_name='Тип пользователя', choices=USER_TYPE_CHOICES, max_length=5, default='buyer')

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return f'{self.first_name} {self.last_name}, {self.email}'

class Shop(models.Model):
    name = models.CharField(max_length=50, verbose_name='Название')
    url =  models.URLField(verbose_name='Ссылка', null=True, blank=True)

    class Meta:
        verbose_name = 'Магазин'
        verbose_name_plural = 'Магазины'

    def __str__(self):
        return self.name

class Category(models.Model):
    name = models.CharField(max_length=40, verbose_name='Название')
    shops = models.ManyToManyField(Shop, verbose_name='Магазины', related_name='categories', blank=True)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=40, verbose_name='Название')
    category = models.ForeignKey(Category, verbose_name='Категория', related_name='products', blank=True, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'

    def __str__(self):
        return self.name

class ProductInfo(models.Model):
    product = models.ForeignKey(Product, verbose_name='Описание товара', related_name='product_info', blank=True, on_delete=models.CASCADE)
    shop = models.ForeignKey(Shop, verbose_name='Магазин', related_name='product_info', blank=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=40, verbose_name='Название')
    description = models.TextField(max_length=5000, verbose_name='Описание')
    quantity = models.IntegerField(verbose_name='Количество')
    price = models.DecimalField(decimal_places=2, verbose_name='Цена')
    rrc_price = models.DecimalField(decimal_places=2, verbose_name='Рекомедованная розничная цена')

    class Meta:
        verbose_name = 'Карточка информации о товаре'
        verbose_name_plural = 'Карточки информации о товаре'

    def __str__(self):
        return self.name

class Parameter(models.Model):
    name = models.CharField(max_length=40, verbose_name='Пользовательский параметр')
    
    class Meta:
        verbose_name = 'Имя доп. параметра'
        verbose_name_plural = 'Имена доп. параметров'

    def __str__(self):
        return self.name

class ProductParameter(models.Model):
    product_info = models.ForeignKey(ProductInfo, verbose_name='Карточка информации о товаре', related_name='parameters', on_delete=models.CASCADE)
    parameter = models.ForeignKey(Parameter, verbose_name='Параметр', related_name='parameters', blank=True, on_delete=models.CASCADE)
    value = models.CharField(verbose_name='Значение', max_length=100)

    class Meta:
        verbose_name = 'Дополнительный параметр'
        verbose_name_plural = 'Дополнительные параметры'

    def __str__(self):
        return f'{self.parameter}: {self.value}'


class Order(models.Model):
    STATUS_CHOICES = (
        ('temporary', 'Подбор товаров'),
        ('new', 'Новый'),
        ('accepted', 'Принят'),
        ('assembled', 'Собран'),
        ('sent', 'Отправлен'),
        ('delivered', 'Доставлен'),
        ('canceled', 'Отменен'),
        )
    
    user = models.ForeignKey(User, verbose_name='Покупатель', related_name='orders', blank=True, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата и время создания')
    status = models.CharField(verbose_name='Статус', choices=STATUS_CHOICES, max_length=20)

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

    def __str__(self):
        return f'Заказ {self.id} пользователя {self.user}'


class OrderItem(models.Model):
    order = models.ForeignKey(Order, verbose_name='Заказ', related_name='positions', blank=True, on_delete=models.CASCADE)
    product_info = models.ForeignKey(ProductInfo, verbose_name='Карточка товара', related_name='orders', blank=True, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(verbose_name='Количество')

    class Meta:
        verbose_name = 'Позиция заказа'
        verbose_name_plural = 'Позиции заказов'

    def __str__(self):
        return f'Позиция {self.product_info} заказа {self.order}'


class Contact(models.Model):
    user = models.OneToOneField(User, verbose_name='Пользователь', related_name='contacts', on_delete=models.CASCADE)
    adress = models.EmailField(max_length=500, verbose_name='Адрес')
    phone = models.IntegerField(verbose_name='Телефон')

    class Meta:
        verbose_name = 'Карточка контактов пользователя'
        verbose_name_plural = 'Карточки контактов пользователей'

    def __str__(self):
        return self.user