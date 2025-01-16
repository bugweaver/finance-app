from django.contrib import admin
from django.contrib.auth import get_user_model
from tracker.models import Transaction, Category

User = get_user_model()

class TransactionInline(admin.TabularInline):
    model = Transaction
    extra = 0


class UserAdmin(admin.ModelAdmin):
    inlines = [TransactionInline]


admin.site.register(Transaction)
admin.site.register(Category)
admin.site.register(User, UserAdmin)