from django.test import TestCase
from rest_framework.test import APIClient
from .models import Customer, Loan
from datetime import date

# Unit test URLs
REGISTER_CUSTOMER_URL = 'http://127.0.0.1:8000/api/register/'
CHECK_ELIGIBILITY_URL = 'http://127.0.0.1:8000/api/check-eligibilty'
CREATE_LOAN_URL = 'http://127.0.0.1:8000/api/create-loan'
VIEW_LOAN_DETAILS_URL = 'http://127.0.0.1:8000/api/view-loans/1'
VIEW_DETAILS_URL = 'http://127.0.0.1:8000/api/view-details/123'


class RegisterCustomerTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_register_customer(self):
        url = REGISTER_CUSTOMER_URL

        data = {
            'first_name': 'Kate',
            'last_name': 'Willey',
            'age': 30,
            'monthly_salary': 5000,
            'phone_number': '9234567890'
        }

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, 201)

        self.assertIn('Customer id', response.data)
        self.assertIn('Name', response.data)
        self.assertIn('Age', response.data)

        self.assertTrue(Customer.objects.filter(first_name='Kate').exists())


class CheckEligibilityTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        # Assuming a customer exists in the database with an ID of 1
        Customer.objects.create(
            customer_id=1,
            first_name="XYZ",
            last_name="ABC",
            age=21,
            monthly_salary=20000,
            phone_number=9876567677,
            approved_limit=21000
        )

    def test_check_eligibility(self):
        url = CHECK_ELIGIBILITY_URL

        data = {
            'customer_id': 1,
            'loan_amount': 10000,
            'interest_rate': 12,
            'tenure': 12
        }

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, 201)
        self.assertIn('customer_id', response.data)
        self.assertIn('approval', response.data)
        self.assertIn('interest_rate', response.data)
        self.assertIn('corrected_interest_rate', response.data)
        self.assertIn('tenure', response.data)
        self.assertIn('monthly_installment', response.data)


class CreateLoanTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        # Assuming a customer exists in the database with an ID of 1
        Customer.objects.create(
            customer_id=1,
            first_name="XYZ",
            last_name="ABC",
            age=21,
            monthly_salary=20000,
            phone_number=9876567677,
            approved_limit=21000
        )

    def test_create_loan(self):
        url = CREATE_LOAN_URL

        data = {
            'customer_id': 1,
            'loan_amount': 20000,
            'interest_rate': 10,
            'tenure': 12
        }

        response = self.client.post(url, data)
        print(response.content)

        self.assertEqual(response.status_code, 200)
        self.assertIn('loan_id', response.data)
        self.assertIn('customer_id', response.data)
        self.assertIn('loan_approved', response.data)
        self.assertIn('message', response.data)
        self.assertIn('monthly_installment', response.data)


class ViewLoanDetailsTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        # Assuming a customer exists in the database with an ID of 1
        customer = Customer.objects.create(
            customer_id=1,
            first_name="XYZ",
            last_name="ABC",
            age=21,
            monthly_salary=20000,
            phone_number=9876567677,
            approved_limit=21000
        )
        # Assuming a loan exists for the customer
        Loan.objects.create(
            customer=customer,
            loan_id=123,
            loan_amount=5000,
            interest_rate=5,
            monthly_payment=1000,
            tenure=5,
            emis_paid_on_time=3,
            start_date=date.today(),
            end_date=date.today()
        )

    def test_view_loan_details(self):
        url = VIEW_LOAN_DETAILS_URL

        response = self.client.get(url)
        print(response.content)

        self.assertEqual(response.status_code, 200)
        self.assertTrue('loan_id' in response.data[0])
        self.assertTrue('loan_amount' in response.data[0])
        self.assertTrue('interest_rate' in response.data[0])
        self.assertTrue('monthly_installment' in response.data[0])
        self.assertTrue('repayments_left' in response.data[0])


class ViewDetailsTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        # Assuming a customer exists in the database with an ID of 1
        customer = Customer.objects.create(
            customer_id=1,
            first_name="XYZ",
            last_name="ABC",
            age=21,
            monthly_salary=20000,
            phone_number=9876567677,
            approved_limit=21000
        )
        Loan.objects.create(
            customer=customer,
            loan_id=123,
            loan_amount=5000,
            interest_rate=5,
            monthly_payment=1000,
            tenure=5,
            emis_paid_on_time=3,
            start_date=date.today(),
            end_date=date.today()
        )

    def test_view_details(self):
        url = VIEW_DETAILS_URL

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTrue('loan_id' in response.data)
        self.assertTrue('customer' in response.data)
        self.assertTrue('loan_amount' in response.data)
        self.assertTrue('interest_rate' in response.data)
        self.assertTrue('monthly_installment' in response.data)
        self.assertTrue('tenure' in response.data)
