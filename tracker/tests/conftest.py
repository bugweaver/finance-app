import random
from datetime import timedelta

import pytest
from django.utils import timezone

from tracker.factories import TransactionFactory, UserFactory


@pytest.fixture
def transactions():
    return TransactionFactory.create_batch(20)

@pytest.fixture
def user_transactions():
    user = UserFactory()
    now = timezone.now()
    transactions = []
    for i in range(20):
        transaction_date = now - timedelta(days=random.randint(0, 4))  # Dates within the last 5 days
        transactions.append(TransactionFactory.create(user=user, date=transaction_date))
    return transactions

@pytest.fixture
def user():
    return UserFactory()

@pytest.fixture
def transaction_dict_params(user):
    transaction = TransactionFactory.create(user=user)
    return {
        'type': transaction.type,
        'category': transaction.category_id,
        'date': transaction.date,
        'amount': transaction.amount,
    }