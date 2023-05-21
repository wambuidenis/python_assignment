### Documentation
#### About 
This is a small app that will use the [AlphaVantage](https://www.alphavantage.co/documentation/)  as a data provider for 
API calls for financial symbols. The app parses, transforms and stores the data in a database. 

Docker is the containerization platform of choice; two services (app and the database). 
The database uses two tables:
- symbols 
- financial_data

`financial_data` keep a reference to symbol via a foreign key
futher the app aim to for integrity through to schema defination and 
code 

#### Tech stack 
The app is built using [flask]() to create a server and related
applications routing, processing and validations;

[MySQL]() is the database of choice. 

#### Installation 
The applications requires the following software 
1. Docker 
2. Python

##### 1. Locally 
To run the code run locally the following commands 
````shell 
docker-compose up  
````
Setting the application and adding the data 
```shell
docker ps  
```
get the `containter id` for the containter `ython_assignment-app` 
```shell
docker exec -it `containter_id` /bin/bash
```
pupulate the database tables by executing `get_raw_data.py`
```shell 
python get_raw_data.py

# output expected

2023-05-21 05:07:42,014 - INFO - record added successfully
2023-05-21 05:07:42,036 - INFO - record added successfully
2023-05-21 05:07:42,093 - INFO - record added successfully
... 
```
Fectching data 
```shell 
curl -X GET 'http://localhost:5000/api/financial_data?start_date=2023-01-01&end_date=2023-05-31&symbol=IBM&limit=3&page=2'
```
```shell 
curl -X GET http://localhost:5000/api/statistics?start_date=2023-01-01&end_date=2023-12-31&symbol=IBM
```
##### 2. Production 
The application changes that would be made in a production enviroment would 
1. Running the application with a load balancer (app and db) 
2. Adding anti-bot measure avoid denial of access and abuse 
3. Request throttling per endpoint per IP 
4. Running the applicatioin using gunicurn or similar 
5. Adding `RUN ["python","get_raw_data.py"]` for the docker file to ensure the database is populated automatically rather than manually 
6. Storing the secrets to a vault for easier rotation and revokation rather than enviroment variables


Running the code
 ```shell 
 docker-compose up 
 ```
