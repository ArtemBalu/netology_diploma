from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.base_user import BaseUserManager


class User(AbstractUser):

    # В стандартной модели пользователя уже имеется:
    # _state — используется для сохранения состояния пользователя
    # id — уникальный идентификатор пользователя
    # password — зашифрованный пароль пользователя
    # last_login — дата и время последнего входа пользователя
    # is_superuser — истинно, если пользователь является суперпользователем, иначе — ложно
    # username — уникальное имя пользователя
    # first_name — имя пользователя
    # last_name — фамилия пользователя
    # email — идентификатор электронного адреса пользователя
    # is_staff — истинно, если пользователь является сотрудником, иначе — ложно
    # is_active — истинно, если профиль пользователя активен
    # date_joined — дата и время первого входа пользователя (заполняется автоматически)

    USER_TYPE_CHOICES = (
        ('shop', 'Магазин'),
        ('buyer', 'Покупатель'),
    )
    
    type = models.CharField(verbose_name='Тип пользователя', choices=USER_TYPE_CHOICES, max_length=5, default='buyer')
    company = models.CharField(verbose_name='Компания', max_length=100, blank=True)
    position = models.CharField(verbose_name='Должность', max_length=100, blank=True)
    adress = models.EmailField(max_length=500, verbose_name='Адрес')
    phone = models.IntegerField(verbose_name='Телефон')
    # Исключил модель Контакты, так как не вижу смысла в ее наличии

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return f'{self.first_name} {self.last_name}, {self.email}, {self.phone}'


class UserManager(BaseUserManager):
    use_in_migrations = True # параметр класса BaseManager для сериализации класса UserManager

    def create_user(self, username, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        if not username or not email:
            raise ValueError('Поля username и email не могут быть пустыми!')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, username, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        if not extra_fields.get('is_staff'):
            raise ValueError('Поле is_staff должно быть True для суперпользователя!')
        if not extra_fields.get('is_superuser'):
            raise ValueError('Поле is_superuser должно быть True для суперпользователя!')
        if not username or not email:
            raise ValueError('Поля username и email не могут быть пустыми!')
        email = self.normalize_email(email)
        superuser = self.model(username=username, email=email, **extra_fields)
        superuser.set_password(password)
        superuser.save(using=self._db)
        return superuser

class Shop(models.Model):
    ORDERS_CHOICES = (
        ('open', 'Заказы открыты'),
        ('closed', 'Заказы закрыты'),
    )

    name = models.CharField(max_length=50, verbose_name='Название')
    url =  models.URLField(verbose_name='Ссылка', null=True, blank=True)
    user = models.OneToOneField(User, verbose_name='Ассоциированный пользователь', on_delete=models.CASCADE)
    status = models.CharField(verbose_name='Прием заказов', choices=ORDERS_CHOICES, max_length=20)

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
    model = models.CharField(max_length=100, verbose_name='Модель')
    shop = models.ForeignKey(Shop, verbose_name='Магазин', related_name='product_info', blank=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=40, verbose_name='Название')
    description = models.TextField(max_length=5000, verbose_name='Информация о товаре')
    quantity = models.IntegerField(verbose_name='Количество')
    price = models.DecimalField(decimal_places=2, verbose_name='Цена')
    recomended_price = models.DecimalField(decimal_places=2, verbose_name='Рекомедованная розничная цена')

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