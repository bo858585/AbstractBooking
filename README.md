# AbstractBooking

***Техническое задание (предварительное) на систему выполнения абстрактных заказов***


###Сущности:
1. Пользователи с профилями трех типов: заказчик, исполнитель, система (администратор).
2. Заказ.

У любого заказчика, исполнителя и cистемы может быть только по одному счету - поле в расширенном профиле модели пользователя. Профиль содержит поле "Счет": DecimalField, NOT NULL, default = 100.

Три группы пользователей с правами:
1. system: all rights to booking model.
2. customers - booking.add_booking.
3. performers - брать заказы на исполнение.  

Тестовые пользователи в админке: user, custuser, perfuser.

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
Форма создания заказа: CreateView. Доступна только заказчикам. В ней можно заполнить поля для модели заказа.
Для отправки формы используется POST request.

2.Лента заказов.

В ней отображаются заказы, доступные для исполнения.
- Созданные заказы отображаются только пользователю, создавшему заказ и всем исполнителям.
- Исполняющиеся заказы отображаются только пользователю, создавшему заказ и пользователю, взявшему его на исполнение.
- Завершенные и удаленные заказы не отображаются.

Для каждого заказа выводится его название, описание, стоимость, статус, заказчик, при наличии - исполнитель, соответствующая статусу кнопка, дата и время создания. В начале на заказе есть кнопка “Взять заказ”, которая отображается только исполнителям. (Для пользователя, создавшего заказ, на месте этой кнопки располагается кнопка "Удалить заказ" - продвинутый вариант)

 Соответствие кнопок на заказе из ленты и текущих статусов этих заказов (Надпись на кнопке - статус заказа):
- "Взять заказ"/"Удалить заказ" - "Ожидает выполнения"("pending").
- "Завершить заказ" - "Взят на исполнение"("running").
- Заказ не отображается в ленте - “Завершен”("completed").


Схема отображения кнопок/действий в столбце таблицы:
- Взять/Удалить заказ можно, если его статус "pending".
- Завершить заказ можно, если его статус "running" и пользователь, создавший заказ, совпадает с текущим пользователем.
- Строка таблицы не отображается, если статус заказа "completed".


(2*) Продвинутый вариант таблицы (JQuery Datatable).
JQuery Datatable - плагин для отображения/рендеринга таблицы.
Модель заказа - строка таблицы, последняя колонка - кнопка для работы с заказом.
POST request - для нажатия на кнопки в последнем столбце таблицы и отправки заказа.

3.При клике на кнопку “Взять заказ”:
производится проверка, хватит ли заказчику этого заказа денег на оплату заказа - цена введенного заказа должна быть меньше (либо равна) сумме, которые у него есть на счету. Со счета заказчика списывается цена заказа. Она помещается в соответствующее поле модели заказа. Заказу назначается  статус “Выполняется”. Заказ сохраняется. (это значит, что системе в ленту заказов - виртульно, согласно статусу заказа - перешли деньги со счета заказчика, то есть система выступает посредником между заказчиком и исполнителем).
Страница обновляется (redirect).
После редиректа кнопка “Взять заказ” на заказе исчезает, появляется кнопка “Завершить заказ”, доступная только заказчику, сделавшему этот заказ.

4.При нажатии на кнопку “Завершить заказ”:
сумма заказа в ленте в зависимости от комиссии (целое число от 0 до 100 процентов, указывается в настройках) делится на две части - на счет исполнителя заказа и системы поступают две эти части суммы. Заказу назначается статус “Завершен”. Страница обновляется. Заказ исчезает из ленты как выполнившийся.

Недочеты работы кнопок взятия и завершения заказа:
1. При включенном AJAX не происходит сокрытия кнопок (нужно перезагружать страницу).
2. На сервере не проверяются права пользователя при изменении статуса заказа (необходимо выяснить,  нужно это делать или нет).
3. Перевод средств.


###Обработка нажатия кнопок в последнем столбце таблицы при включенном ajax:
По нажатию кнопки в строке таблицы вызывается AJAX POST request по обработке
заказа с последующим изменением его статуса и редиректом на таблицу.

Стандартные средства входа django.
django-admin - админка с отображением ленты заказов и возможностью редактирования.


###Для разработки установить:

1. virtualenvwrapper
https://virtualenvwrapper.readthedocs.org/en/latest/

2. python

3. postgresql http://paintincode.blogspot.ru/2012/08/install-postgresql-for-django-and.html
(проверить pg_conf с django https://stackoverflow.com/questions/7695962/postgresql-password-authentication-failed-for-user-postgres)

4. django

5. После разработки установить проект в Docker контейнер.
