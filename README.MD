1) From github 

- pip install -r requirements.txt
- cd /sweets
if you want to run server
- python3 manage.py runserver 0.0.0.0:8000 
 <br>or
-  docker-compose up 

Dockerhub:
**https://hub.docker.com/repository/docker/vikusha007/4term_isp34/general

if you want to run tests
- coverage run --source='.' manage.py test front posts

- coverage report




2) Description
- python REST API service , that allows hire couriers, get orders, and distribute orders between them,calculate their salary and rating , added frontend

3) Notes

- to add order sign-in as admin (create first) 

© designed with love by VictoriaSviridchik
