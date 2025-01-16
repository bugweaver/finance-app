from datetime import datetime
import random
from faker import Faker
from django.core.management.base import BaseCommand
from tracker.models import User, Transaction, Category


class Command(BaseCommand):
    help = "Generates transactions for testing"

    def handle(self, *args, **options):
        fake = Faker()

        categories = [
            'Bills',
            'Food',
            'Clothes',
            'Medical',
            'Housing',
            'Salary',
            'Social',
            'Transport',
            'Vacation'
        ]
        print("Creating categories:\n")
        for category in categories:
            Category.objects.get_or_create(name=category)
            print(category)

        user = User.objects.filter(username='admin').first()
        if not user:
            user = User.objects.create_superuser(username='admin', password='admin@11')

        categories = Category.objects.all()
        types = [x[0] for x in Transaction.TRANSACTION_TYPE_CHOICES]
        for i in range(20):
            transaction = Transaction.objects.create(
                category=random.choice(categories),
                user=user,
                amount=random.uniform(1, 3000),
                date=fake.date_time_between(start_date='-1y', end_date=datetime.now()),
                type=random.choice(types)
            )
            print(
                "Transaction\n",
                transaction.category,
                transaction.amount,
                transaction.date
            )
