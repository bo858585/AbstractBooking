from django.contrib.auth.models import User


class ExtendedUser(models.Model):
    user = models.OneToOneField(User, related_name='customer')
    cash = models.DecimalField(max_digits=6, decimal_places=2)
