'''
This code reads data from an AWS SQS (Simple Queue Service) queue, hashes IP addresses and device IDs, and then inserts user login information into a PostgreSQL database table.

The code performs the following steps:

1. Establishes a connection to a PostgreSQL database.
2. Configures a Boto3 client to interact with AWS SQS.
3. Receives messages from the specified SQS queue.
4. Extracts login information from the received messages.
5. Hashes the IP address and device ID for privacy reasons.
6. Constructs an SQL query for inserting the extracted login information into a PostgreSQL table.
7. Executes the SQL query for each extracted login entry.
8. Commits the changes to the PostgreSQL database.
9. Closes the database connection.

Note:
- The hashing function used for IP addresses and device IDs adds a fixed salt ('hello') to the input string and computes a SHA-256 hash.
- The login information is extracted from JSON messages received from the SQS queue.
- The extracted data is inserted into a PostgreSQL table named 'user_logins'.

To use this code, ensure you have the required AWS credentials and PostgreSQL database configured appropriately.

Author: José Emiliano Herrera Velázquez
Date: 2023-09-19
'''

import boto3
import json
from hashlib import sha256
import psycopg2



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

print('Looking for queues...')

response = sqs.receive_message(QueueUrl='http://localhost:4566/000000000000/login-queue')

# extract messages from sqs queue
messages = response['Messages']

for message in messages:
    
    login_information = json.loads(message['Body'])
    
    print(login_information)

    # extract login information.
    extracted_login_info_dict = {
        "user_id": login_information["user_id"],
        "device_type": login_information["device_type"],
        "masked_ip": hashFunction(login_information["ip"]),
        "masked_device_id": hashFunction(login_information["device_id"]),
        "locale": login_information["locale"],
        "app_version": login_information["app_version"].replace('.', '')
    }

    cursor.execute(insertIntoQuery(extracted_login_info_dict))


# Commit your changes in the database

conn.commit()
print("Records inserted........")

# Closing the connection
conn.close()
