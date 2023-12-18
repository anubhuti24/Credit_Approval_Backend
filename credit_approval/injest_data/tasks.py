import pandas as pd
from celery import Celery
from .models import Customer, Loan
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings

app = Celery('tasks', broker=settings.CELERY_RESULT_BACKEND)


@app.task
def process_customer_data(customer_file_path, loan_file_path):
    customer_data = pd.read_excel(customer_file_path)

    for index, row in customer_data.iterrows():
        print("AGE:", row['Age'])
        Customer.objects.create(
            customer_id=row['Customer ID'],
            first_name=row['First Name'],
            last_name=row['Last Name'],
            age=row['Age'],
            phone_number=row['Phone Number'],
            monthly_salary=row['Monthly Salary'],
            approved_limit=row['Approved Limit'],
        )
        
    process_loan_data.delay(loan_file_path)


@app.task
def process_loan_data(loan_file_path):
    loan_data = pd.read_excel(loan_file_path)

    for index, row in loan_data.iterrows():
        customer_id = row['Customer ID']
        print(customer_id)

        try:
            customer = Customer.objects.filter(customer_id=customer_id).first()

        except ObjectDoesNotExist:
            continue

        Loan.objects.create(
            customer=customer,
            loan_id=row['Loan ID'],
            loan_amount=row['Loan Amount'],
            tenure=row['Tenure'],
            interest_rate=row['Interest Rate'],
            monthly_payment=row['Monthly payment'],
            emis_paid_on_time=row['EMIs paid on Time'],
            start_date=row['Date of Approval'],
            end_date=row['End Date']
        )
