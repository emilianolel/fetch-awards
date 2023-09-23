# DAG

import boto3
import json
from hashlib import sha256
import psycopg2
import pendulum


from airflow.decorators import dag, task

@dag(
    schedule=None,
    start_date=pendulum.datetime(2021, 1, 1, tz="UTC"),
    catchup=False,
    tags=["fetch-rewards"],
)

def sqa_pipeline_dag():

    # define hash + salt function
    # meanwhile salt do not change, function output will be the same.

    def hashFunction(string):
        _salt = 'hello'
        return sha256((string + _salt).encode('utf-8')).hexdigest()


    # define query string function

    def insertIntoQuery(dictionary):
        TABLE = 'user_logins'
        return f'''INSERT INTO {TABLE} (user_id, device_type, masked_ip, masked_device_id, locale, app_version, create_date)
        VALUES (CAST('{dictionary['user_id']}' AS VARCHAR(128)), CAST('{dictionary['device_type']}' AS VARCHAR(32)), CAST('{dictionary['masked_ip']}' AS VARCHAR(256)), CAST('{dictionary['masked_device_id']}' AS VARCHAR(256)), CAST('{dictionary['locale']}' AS VARCHAR(256)), CAST('{dictionary['app_version']}' AS INT), CURRENT_DATE);'''
    

    # Establishing the connection
    conn = psycopg2.connect(
            database='postgres',
            user='postgres',
            password='postgres',
            host='localhost',
            port='5432')

    # Setting auto commit false
    conn.autocommit = True

    # Creating a cursor object using the cursor() method
    cursor = conn.cursor()


    # starting boto3 Session

    session = boto3.Session()

    sqs = session.client('sqs',
            endpoint_url='http://localhost:4566/000000000000/login-queue',
            region_name='us-east-1',
            aws_secret_access_key='x',
            aws_access_key_id='x',
            use_ssl=False)
    

    @task()
    def get_json_sqs():

        print("extracting data task started......")

        response = sqs.receive_message(QueueUrl='http://localhost:4566/000000000000/login-queue')
        
        # extract messages from sqs queue
        message = response['Messages']

        print("extracting data task finished..........")

        return message
    

    @task()
    def transform_login_data(message):

        print("transforming data task started..........")

        login_information = json.loads(message['Body'])

        # extract login information.
        extracted_login_info_dict = {
            "user_id": login_information["user_id"],
            "device_type": login_information["device_type"],
            "masked_ip": hashFunction(login_information["ip"]),
            "masked_device_id": hashFunction(login_information["device_id"]),
            "locale": login_information["locale"],
            "app_version": login_information["app_version"].replace('.', '')
        }

        print ("transforming data task finished..........")

        return extracted_login_info_dict
    
    @task()
    def load_login_data_postgres(extracted_login_info_dict):

        print("load task started.......")

        cursor.execute(insertIntoQuery(extracted_login_info_dict))

        conn.commit()
        print("Record inserted........")

        conn.close()
        print("Connection closed........")

        print("load task finished.........")
    

    extract = get_json_sqs()

    transform = transform_login_data(extract)

    load = load_login_data_postgres(transform)


sqa_pipeline_dag()
