# AbstractBooking

***Техническое задание (детальное описание) и руководство по установке системы выполнения заказов (услуг, продуктов) (отредактировано в http://dillinger.io)***

Booking - здесь "Заказ".
Демонстрационный проект-пример кода.

###Установка библиотек и остальных компонентов, необходимых для работы:
```sh
# Установить virtualenvwrapper, python, Django:
# (https://virtualenvwrapper.readthedocs.org/en/latest/)

pip install virtualenvwrapper
mkvirtualenv _Booking
pip install python
sudo apt-get install libpq-dev python-dev
pip install Django==1.7.5

# Согласно инуструкциям для Trusty 14.04, установить Postgres:
# (http://www.postgresql.org/download/linux/ubuntu/):

deb http://apt.postgresql.org/pub/repos/apt/ trusty-pgdg main
wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | \
sudo apt-key add -
sudo apt-get update
apt-get install postgresql-9.4

# Установить драйвер для Postgres:
pip install psycopg2

#Установка пароля для пользователя postgres:
sudo -u postgres psql template1
ALTER USER postgres with encrypted password 'postgres';

#Добавить строчку в pg_hba.conf:
sudo nano /etc/postgresql/9.4/main/pg_hba.conf
local   all             postgres                                md5

# Перезапуск бд
su postgres
su postgres /etc/init.d/postgresql stop
su postgres /etc/init.d/postgresql start
su your_user

(# Также бд можно перезапустить так, но потребуется указать trust в pg_hba.conf:
sudo service postgresql restart)

#Создать пользователя бд для django-приложения:
sudo -u postgres createuser -P django_dev
Пароль: django_dev_password

#Добавить postgres-пользователя в sudoers:
sudo nano /etc/sudoers
postgres ALL=(ALL) ALL

# Создать базу данных для проекта:
psql -U postgres
CREATE DATABASE django_db OWNER django_dev ENCODING 'UTF8';

# Добавить настройки в /etc/postgresql/9.4/main/pg_hba.conf:
# (Доступ по паролю для пользователя django-приложения)
local    django_db    django_dev    md5

# В корне проекта лежит пример настройки postgresql.conf
# Его необходимо скопировать из корня проекта в /etc/postgresql/9.4/main/postgresql.conf:
cd /etc/postgresql/9.4/main
cp postgresql.conf _postgresql.conf
cd proj_dir
cp postgresql.conf /etc/postgresql/9.4/main

# Перезапуск бд
su postgres
su postgres /etc/init.d/postgresql stop
su postgres /etc/init.d/postgresql start
su your_user

# Перезапуск бд можено делать и через
service postgresql restart
# Но понадобится выставить trust вместо md5 в pg_hba.conf

# При необходимости сгенерировать ssh ключ
https://help.github.com/articles/generating-ssh-keys/

# Склонировать проект
git clone git@github.com:bo858585/AbstractBooking.git
cd AbstractBooking

# Установить django-registration:
cd Booking
git clone https://github.com/macropin/django-registration
cd django-registration
python setup.py install

cd ../

python manage.py migrate
python manage.py syncdb
(создать admin-пользователя user/123)

# Соберем статику:

mkdir static_for_deploy
python manage.py collectstatic
```

###Развертывание

/home/user/work/Booking/AbstractBooking/Booking - этот путь к проекту везде необходимо заменить на локальный.

**Настройка supervisor:**

```sh
apt-get install supervisor
pip install uwsgi
sudo apt-get install uwsgi-plugin-python

# Конфигурационный файл

sudo nano /etc/supervisor/conf.d/Booking.conf

[program:Booking]
command = /home/user/.virtualenvs/_Booking/bin/uwsgi --socket :3031 --chdir /home/user/work/Booking/AbstractBooking/Booking --env DJANGO_SETTINGS_MODULE=Booking.settings --module "django.core.wsgi:get_wsgi_application()"
autostart = true
autorestart = true
stderr_logfile = /home/user/work/Booking/AbstractBooking/Booking/wsgi_err.log
stdout_logfile = /home/user/work/Booking/AbstractBooking/Booking/wsgi.log
redirect_stderr=true
stopwaitsecs = 60
stopsignal = INT

# Обновляем supervisor

sudo supervisorctl update

# Теперь мы можем проверить статус приложения командой

sudo supervisorctl status

# и перезапустить

sudo supervisorctl restart Booking
```

**Настройка nginx:**

Сгенерировать сертификат:
(для тестирования подойдет самоподписанный
http://dracoblue.net/dev/https-nginx-with-self-signed-ssl-certificate/)

```sh
apt-get install nginx

sudo -s
cd /etc/nginx
openssl req -new -x509 -nodes -out server.crt -keyout server.key
chmod 600 server.key

cp /etc/nginx/sites-available/default /etc/nginx/sites-available/_default

# Вставить в default файл из корня проекта
nano /etc/nginx/sites-available/default

# Теперь перезапускаем nginx:
sudo /etc/init.d/nginx reload

# Сайт доступен по адресам 127.0.0.1, http://127.0.0.1, https://127.0.0.1
```

###Сущности:
1. **Пользователи.** Пользователь - либо администратор, либо принадлежит к одной из двух групп - исполнители, заказчики. Эти группы обладают различными правами.
2. **Расширенный профиль** пользователя.
3. **Заказ**.
4. **Счет системы**.


###Счет пользователя:
У любого заказчика, исполнителя может быть только по одному счету - поле в расширенном профиле модели пользователя. Профиль содержит поле "Счет": DecimalField, NOT NULL, default = 100.

###Две группы пользователей с правами:
1. **customers** - booking.add_booking (создавать заказ).
2. **performers** - booking.perform_perm (брать заказ на исполнение).  


###Настройка и использование сущностей в админке:
1. **System accounts** - создать один счет системы (обязательно должен присутствовать), указать текущие денежные средства и комиссию системы.
2. **Группы** - создать две группы (обязательно должны присутствовать): customers, performers, назначить им права (см. ниже).
3. **Пользователи** - тестовых пользователей после создания групп можно завести в админке (например custuser, perfuser) и внести их в соответствующую группу. Также это можно сделать через форму регистрации, но после создания групп в админке. В этом случае расширенные профили пользователей будут созданы автоматически.
4. **User profiles**	- при создании тестовых пользователей в админке профили каждого из них также нужно заводить также через админку, при необходимости указать их денежные средства.

**Добавить группам в админке права:**(обязательно должны присутствовать)

1. performers - booking | booking | Ability to perform created booking
2. customers - booking | booking | Can add booking
3. customers - booking | booking | Can change booking
4. customers - booking | booking | Can delete booking

**Добавить пользователям группы в админке:**
1. custuser - customers,
2. perfuser - performers

Введенные в админке данные должны быть валидными.

###Элементы управления заказами в пользовательском интерфейсе списка заказов:
- **Для исполнителя:** исполняет заказ (кнопка в элементе списка в BookingListView).
- **Для заказчика:** завершает заказ (кнопка в элементе списка в BookingListView).

###Модель заказа:

######Статусы заказа (CHOICES в модели заказа):
1. **"Ожидает выполнения"** - начальный статус.
2. **"Взят на исполнение"** - статус назначается заказу после клика на кнопку
“Взять заказ” исполнителем.
3. **"Завершен"** - статус назначается заказу после клика на кнопку “Завершить заказ” исполнителем.

**CHOICES** = [ “pending”, “running”, “completed” ]

######Схема модели заказа:
- **Название** - CharField NOT NULL.
- **Описание** - TextField NOT NULL.
- **Стоимость** - IntegerField NOT NULL, default=100.
- **Статус** - CharField с choices - варианты внутри модели, один из них default.
- **Заказчик** - Foreign Key, NOT NULL.
- **Исполнитель** - Foreign Key (can be NULL).
- **Дата и время создания заказа** - стандартное поле.


###User stories.

1. ######Форма создания заказа: CreateView.
Когда заказчик формирует заказ через форму, он указывает стоимость заказа.
Заказу назначается введенная цена. Затем заказ сохраняется в таблицу-ленту
заказов, заказу автоматически назначается статуc - “Ожидает выполнения”,
заказу не назначается исполнитель - "NULL". Форма доступна только заказчикам.
В ней можно заполнить поля для модели заказа.

2. ######Лента заказов.
В ней отображается список заказов в виде таблицы. Заказы
доступны для подачи заявок исполнителям. Заказчики могут их просматривать и
пытаться брать на выполнение. Завершенные заказы не отображаются.
Несколько исполнителей одновременно могут пытаться взять заказ. Для создавшенго
заказ заказчика появляется кнопка подтверждания со списокм возможных исполнителей.
После подтверждения заказчиком одного из исполнителей заказ получает статус
становится исполняющегося. Для каждого заказа в таблице выводится его
название, описание, стоимость, статус, заказчик, при наличии - исполнитель,
соответствующие статусу кнопки, дата и время создания. В начале на заказе есть
кнопка “Взять заказ”, которая отображается только исполнителям. Для пользователя,
создавшего заказ в таблице есть кнопка  "Удалить заказ" (заказ удалить нельзя,
если заказ исполняется или ожидает подтверждения взятия на исполнение).

 **Соответствие кнопок на заказе из ленты и текущих статусов этих заказов
(Надпись на кнопке - статус заказа):**
  - "Взять заказ" - "Ожидает выполнения"("pending").
  - "Подтвердить" - "Ожидает подтверждения" ("waiting_for_approval")
  - "Завершить заказ" - "Взят на исполнение"("running").
  - "Удалить заказ" - "Ожидает выполнения", “Завершен” (для списка своих заказов пользователя.)
  - Заказ не отображается в ленте - “Завершен”("completed").

 **Схема отображения кнопок/действий в столбце таблицы:**
  - Взять заказ можно, если его статус "pending" и у заказчика достаточно
  средств для оплаты. Если средств недостаточно, заказ неактивен.
  - Завершить/Подтвердить заказ можно, если пользователь, создавший
  заказ, совпадает с текущим пользователем.
  - Строка таблицы не отображается, если статус заказа "completed".

3. ######При клике на кнопку “Взять заказ”:
Производится проверка, хватит ли заказчику этого заказа денег на оплату заказа.
Цена введенного заказа должна быть меньше (либо равна) сумме, которая у него
есть на счету. Заказу назначается статус “Ожидает подтверждения”. Появляются
кнопка “Подтвердить”, доступная только заказчику, сделавшему этот заказ.
Удалить в таком состоянии заказчик этот заказ не может.

4. ######При клике на кнопку “Подтвердить”:
Цена введенного заказа должна быть меньше (либо равна) сумме, которая у него
есть на счету. Со счета заказчика списывается цена заказа (она присутствует в
модели заказа). Заказу назначается  статус “Выполняется”. Заказ сохраняется.
Это значит, что системе в ленту заказов - виртуально, согласно статусу заказа -
перешли деньги со счета заказчика, то есть система выступает посредником
между заказчиком и исполнителем). Страница обновляется. После этого кнопка
“Подтвердить”, доступная этому заказчику, на заказе исчезают,
появляется кнопка “Завершить заказ”, доступная только ему. Удалить в таком
состоянии заказчик этот заказ не может.

5. ######При нажатии на кнопку “Завершить заказ”:
Сумма заказа в ленте в зависимости от комиссии (целое число от 0 до 100
процентов, указывается в админке с системном счете) делится на две части -
на счет исполнителя заказа (виден пользователю на его странице) и системы
(SystemAccount в админке) поступают две эти части суммы. Заказу назначается
статус “Завершен”. Заказчику выводятся сообщения с указанием этих сумм.
Страница обновляется. Заказ исчезает из ленты как выполнившийся.

6. ######Список заказов, связанных с пользователем:
Страница, в которой отображается список заказов самого пользователя - заказы,
в которых он является заказчиком или исполнителем. Этот список полностью
аналогичен списку всех заказов системы за тем исключением, что в нем
отображаются и завершенные заказы (сделано, чтобы пользователь видел историю
своих заказов).

7. ######Кнопка удаления заказа:
Заказчик может удалить свой заказ, если статус заказа не RUNNING (заказ не
обрабатывается в данный момент) и не WAITING_FOR_APPROVAL (заказ ждет
подтверждения на выполнение).

8. ######Разрешение спорных ситуаций между заказчиком и исполнителем:
email администратора

9. ######Интеграция с robokassa.
При регистрации пользователю начисляется бонус 1000. Система может быть
интегрирована с приложением django-robokassa для ввода средств юридическими лицами.

###Тесты

```sh

sudo -u postgres psql template1
alter user django_dev createdb;

$ cd /home/user/work/Booking/AbstractBooking/Booking
$ python manage.py test booking.tests.BookingModelTestCase
$ python manage.py test booking.tests.BookingViewsTestCase
$ python manage.py test booking.tests.BookingViewsPerformanceTestCase
```
