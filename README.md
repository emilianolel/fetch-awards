# Data Engineering Take-Home Project: Fetch Awards

This project demonstrates a data engineering solution that reads data from an AWS SQS queue, hashes certain fields, and inserts the data into a PostgreSQL database. It uses Docker Compose to set up the required services: LocalStack for AWS SQS emulation and a PostgreSQL database.

## Prerequisites

Before you begin, make sure you have the following prerequisites installed on your system:

- [Docker](https://www.docker.com/get-started)
- [Docker Compose](https://docs.docker.com/compose/install/)

## Getting Started

1. Clone this repository to your local machine:

   ```bash
   git clone https://github.com/emilianolel/fetch-awards.git
   ```

2. Change into the project directory:

   ```bash
   cd fetch-awards
   ```

3. Move on to the `app/` directory and start de project using Docker Compose:

   ```bash
   docker-compose up -d
   ```

This command will spin up two services: LocalStack and PostgreSQL, exposing ports 4566 and 5432 for AWS SQS and PostgreSQL, respectively.

4. Wait for the services to start. You can check the status with:

   ```bash
   docker-compose ps
   ```

Both services should show a status of "Up."

## Running the Project Code

1. Ensure that the LocalStack and PostgreSQL services are up and running by checking their status with docker-compose ps.

2. Open a new terminal window and navigate to the project directory.

3. Run the data engineering code by executing the Python script:

   ```bash
   python fetch-awards.py
   ```

This script reads data from the AWS SQS queue (emulated by LocalStack), hashes certain fields, and inserts the data into the PostgreSQL database.

4. Monitor the script's output to see the progress and confirm that data is being processed and inserted into the database.

## Cleaning Up
To stop and remove the Docker containers and associated resources, run:

   ```bash
   docker-compose down
   ```

This will stop the LocalStack and PostgreSQL containers and remove them. 

Note that this will also remove any data stored in the PostgreSQL database.

# Question Section

### ● How will you read messages from the queue?

   With use of `boto3` library. 

   1. Configured a Boto3 client to interact with AWS SQS.
   2. Then received messages from the specified SQS queue using the `recive_message` boto3 client method.

### ● What type of data structures should be used?

   In order to read the data sqs messages, it was used a dictionary.

   ```python
   extracted_login_info_dict = {
        "user_id": login_information["user_id"],
        "device_type": login_information["device_type"],
        "masked_ip": hashFunction(login_information["ip"]),
        "masked_device_id": hashFunction(login_information["device_id"]),
        "locale": login_information["locale"],
        "app_version": login_information["app_version"].replace('.', '')
    }
   ```

### ● How will you mask the PII data so that duplicate values can be identified?

   Defined a function that uses the sha256 algorithm to the ip and device values.

   ```python
   def hashFunction(string):
      _salt = 'hello'
      return sha256((string + _salt).encode('utf-8')).hexdigest()
   ```

### ● What will be your strategy for connecting and writing to Postgres?

   With use of `import psycopg2` library.

   1. Established a connection to the PostgreSQL database.
   
   2. Execute the `INSERT` query
      ```sql
      ''INSERT INTO {TABLE} (user_id, device_type, masked_ip, masked_device_id, locale, app_version, create_date) VALUES (CAST('{dictionary['user_id']}' AS VARCHAR(128)), CAST('{dictionary['device_type']}' AS VARCHAR(32)), CAST('{dictionary['masked_ip']}' AS VARCHAR(256)), CAST('{dictionary['masked_device_id']}' AS VARCHAR(256)), CAST('{dictionary['locale']}' AS VARCHAR(256)), CAST('{dictionary['app_version']}' AS INT), CURRENT_DATE);'''
      ```

### ● Where and how will your application run?
   
   The application will run in a machine with Docker and Docker Compose.

### ● How would you deploy this application in production?

   - Automate execution process. Using airflow could be a great fit.

   - Add tests to the code, in order to garantee the data reliability.

   - Create a modular code, in order to mantain atomic jobs.

### ● What other components would you want to add to make this production ready?

   - Airflow is a must be.

### ● How can this application scale with a growing dataset.

   - Use Apache Spark Streaming library to read real-time sqs queue and process its data.

   - Move on to HDFS in order to store procesed data in a more efficient way and also better to query on `user_logins` table. Using Parquet and partitioned into `device_type` and `create_date`.

### ● How can PII be recovered later on?

   - Using another algorithm like a pgp encription protocol. (private key and public key).

   - Creating two tables which contains `(ip -> masked_ip)` and `(device_id -> masked_device_id)`. But I think it is insecure.

### ● What are the assumptions you made?

   - I asumed the `json` sqs response is the same for all responses.

   - Also I asumed it could be more than one message in the `json` response.

   ```json
   {
      "Messages":[
         {
               "MessageId":"3e36bba9-afd9-4908-a712-b5948dc2561f",
               "ReceiptHandle":"MjA2YTgxYTMtN2Q1NS00NThiLWFlMzItODY5ZmI2NjIxZjVlIGFybjphd3M6c3FzOnVzLWVhc3QtMTowMDAwMDAwMDAwMDA6bG9naW4tcXVldWUgM2UzNmJiYTktYWZkOS00OTA4LWE3MTItYjU5NDhkYzI1NjFmIDE2OTUxMDA1NDIuMjg1MzM0Mw==",
               "MD5OfBody":"e4f1de8c099c0acd7cb05ba9e790ac02",
               "Body":"{\"user_id\": \"424cdd21-063a-43a7-b91b-7ca1a833afae\", \"app_version\": \"2.3.0\", \"device_type\": \"android\", \"ip\": \"199.172.111.135\", \"locale\": \"RU\", \"device_id\": \"593-47-5928\"}"
         }
      ],
      "ResponseMetadata":{
         "RequestId":"2RGYD6NTLTMF3JTUZHABTBH8QPJEXP2PZRDR3V6RTXQ2ZM436WCW",
         "HTTPStatusCode":200,
         "HTTPHeaders":{
               "content-type":"text/xml",
               "content-length":"951",
               "access-control-allow-origin":"*",
               "access-control-allow-methods":"HEAD,GET,PUT,POST,DELETE,OPTIONS,PATCH",
               "access-control-allow-headers":"authorization,cache-control,content-length,content-md5,content-type,etag,location,x-amz-acl,x-amz-content-sha256,x-amz-date,x-amz-request-id,x-amz-security-token,x-amz-tagging,x-amz-target,x-amz-user-agent,x-amz-version-id,x-amzn-requestid,x-localstack-target,amz-sdk-invocation-id,amz-sdk-request",
               "access-control-expose-headers":"etag,x-amz-version-id",
               "connection":"close",
               "date":"Tue, 19 Sep 2023 05:15:42 GMT",
               "server":"hypercorn-h11"
         },
         "RetryAttempts":0
      }
   }
   ```
   
   That is why there is a `for` loop defined.

   ```python
   # extract messages from sqs queue
   messages = response['Messages']

   for message in messages:
      
      login_information = json.loads(message['Body'])
   ```