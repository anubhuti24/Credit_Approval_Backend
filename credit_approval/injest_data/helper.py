from .models import Loan
from django.db.models import Sum, Avg
from django.utils import timezone


def check_loan_eligibitly(customer, interest_rate):
    past_loans = Loan.objects.filter(customer=customer)

    average_tenure = past_loans.aggregate(Avg('tenure'))['tenure__avg']

    past_loans_paid_on_time = sum(loan.emis_paid_on_time / average_tenure for loan in past_loans) / len(
        past_loans) if past_loans else 0

    loan_activity_current_year = 0.2 * (timezone.now().year == timezone.now().year)

    loan_amount_sum = Loan.objects.filter(customer=customer).aggregate(Sum('loan_amount'))['loan_amount__sum']
    approved_limit = float(customer.approved_limit)

    scaled_sum_of_loans = 0.2 * min(float(loan_amount_sum) / approved_limit, 1) if loan_amount_sum is not None else 0

    loan_amount_sum = past_loans.aggregate(Sum('loan_amount'))['loan_amount__sum']
    monthly_salary = float(customer.monthly_salary)

    scaled_sum_comparison = (
            0.2 * min(float(loan_amount_sum) / float(monthly_salary), 1)
    ) if loan_amount_sum is not None else 0

    credit_score = (
                           0.2 * min(past_loans_paid_on_time, 1) +
                           0.2 * max((past_loans.count() - 1) / 5, 0) +
                           loan_activity_current_year +
                           scaled_sum_of_loans +
                           scaled_sum_comparison
                   ) * 100

    if credit_score > 50:
        loan_approved = True
    elif 50 > credit_score > 30 and interest_rate > 12:
        loan_approved = True
    elif 30 > credit_score > 10 and interest_rate > 16:
        loan_approved = True
    else:
        loan_approved = False

    sum_of_current_emis = \
        Loan.objects.filter(customer=customer).aggregate(Sum('monthly_payment'))[
            'monthly_payment__sum']

    if sum_of_current_emis is not None and sum_of_current_emis > 0.5 * float(customer.monthly_salary):
        loan_approved = False

    return loan_approved


def calculate_monthly_installments(interest_rate, tenure, loan_amount):
    monthly_interest_rate = float(interest_rate) / (12 * 100)
    number_of_payments = tenure
    monthly_installment = (
                                  float(loan_amount) * float(monthly_interest_rate) * (
                                  1 + float(monthly_interest_rate)) ** int(number_of_payments)
                          ) / ((1 + float(monthly_interest_rate)) ** int(number_of_payments) - 1)

    return monthly_installment
