import pytest
from tracker.models import Transaction


@pytest.mark.django_db
def test_queryset_get_income_method(transactions):
    qs = Transaction.objects.get_income()
    assert qs.count() > 0
    assert all(
        [transaction.type == 'income' for transaction in qs]
    )


@pytest.mark.django_db
def test_queryset_get_expenses_method(transactions):
    qs = Transaction.objects.get_expenses()
    assert qs.count() > 0
    assert all(
        [transaction.type == 'expense' for transaction in qs]
    )


@pytest.mark.django_db
def test_queryset_get_total_income_method(transactions):
    qs = Transaction.objects.get_total_income()
    assert qs == sum(transaction.amount for transaction in transactions if transaction.type == 'income')


@pytest.mark.django_db
def test_queryset_get_total_expenses_method(transactions):
    qs = Transaction.objects.get_total_expenses()
    assert qs == sum(transaction.amount for transaction in transactions if transaction.type == 'expense')
