from django.urls import path
from .views import (
    IndexView,
    TransactionsListView,
    TransactionCreateView,
    TransactionUpdateView,
    TransactionDeleteView,
    TransactionsGetView,
    TransactionChartsView,
    TransactionExportView,
    TransactionImportView
)

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('transactions/', TransactionsListView.as_view(), name='transactions-list'),
    path('transactions/charts/', TransactionChartsView.as_view(), name='transactions-charts'),
    path('transactions/create/', TransactionCreateView.as_view(), name='create-transaction'),
    path('transactions/<int:pk>/update/', TransactionUpdateView.as_view(), name='update-transaction'),
    path('transactions/<int:pk>/delete/', TransactionDeleteView.as_view(), name='delete-transaction'),

    path('get-transactions/', TransactionsGetView.as_view(), name='get-transactions'),

    path('transactions/export/', TransactionExportView.as_view(), name='export'),
    path('transactions/import/', TransactionImportView.as_view(), name='import'),

]
