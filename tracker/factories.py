import random
from decimal import Decimal

from django.utils import timezone

import factory
from faker import Faker
from datetime import datetime
from tracker.models import Category, Transaction, User

fake = Faker()


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
        django_get_or_create = ('username',)

    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    username = factory.Sequence(lambda n: 'user%d' % n)


class CategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Category
        django_get_or_create = ('name',)

    name = factory.Iterator(
        ['Bills', 'Housing', 'Salary', 'Food', 'Social']
    )


class TransactionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Transaction

    user = factory.SubFactory(UserFactory)
    category = factory.SubFactory(CategoryFactory)
    amount = factory.LazyFunction(lambda: Decimal(random.uniform(1, 3000)).quantize(Decimal('0.01')))
    date = factory.LazyFunction(
        lambda: timezone.make_aware(fake.date_time_between(
            start_date='-1y', end_date=datetime.now()
        ))
    )
    type = factory.Iterator(
        [
            x[0] for x in Transaction.TRANSACTION_TYPE_CHOICES
        ]
    )
