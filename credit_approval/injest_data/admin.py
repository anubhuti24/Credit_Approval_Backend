from django.contrib import admin
from .models import Customer, Loan


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = (
    'customer_id', 'first_name', 'last_name', 'phone_number', 'monthly_salary', 'approved_limit')


@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = (
    'loan_id', 'customer', 'loan_amount', 'tenure', 'interest_rate', 'monthly_payment', 'emis_paid_on_time',
    'start_date', 'end_date')
