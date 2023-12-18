# Credit_Approval_Backend

## Run Project 

  ### Locally

  Make migrations to inlcude changes in model:
  
  `python manage.py makemigrations`

  Migrate the changes to database:
  
  `python manage.py migrate`

  Start django in development server:
  
  `python manage.py runserver`

  Start Redis-server:
  
  `sudo systemctl start redis-server`

  Start Celery:
  
  `celery -A credit_approval worker -l info`

  ### Using Docker
  `sudo docker-compose up --build`


## Unit testing

To run unit tests , run the following commands.
All the tests could be found in credit_approval/injest_data/tests.py

`python manage.py test injest_data.tests`



## Test APIs using Postman Collection
- Postman API collection for this project is uploaded in this repository itself.
- Import the json file into Postman and test APIs.

  
