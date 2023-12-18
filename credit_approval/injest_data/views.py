from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.conf import settings
from .tasks import process_customer_data
from .models import Customer, Loan
from datetime import date, timedelta
from .helper import check_loan_eligibitly, calculate_monthly_installments
import random


@api_view(['GET'])
def upload_data_view(request):
    customer_file_path = settings.CUSTOMER_DATA_PATH
    loan_file_path = settings.LOAN_DATA_PATH

    process_customer_data.delay(customer_file_path, loan_file_path)

    return Response("Data injested successfully.", status=status.HTTP_200_OK)


@api_view(['POST'])
def register_customer(request):
    data = request.data
    required_fields = ['first_name', 'last_name', 'age', 'monthly_salary', 'phone_number']

    if not all(field in data for field in required_fields):
        return Response({'error': 'Missing required fields'}, status=status.HTTP_400_BAD_REQUEST)

    first_name = data['first_name']
    last_name = data['last_name']
    age = data['age']

    id = Customer.objects.count() + 1

    try:
        monthly_salary = float(data['monthly_salary'])
    except ValueError:
        return Response({'error': 'Invalid monthly_income value'}, status=status.HTTP_400_BAD_REQUEST)

    phone_number = data['phone_number']

    approved_limit = round(36 * monthly_salary, -5)

    Customer.objects.create(
        customer_id=id,
        first_name=first_name,
        last_name=last_name,
        age=age,
        monthly_salary=monthly_salary,
        phone_number=phone_number,
        approved_limit=approved_limit
    )

    return Response({
        'Customer id': id,
        'Name': first_name + " " + last_name,
        'Age': age,
        'Monthly income': monthly_salary,
        'Approved limit': approved_limit,
        'Phone number': phone_number
    }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
def check_eligibilty(request):
    customer_id = request.data['customer_id']
    loan_amount = request.data['loan_amount']
    interest_rate = float(request.data['interest_rate'])
    tenure = float(request.data['tenure'])

    try:
        customer = Customer.objects.get(customer_id=customer_id)
    except Customer.DoesNotExist:
        return Response({'error': 'Customer not exists'}, status=status.HTTP_400_BAD_REQUEST)

    loan_approved = check_loan_eligibitly(customer, interest_rate)

    approved_limit = float(customer.approved_limit)

    if float(interest_rate) > 0.5 * approved_limit:
        corrected_interest_rate = min(float(interest_rate), 16)
    else:
        corrected_interest_rate = None

    monthly_installment = calculate_monthly_installments(interest_rate, tenure, loan_amount)

    response_data = {
        'customer_id': customer_id,
        'approval': loan_approved,
        'interest_rate': interest_rate,
        'corrected_interest_rate': corrected_interest_rate,
        'tenure': tenure,
        'monthly_installment': monthly_installment,
    }

    return Response(response_data, status=status.HTTP_201_CREATED)


@api_view(['POST'])
def create_loan(request):
    customer_id = request.data['customer_id']
    loan_amount = request.data['loan_amount']
    interest_rate = request.data['interest_rate']
    tenure = request.data['tenure']

    try:
        customer = Customer.objects.get(customer_id=customer_id)
    except Customer.DoesNotExist:
        return Response({'error': 'Customer not exists'}, status=status.HTTP_400_BAD_REQUEST)

    if customer_id is not None and loan_amount is not None and interest_rate is not None and tenure is not None:

        eligible_for_loan = check_loan_eligibitly(customer, interest_rate)
        monthly_installment = calculate_monthly_installments(interest_rate, tenure, loan_amount)

        if eligible_for_loan:
            loan_approved = True
            message = "Loan approved"
            monthly_installment = monthly_installment
            start_date = date.today()
            end_date = start_date + timedelta(days=30 * float(tenure))

            approved_loan = Loan.objects.create(
                customer=customer,
                loan_id=random.randint(1000, 9999),
                loan_amount=loan_amount,
                tenure=tenure,
                interest_rate=interest_rate,
                monthly_payment=monthly_installment,
                emis_paid_on_time=0,
                start_date=start_date,
                end_date=end_date,
            )

            response_data = {
                'loan_id': approved_loan.loan_id,
                'customer_id': customer_id,
                'loan_approved': loan_approved,
                'message': message,
                'monthly_installment': monthly_installment,
            }
            return Response(response_data, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Loan not approved'}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({'error': 'Incomplete data provided'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def view_loan_details(request, customer_id):
    try:
        customer = Customer.objects.get(customer_id=customer_id)
    except Customer.DoesNotExist:
        return Response({'error': 'Customer not exists'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        current_loans = Loan.objects.filter(customer=customer)

        response_data = []
        for loan in current_loans:
            loan_item = {
                'loan_id': loan.loan_id,
                'loan_amount': loan.loan_amount,
                'interest_rate': loan.interest_rate,
                'monthly_installment': loan.monthly_payment,
                'repayments_left': loan.tenure - loan.emis_paid_on_time,
            }
            response_data.append(loan_item)

        return Response(response_data, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def view_details(request, loan_id, ):
    try:
        loan = Loan.objects.get(loan_id=loan_id)

        customer = loan.customer

        response_data = {
            'loan_id': loan.loan_id,
            'customer': {
                'id': customer.customer_id,
                'first_name': customer.first_name,
                'last_name': customer.last_name,
                'phone_number': customer.phone_number,
                'age': customer.age,
            },
            'loan_amount': loan.loan_amount,
            'interest_rate': loan.interest_rate,
            'monthly_installment': loan.monthly_payment,
            'tenure': loan.tenure,
        }

        return Response(response_data, status=status.HTTP_200_OK)

    except Loan.DoesNotExist:
        return Response({"message": "Loan not found"}, status=status.HTTP_404_NOT_FOUND)
    except Customer.DoesNotExist:
        return Response({"message": "Customer not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
