from django.utils import timezone

from django.db import models
from django.contrib.auth.models import AbstractUser
from .managers import TransactionQuerySet


class User(AbstractUser):
    pass


class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)

    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name


class Transaction(models.Model):
    TRANSACTION_TYPE_CHOICES = (
        ('income', 'Income'),
        ('expense', 'Expense'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    type = models.CharField(max_length=7, choices=TRANSACTION_TYPE_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField()

    objects = TransactionQuerySet.as_manager()

    def __str__(self):
        date_aware = timezone.localtime(self.date)
        date_formatted = date_aware.strftime('%Y-%m-%d %H:%M:%S')
        return f"{self.type} of {self.amount} on {date_formatted} by {self.user.username}"

    class Meta:
        ordering = ['-date']
