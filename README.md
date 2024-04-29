# Заключительный учебный проект (дипломная работа)
### Данный проект создан в целях обучения. 

## Описание проекта

POST 'partner/update'
    обновление информации о магазине (добавление новых товаров в БД)
    пользователь должен быть аутентифицирован и являться продавцом

GET 'partner/orders'
    просмотр информации о заказах, полученных текщим продавцом
    пользователь должен быть аутентифицирован и являться продавцом

POST 'user/register'
    регистрация нового пользователя с валидацией данных
    обязательно передаются параметры: 'username', 'email', 'password'
    метод возвращает статус регистрации

POST 'user/register/confirm'
    подтверждение адреса электронной почты пользователя
    обязательные параметры: 'email', 'token' (созданный приемником сигнала в момент регистрации)
    метод возвращает статус подтверждения

GET 'user/details'
    просмотр данных о пользователе
    пользователь должен быть аутентифицирован

POST 'user/details'
    редактирование профиля пользователя
    пользователь должен быть аутентифицирован

POST 'user/signin'
    аутентификация пользователя
    обязательные параметры: 'username', 'password'
    метод возвращает статус и токен аутентификации

GET 'categories'
    просмотр списка всех категорий
    пользователь может быть анонимным

GET 'shops'
    просмотр информации о магазине, который связан с текущим пользователем
    пользователь должен быть аутентифицирован

POST 'shops'
    изменение стуса приема заказов
    пользователь должен быть аутентифицирован

GET 'products'
    отображение спика доступных товаров, используется стандартная фильтрация и поиск по полям
    пользователь может быть анонимным

GET 'basket'
    отображение содержимого предварительного заказа (корзины)
    подсчет общей стоимости заказа (с исключением повторов)
    пользователь должен быть аутентифицирован

POST 'basket'
    редактирование позиций в корзине
    обязательные параметры: 'items'
    пользователь должен быть аутентифицирован

PUT 'basket'
    добавление позиции в корзину
    обязательные параметры: 'items'
    пользователь должен быть аутентифицирован

DELETE 'basket'
    удаление позиций из корзины
    обязательные параметры: 'items'
    пользователь должен быть аутентифицирован

GET 'order'
    просмотр информации о заказах текущего пользователя
    пользователь должен быть аутентифицирован

POST 'order'
    размещение заказа из корзины
    пользователь должен быть аутентифицирован

'user/password_reset'
    сброс пароля

'user/password_reset/confirm'
    подтверждение сброса пароля