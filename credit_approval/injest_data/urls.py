from django.urls import path
from injest_data.views import upload_data_view, register_customer, check_eligibilty, create_loan, view_loan_details, view_details

urlpatterns = [
    path('injest/', upload_data_view),
    path('register/', register_customer),
    path('check-eligibilty', check_eligibilty),
    path('create-loan', create_loan),
    path('view-loans/<int:customer_id>', view_loan_details),
    path('view-details/<int:loan_id>', view_details)
]
