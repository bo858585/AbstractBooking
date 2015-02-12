from django.contrib.auth.models import User


class Customer(models.Model):
    user = models.OneToOneField(User, related_name='customer')
    cash = models.DecimalField(max_digits=6, decimal_places=2)


class Performer(models.Model):
    user = models.OneToOneField(User, related_name='performer')
    cash = models.DecimalField(max_digits=6, decimal_places=2)


class System(models.Model):
    user = models.OneToOneField(User, related_name='system')
    cash = models.DecimalField(max_digits=6, decimal_places=2)
