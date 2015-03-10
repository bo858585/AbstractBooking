# AbstractBooking

***Техническое задание и руководство по установке системы выполнения абстрактных заказов (отредактировано в http://dillinger.io)***

###Установка библиотек и остальных компонентов, необходимых для работы:
```sh
# Установить virtualenvwrapper, python, Django:
# (https://virtualenvwrapper.readthedocs.org/en/latest/)

pip install virtualenvwrapper
mkvirtualenv booking_venv
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

# Драйвер для бд:
pip install psycopg2

#Установка пароля для пользователя postgres:
sudo -u postgres psql template1
ALTER USER postgres with encrypted password 'postgres';

#Добавить строчку в pg_hba.conf:
sudo nano /etc/postgresql/9.4/main/pg_hba.conf
local   all             postgres                                trust

#Создать пользователя бд для django-приложения:
sudo -u postgres createuser -P django_dev
Пароль: django_dev_password

# (При необходимости пароль изменить так:)
sudo -u postgres psql template1
ALTER USER django_dev with encrypted password 'django_dev_password';

#Добавить postgres-пользователя в sudoers:
sudo nano /etc/sudoers
postgres ALL=(ALL) ALL

psql -U postgres
CREATE DATABASE django_db OWNER django_dev ENCODING 'UTF8';

#Настройки /etc/postgresql/9.4/main/pg_hba.conf :
local    all    postgres    trust
local    all    all    md5
local    django_db    django_dev    md5

# В корне проекта лежит пример настройки postgresql.conf.
# Его необходимо скопировать из корня проекта в /etc/postgresql/9.4/main/postgresql.conf:
cd proj_dir
cp ./postgresql.conf ./etc/postgresql/9.4/main/postgresql.conf

# Перезапуск бд
sudo service postgresql restart

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
command = /home/user/.virtualenvs/booking_venv/bin/uwsgi --socket :3031 --chdir /home/user/work/Booking/AbstractBooking/Booking --env DJANGO_SETTINGS_MODULE=Booking.settings --module "django.core.wsgi:get_wsgi_application()"
autostart = true
autorestart = true
stderr_logfile = /home/user/work/Booking/AbstractBooking/Booking/wsgi_err.log
stdout_logfile = /home/user/work/Booking/AbstractBooking/Booking/wsgi.log
redirect_stderr=true
stopwaitsecs = 60
stopsignal = INT

#Обновляем supervisor

sudo supervisorctl update

#Теперь мы можем проверить статус приложения командой

sudo supervisorctl status

#и перезапустить

sudo supervisorctl restart Booking
```

**Настройка nginx:**

```sh
apt-get install nginx
cp /etc/nginx/sites-available/default /etc/nginx/sites-available/_default
nano /etc/nginx/sites-available/default

#Вставить в default конфигурацию ниже:

server {
  listen   80;
  server_name localhost;

  error_log   /var/log/nginx/error.log;

  location /static/  {
    alias /home/user/work/Booking/AbstractBooking/Booking/static_for_deploy/;
    expires 30d;
  }

  location / {
    root            /home/user/work/Booking/AbstractBooking/Booking/Booking;
    uwsgi_pass      127.0.0.1:3031;
    include         uwsgi_params;
  }
}

#Теперь перезапускаем nginx:

sudo /etc/init.d/nginx reload
```

###Сущности:
1. **Пользователи.** Пользователь - либо администратор, либо принадлежит к одной из двух групп - исполнители, заказчики. Эти группы обладают различными правами.
2. **Расширенный профиль** пользователя.
3. **Заказ**.
4. **Счет системы**.


###Счет пользователя:
У любого заказчика, исполнителя может быть только по одному счету - поле в расширенном профиле модели пользователя. Профиль содержит поле "Счет":
DecimalField, NOT NULL, default = 100.

###Две группы пользователей с правами:
1. **customers** - booking.add_booking (создавать заказ).
2. **performers** - booking.perform_perm (брать заказ на исполнение).  


###Настройка и использование сущностей в админке:
1. **System accounts** - создать один счет системы, указать текущие денежные средства и комиссию системы.
2. **Группы** - создать две группы: customers, performers, назначить им права (см. ниже).
3. **Пользователи** - тестовых пользователей после создания групп можно завести в админке (например custuser, perfuser) и внести их в соответствующую группу. Также это можно сделать через форму регистрации, но после создания групп в админке. В этом случае расширенные профили пользователей будут созданы автоматически.
4. **User profiles**	- при создании тестовых пользователей в админке профили каждого из них также нужно заводить также через админку, при необходимости указать их денежные средства.

**Добавить группам в админке права:**

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
заказу назначается исполнитель - "NULL". Форма доступна только заказчикам.
В ней можно заполнить поля для модели заказа.

2. ######Лента заказов.
В ней отображается список заказов в виде таблицы. Невзятые на исполнение заказы
доступны для подачи заявок исполнителям. Заказчики могут их просматривать.
Завершенные заказы не отображаются. После того, как какой-нибудь из заказчиков
пытается взять заказ на исполнение, заказ становится доступен исполнителям
в списке только на чтение (исчезает соответсвующая кнопка подачи заявки на
исполнение). Для создавшенго его заказчика появляется кнопка подтверждания
заявки исполнителя и кнопка отклонения заявки. После подтверждения заказ
становится исполняемым тем исполнителем, который подавал заявку. Если заказчик
отклонит заявку, статус заказа возвращается к прежнему “Ожидает выполнения”.
Для каждого заказа в таблице выводится его название, описание, стоимость,
статус, заказчик, при наличии - исполнитель, соответствующие статусу кнопки,
дата и время создания. В начале на заказе есть кнопка “Взять заказ”, которая
отображается только исполнителям. Для пользователя, создавшего заказ в таблице
есть кнопка  "Удалить заказ" (заказ удалить нельзя, если заказ исполняется или
ожидает подтверждения взятия на исполнение).

 **Соответствие кнопок на заказе из ленты и текущих статусов этих заказов
(Надпись на кнопке - статус заказа):**
  - "Взять заказ" - "Ожидает выполнения"("pending").
  - "Подтвердить"/"Отклонить" - "Ожидает подтверждения" ("waiting_for_approval")
  - "Завершить заказ" - "Взят на исполнение"("running").
  - "Удалить заказ" - "Ожидает выполнения", “Завершен”
  - Заказ не отображается в ленте - “Завершен”("completed").

 **Схема отображения кнопок/действий в столбце таблицы:**
  - Взять заказ можно, если его статус "pending" и у заказчика достаточно
  средств для оплаты. Если средств недостаточно, заказ неактивен.
  - Завершить/Подтвердить/Отклонить заказ можно, если пользователь, создавший
  заказ, совпадает с текущим пользователем.
  - Строка таблицы не отображается, если статус заказа "completed".

3. ######При клике на кнопку “Взять заказ”:
Производится проверка, хватит ли заказчику этого заказа денег на оплату заказа.
Цена введенного заказа должна быть меньше (либо равна) сумме, которая у него
есть на счету. Заказу назначается статус “Ожидает подтверждения”. После этого
кнопка “Взять заказ”, доступная исполнителям, на заказе исчезает, появляются
кнопки “Подтвердить/Отклонить”, доступные только заказчику, сделавшему этот заказ.
Удалить в таком состоянии заказчик этот заказ не может.

4. ######При клике на кнопку “Подтвердить”:
Цена введенного заказа должна быть меньше (либо равна) сумме, которая у него
есть на счету. Со счета заказчика списывается цена заказа (она присутствует в
модели заказа). Заказу назначается  статус “Выполняется”. Заказ сохраняется.
Это значит, что системе в ленту заказов - виртуально, согласно статусу заказа -
перешли деньги со счета заказчика, то есть система выступает посредником
между заказчиком и исполнителем). Страница обновляется. После этого кнопки
“Подтвердить/Отклонить”, доступные этому заказчику, на заказе исчезают,
появляется кнопка “Завершить заказ”, доступная только ему. Удалить в таком
состоянии заказчик этот заказ не может.

