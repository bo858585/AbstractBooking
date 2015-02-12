# AbstractBooking

***Техническое задание (предварительное) на систему выполнения абстрактных заказов***


###Сущности:
1. Пользователи с профилями трех типов: заказчик, исполнитель, система (администратор).
2. Заказ.

У любого заказчика, исполнителя и cистемы может быть только по одному счету - поле в расширенном профиле модели пользователя. Профиль содержит поле "Счет": DecimalField, NOT NULL, default = 100.


###Права:
- Система: создавать заказ(CreateBooking view).
- Заказчик: создавать заказ (CreateBooking view).
- Исполнитель: исполнять заказ (кнопка в элементе списка в BookingListView).
- Заказчик: завершать заказ (кнопка в элементе списка в BookingListView).


###Модели:

######Статусы заказа (CHOICES в модели заказа):
1. "Ожидает выполнения" - начальный статус.
2. "Взят на исполнение" - статус назначается заказу после клика на кнопку “Взять заказ” исполнителем.
3. "Завершен" - статус назначается заказу после клика на кнопку “Завершить заказ” исполнителем.

CHOICES = [ “pending”, “running”, “completed” ]

######Схема модели заказа:
- Название - CharField NOT NULL.
- Описание - TextField NOT NULL.
- Стоимость - IntegerField NOT NULL, default=100.
- Статус - CharField с choices - варианты внутри модели, один из них default.
- Заказчик - Foreign Key, NOT NULL.
- Исполнитель - Foreign Key (can be NULL).
- Дата и время создания заказы - стандартное поле.


###User stories.
1.Когда заказчик формирует заказ через форму, он указывает стоимость заказа. Заказу назначается введенная цена. Затем заказ сохраняется в таблицу-ленту заказов, заказу автоматически назначается статуc - “Ожидает выполнения”, заказу назначается исполнитель - "NULL".
Форма создания заказа заказа: CreateView. Доступна только заказчикам. В ней можно заполнить поля для модели заказа.
Для отправки формы используется POST request.

2.Лента заказов BookingListView(BaseDatatableView, AjaxableResponseMixin).
https://pypi.python.org/pypi/django-datatables-view/1.10
https://docs.djangoproject.com/en/1.7/topics/class-based-views/generic-editing/
В ней отображаются заказы, доступные для исполнения (можно сделать исполняющиеся заказы также отображающимися в ленте). Для каждого заказа выводится его название, описание, стоимость, статус, заказчик, при наличии - исполнитель, соответствующая статусу кнопка, дата и время создания. В начале на заказе есть кнопка “Взять заказ”, которая отображается только исполнителям. Для других пользователей поле пустое (Если в таблице также отображать исполняющиеся заказы, заказы можно отсортировать и по статусу - вверху будут свободные заказы.)
Соответствие кнопок на заказе из ленты и текущих статусов этих заказов (Надпись на кнопке - статус заказа):
- "Взять заказ" - "Ожидает выполнения".
- "Завершить заказ" - "Взят на исполнение".
- Заказ не отображается в ленте - “Завершен”.

JQuery Datatable - плагин для отображения/рендеринга таблицы.
Модель заказа - строка таблицы, последняя колонка - кнопка для работы с заказом.
https://stackoverflow.com/questions/25975086/django-datatables-load-ajax-data-load
Класс, отвечающий за отрисовку таблицы, наследуется от двух классов:
BaseDatatableView - серверная обработка datatable плагина.
AjaxableResponseMixin - примесь для обработки нажатия на кнопки.

3.При клике на кнопку “Взять заказ”:
производится проверка, хватит ли заказчику этого заказа денег на оплату заказа - цена введенного заказа должна быть меньше (либо равна) сумме, которые у него есть на счету. Со счета заказчика списывается цена заказа. Она помещается в соответствующее поле модели заказа. Заказу назначается  статус “Выполняется”. Заказ сохраняется. (это значит, что системе в ленту заказов - виртульно, согласно статусу заказа - перешли деньги со счета заказчика, то есть система выступает посредником между заказчиком и исполнителем).
Страница обновляется (redirect).
После редиректа кнопка “Взять заказ” на заказе исчезает, появляется кнопка “Завершить заказ”, доступная только заказчику, сделавшему этот заказ.

4.При нажатии на кнопку “Завершить заказ”:
сумма заказа в ленте в зависимости от комиссии (целое число от 0 до 100 процентов, указывается в настройках) делится на две части - на счет исполнителя заказа и системы поступают две эти части суммы. Заказу назначается статус “Завершен”. Страница обновляется. Заказ исчезает из ленты как выполнившийся.

###Рендеринг таблицы:
Рендеринг кнопки последнего столбца таблицы происходит в классе BaseDatatableView в методе render_column() - рисуется разная кнопка в зависимости от того, какой статус у заказа.

В методе filter_queryset() фильтруется отображение строк - не отображаются выполненные заказы.

###Обработка нажатия кнопок в последнем столбце таблицы:
По нажатию кнопки в строке таблицы вызывается AJAX POST request по обработке заказа через AjaxableResponseMixin (с последующим изменением его статуса и редиректом на таблицу).

django-registration - необходимы приложение для регистрации пользователей двух типов и страница входа.
Стандартные средства входа django.
django-admin - админка с отображением ленты заказов.


###Для разработки установить:

1. virtualenvwrapper
https://virtualenvwrapper.readthedocs.org/en/latest/

2. python

3. postgresql http://paintincode.blogspot.ru/2012/08/install-postgresql-for-django-and.html
(проверить pg_conf с django https://stackoverflow.com/questions/7695962/postgresql-password-authentication-failed-for-user-postgres)

4. django

  После разработки установить проект в Docker контейнер.
