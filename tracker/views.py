from django.shortcuts import render, get_object_or_404
from django.views.generic import View, ListView, TemplateView, UpdateView, DeleteView
from django.core.paginator import Paginator
from django.conf import settings
from .models import Transaction
from .filters import TransactionFilter
from .forms import TransactionForm
from django_htmx.http import retarget
from .charting import plot_income_expenses_bar_chart, plot_category_pie_chart
from .resources import TransactionResource
from django.http import HttpResponse, Http404
from tablib import Dataset


class HtmxOnlyMixin:
    def dispatch(self, request, *args, **kwargs):
        if not request.headers.get('HX-Request'):
            raise Http404("This view is only for HTMX requests.")
        return super().dispatch(request, *args, **kwargs)

class IndexView(TemplateView):
    template_name = 'index.html'


class TransactionsListView(View):
    def get(self, request):
        transaction_filter = TransactionFilter(
            request.GET,
            queryset=Transaction.objects.filter(user=request.user).select_related('category')
        )
        paginator = Paginator(transaction_filter.qs, settings.PAGE_SIZE)
        transaction_page = paginator.page(1)

        total_income = transaction_filter.qs.get_total_income()
        total_expenses = transaction_filter.qs.get_total_expenses()

        context = {
            'transactions': transaction_page,
            'filter': transaction_filter,
            'total_income': total_income,
            'total_expenses': total_expenses,
            'net_income': total_income - total_expenses,
        }

        if request.htmx:
            return render(request, 'partials/transactions-container.html', context)
        return render(request, 'transactions-list.html', context)


class TransactionsGetView(HtmxOnlyMixin, View):
    def get(self, request):
        page = request.GET.get('page', 1)

        transaction_filter = TransactionFilter(
            request.GET,
            queryset=Transaction.objects.filter(user=request.user).select_related('category')
        )
        paginator = Paginator(transaction_filter.qs, settings.PAGE_SIZE)
        context = {
            'transactions': paginator.page(page)
        }
        return render(request, 'partials/transactions-container.html#transaction_list', context)


class TransactionCreateView(HtmxOnlyMixin, View):
    def get(self, request):
        context = {'form': TransactionForm()}
        return render(request, 'partials/create-transaction.html', context)

    def post(self, request):
        form = TransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.user = request.user
            transaction.save()
            context = {'message': "Transaction was added successfully!"}
            return render(request, 'partials/transaction-success.html', context)
        else:
            context = {'form': form}
            response = render(request, 'partials/create-transaction.html', context)
            return retarget(response, '#form-modal')


class TransactionUpdateView(HtmxOnlyMixin, UpdateView):
    model = Transaction
    form_class = TransactionForm
    template_name = 'partials/update-transaction.html'
    success_template_name = 'partials/transaction-success.html'
    context_object_name = 'transaction'

    def get_object(self, queryset=None):
        return get_object_or_404(Transaction, pk=self.kwargs['pk'], user=self.request.user)

    def form_valid(self, form):
        form.save()
        context = {'message': "Transaction was updated successfully!"}
        return render(self.request, self.success_template_name, context)

    def form_invalid(self, form):
        context = {
            'form': form,
            'transaction': self.get_object(),
        }
        response = render(self.request, self.template_name, context)
        return retarget(response, '#form-modal')


class TransactionDeleteView(HtmxOnlyMixin, DeleteView):
    model = Transaction
    success_template_name = 'partials/transaction-success.html'

    def delete(self, request, *args, **kwargs):
        transaction = self.get_object()
        transaction.delete()
        context = {
            'message': f"Transaction of {transaction.amount} on {transaction.date.date()} was deleted successfully!"}
        return render(request, self.success_template_name, context)


class TransactionChartsView(View):
    def get(self, request):
        transaction_filter = TransactionFilter(
            request.GET,
            queryset=Transaction.objects.filter(user=request.user).select_related('category')
        )
        income_expense_bar = plot_income_expenses_bar_chart(transaction_filter.qs)

        category_income_pie = plot_category_pie_chart(
            transaction_filter.qs.filter(type='income')
        )
        category_expense_pie = plot_category_pie_chart(
            transaction_filter.qs.filter(type='expense')
        )
        context = {
            'filter': transaction_filter,
            'income_expense_barchart': income_expense_bar.to_html(),
            'category_income_pie': category_income_pie.to_html(),
            'category_expense_pie': category_expense_pie.to_html(),
        }
        if request.htmx:
            return render(request, 'partials/charts-container.html', context)
        return render(request, 'charts.html', context)


class TransactionExportView(View):
    def get(self, request):

        if request.htmx:
            return HttpResponse(headers={'HX-Redirect': request.get_full_path()})


        transaction_filter = TransactionFilter(
            request.GET,
            queryset=Transaction.objects.filter(user=request.user).select_related('category')
        )
        data = TransactionResource().export(transaction_filter.qs)
        response = HttpResponse(data.csv)
        response['Content-Disposition'] = 'attachment; filename="transactions.csv"'

        return response


# class TransactionImportView(View):
#     def post(self, request):
#         file = request.FILES.get('file')
#         resource = TransactionResource
#         dataset = Dataset()
#         dataset.load(file.read().decode(), format='csv')
#         result = resource.import_data(dataset, user=request.user, dry_run=True)
#
#         if not result.has_errors():
#             resource.import_data(dataset, user=request.user, dry_run=False)
#             context = {'message': f'{len(dataset)} transactions were uploaded successfully'}
#         else:
#             context = {'message': 'Sorry, an error occurred'}
#
#         return render(request, 'partials/transaction-success.html', context=context)
#
#     def get(self, request):
#         return render(request, 'partials/import-transaction.html')

class TransactionImportView(HtmxOnlyMixin, View):
    def post(self, request):
        file = request.FILES.get('file')
        if not file:
            context = {'message': 'No file was uploaded'}
            return render(request, 'partials/transaction-success.html', context=context)

        resource = TransactionResource()
        dataset = Dataset()

        try:
            dataset.load(file.read().decode(), format='csv')
        except Exception as e:
            context = {'message': f'Error loading file: {str(e)}'}
            return render(request, 'partials/transaction-success.html', context=context)

        result = resource.import_data(dataset, user=request.user, dry_run=True)

        if not result.has_errors():
            resource.import_data(dataset, user=request.user, dry_run=False)
            context = {'message': f'{len(dataset)} transactions were uploaded successfully'}
        else:
            context = {'message': 'Some errors occurred during import. Please check the file and try again.'}
        return render(request, 'partials/transaction-success.html', context=context)

    def get(self, request):
        return render(request, 'partials/import-transaction.html')