5. ######При клике на кнопку “Отклонить”:
Статус заказа становится “Ожидает выполнения”. Удалять заказ теперь можно.
Как и подавать заявку на исполнение - любой исполнитель может это сделать.

6. ######При нажатии на кнопку “Завершить заказ”:
Сумма заказа в ленте в зависимости от комиссии (целое число от 0 до 100
процентов, указывается в админке с системном счете) делится на две части -
на счет исполнителя заказа (виден пользователю на его странице) и системы
(SystemAccount в админке) поступают две эти части суммы. Заказу назначается
статус “Завершен”. Заказчику выводятся сообщения с указанием этих сумм.
Страница обновляется. Заказ исчезает из ленты как выполнившийся.

7. ######Список заказов, связанных с пользователем:
Страница, в которой отображается список заказов самого пользователя - заказы,
в которых он является заказчиком или исполнителем. Этот список полностью
аналогичен списку всех заказов системы за тем исключением, что в нем
отображаются и завершенные заказы (сделано, чтобы пользователь видел историю
своих заказов).

8. ######Кнопка удаления заказа:
Заказчик может удалить свой заказ, если статус заказа не RUNNING (заказ не
обрабатывается в данный момент) и не WAITING_FOR_APPROVAL (заказ ждет
подтверждения на выполнение).

9. ######Разрешение спорных ситуаций между заказчиком и исполнителем:
email администратора

10. ######Интеграция с robokassa.
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
