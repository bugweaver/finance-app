import random
from datetime import datetime, timedelta
from django.utils import timezone
import pytest
from django.urls import reverse
from tracker.models import Category, Transaction
from pytest_django.asserts import assertTemplateUsed


@pytest.mark.django_db
def test_total_values_appear_on_list_page(user_transactions, client):
    user = user_transactions[0].user
    client.force_login(user)

    income_total = sum(t.amount for t in user_transactions if t.type == 'income')
    expense_total = sum(t.amount for t in user_transactions if t.type == 'expense')
    net = income_total - expense_total

    response = client.get(reverse('transactions-list'))
    assert response.context['total_income'] == income_total
    assert response.context['total_expenses'] == expense_total
    assert response.context['net_income'] == net


@pytest.mark.django_db
def test_transaction_type_filter(user_transactions, client):
    user = user_transactions[0].user
    client.force_login(user)

    get_params = {'transaction_type': 'income'}
    response = client.get(reverse('transactions-list'), get_params)

    qs = response.context['filter'].qs

    for transaction in qs:
        assert transaction.type == 'income'

    get_params = {'transaction_type': 'expense'}
    response = client.get(reverse('transactions-list'), get_params)

    qs = response.context['filter'].qs

    for transaction in qs:
        assert transaction.type == 'expense'


@pytest.mark.django_db
def test_category_filter(user_transactions, client):
    user = user_transactions[0].user
    client.force_login(user)

    category_pks = Category.objects.all()[:2].values_list('pk', flat=True)

    get_params = {'category': category_pks}
    response = client.get(reverse('transactions-list'), get_params)

    qs = response.context['filter'].qs

    for transaction in qs:
        assert transaction.category.pk in category_pks


@pytest.mark.django_db
def test_start_end_date_filter(user_transactions, client):
    user = user_transactions[0].user
    client.force_login(user)

    end_date_cutoff = timezone.now()
    start_date_cutoff = end_date_cutoff - timedelta(days=5)  # Example: filter last 5 days

    get_params = {
        'start_date': start_date_cutoff.isoformat(),
        'end_date': end_date_cutoff.isoformat()
    }
    response = client.get(reverse('transactions-list'), get_params)

    qs = response.context['filter'].qs
    for transaction in qs:
        assert start_date_cutoff <= transaction.date <= end_date_cutoff


@pytest.mark.django_db
def test_add_transaction_request(user, transaction_dict_params, client):
    client.force_login(user)
    user_transaction_count = Transaction.objects.filter(user=user).count()

    headers = {'HTTP_HX-Request': 'true'}
    response = client.post(
        reverse('create-transaction'),
        transaction_dict_params,
        **headers
    )

    assert Transaction.objects.filter(user=user).count() == user_transaction_count + 1

    assertTemplateUsed(response, 'partials/transaction-success.html')


@pytest.mark.django_db
def test_cannot_add_transaction_with_negative_amount(user, transaction_dict_params, client):
    client.force_login(user)
    user_transaction_count = Transaction.objects.filter(user=user).count()
    transaction_dict_params['amount'] = -44

    headers = {'HTTP_HX-Request': 'true'}
    response = client.post(
        reverse('create-transaction'),
        transaction_dict_params,
        **headers
    )

    assert Transaction.objects.filter(user=user).count() == user_transaction_count

    assertTemplateUsed('partials/create-transaction.html')
    assert 'HX-Retarget' in response.headers


@pytest.mark.django_db
def test_update_transaction_request(user, transaction_dict_params, client):
    client.force_login(user)
    assert Transaction.objects.filter(user=user).count() == 1

    transaction = Transaction.objects.first()

    now = timezone.now()
    transaction_dict_params['amount'] = 40
    transaction_dict_params['date'] = now

    client.post(
        reverse('update-transaction', kwargs={'pk': transaction.pk}),
        transaction_dict_params
    )

    assert Transaction.objects.filter(user=user).count() == 1

    transaction = Transaction.objects.first()
    assert transaction.amount == 40
    assert transaction.date == now


@pytest.mark.django_db
def test_delete_transaction_request(user, transaction_dict_params, client):
    client.force_login(user)
    assert Transaction.objects.filter(user=user).count() == 1
    transaction = Transaction.objects.first()

    client.delete(
        reverse('delete-transaction', kwargs={'pk': transaction.pk})
    )

    assert Transaction.objects.filter(user=user).count() == 0