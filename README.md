# pinterest-data-pipeline

## Table of contents
- [Project Introduction](#project-introduction)
- [Dependencies](#dependencies)
- [Tools Used](#tools-used)
- [Pinterest Data](#pinterest-data)
- [Pinterest Architecture](#pinterest-architecture)
- [Building a Data Pipeline](#building-a-data-pipeline)
    - [Create Kafka cluster using Amazon MSK](#create-kafka-cluster-using-amazon-msk)
    - [Create a client machine for the MSK cluster](#create-a-client-machine-for-the-msk-cluster)
    - [Configure Kafka client to use AWS IAM](#configure-kafka-client-to-use-aws-iam)
    - [Create a topic on a client machine](#create-a-topic-on-a-client-machine)
    - [Delivering messages to Kafka cluster](#delivering-messages-to-kafka-cluster)
    - [Connect MSK cluster to s3 Bucket](#connect-msk-cluster-to-s3-bucket)
    - [AWS API Gateway](#aws-api-gateway)
    - [Send Data to the API](#send-data-to-the-api)

- [Processing Batch Data on Databricks](#processing-batch-data-on-databricks)

- [Stream Processing: AWS Kinesis]











## Project Introduction
Pinterest crunches billions of data points every day to decide how to provide more value to their users. In this project, I have created a similar system using the AWS Cloud. Here, I have created two separate pipelines, one for computing real-time metrics and other for computing metrics that depend on the historical data. 

## Dependencies
- sqlalchemy
- requests

## Tools Used
- [Apache Kafka](https://kafka.apache.org/): Apache Kafka is a relatively new open-source technology for distributed data storage optimized for ingesting and processing streaming data in real-time

- [Amazon MSK](https://aws.amazon.com/msk/):Amazon Managed Streaming for Apache Kafka (Amazon MSK) is a fully managed service used to build and run applications that use Apache Kafka to process data.

- [MSK Connect](https://docs.aws.amazon.com/msk/latest/developerguide/msk-connect.html):MSK Connect is a feature of AWS MSK, that allows users to stream data to and from their MSK-hosted Apache Kafka clusters. With MSK Connect, you can deploy fully managed connectors that move data into or pull data from popular data stores like Amazon S3 and Amazon OpenSearch Service, or that connect Kafka clusters with external systems, such as databases and file systems

- [AWS API Gateway](https://aws.amazon.com/api-gateway/):Amazon API Gateway is a fully managed service that makes it easy for developers to create, publish, maintain, monitor, and secure APIs at any scale. APIs act as the "front door" for applications to access data, business logic, or functionality from your backend services.

- [Kafka REST Proxy](https://docs.confluent.io/platform/current/kafka-rest/index.html):Kafka REST Proxy integration provides a RESTful interface to a Kafka cluster. This makes it easy to produce and consume messages, view the state of a cluster, or perform administrative actions without using native Kafka protocols or clients.

- [Amazon s3](https://aws.amazon.com/s3/):
Amazon Simple Storage Service (Amazon S3) is an object storage service that offers industry-leading scalability, data availability, security, and performance.

- [AWS MWAA](https://docs.aws.amazon.com/mwaa/latest/userguide/what-is-mwaa.html):Amazon Managed Workflows for Apache Airflow (MWAA) is a managed service that was designed to help you integrate Apache Airflow straight in the cloud, with minimal setup and the quickest time to execution. Apache Airflow is a tool used to schedule and monitor different sequences of processes and tasks, referred to as workflows.

- [Apache Spark](https://spark.apache.org/docs/3.4.1/):Spark is a unified engine for large-scale distributed data processing on computer clusters.

- [PySpark](https://spark.apache.org/docs/3.4.1/api/python/index.html):PySpark is the Python API for Apache Spark.It enables you to perform real-time, large-scale data processing in a distributed environment using Python.

- [Databricks](https://docs.databricks.com/en/index.html): The Databricks Lakehouse Platform is a unified platform that provides tools for building, deploying, sharing, and maintaining enterprise-grade data solutions at scale. Databricks integrates with cloud storage and security in your cloud account, and can manage and deploy cloud infrastructure on your behalf.

- [AWS Kinesis](https://aws.amazon.com/kinesis/):AWS Kinesis can collect streaming data such as event logs, social media feeds, application data, and IoT sensor data in real time or near real-time. Kinesis enables you to process and analyze this data as soon as it arrives, allowing you to respond instantly and gain timely analytics insights.


## Pinterest Data:
In order to emulate the Pinterest's data, this project runs a script,user_posting_emulation.py,that contains the login credentials for a RDS database, which contains three tables with data resembling data received by the Pinterest API when a POST request is made by a user uploading data to Pinterest:

- pinterest_data contains data about posts being updated to Pinterest
- geolocation_data contains data about the geolocation of each - Pinterest post found in pinterest_data
- user_data contains data about the user that has uploaded each post found in pinterest_data 

The data generated looked like following:
pinterest_data:

```{'index': 7528, 'unique_id': 'fbe53c66-3442-4773-b19e-d3ec6f54dddf', 'title': 'No Title Data Available', 'description': 'No description available Story format', 'poster_name': 'User Info Error', 'follower_count': 'User Info Error', 'tag_list': 'N,o, ,T,a,g,s, ,A,v,a,i,l,a,b,l,e', 'is_image_or_video': 'multi-video(story page format)', 'image_src': 'Image src error.', 'downloaded': 0, 'save_location': 'Local save in /data/mens-fashion', 'category': 'mens-fashion'}```

geolocation_data:
```
{'ind': 7528, 'timestamp': datetime.datetime(2020, 8, 28, 3, 52, 47), 'latitude': -89.9787, 'longitude': -173.293, 'country': 'Albania'}```

user_data:

```{'ind': 7528, 'first_name': 'Abigail', 'last_name': 'Ali', 'age': 20, 'date_joined': datetime.datetime(2015, 10, 24, 11, 23, 51)}
```


## Pinterest Architecture

![pintrest-architecture](https://github.com/SoniyaMaheshwari/pinterest-data-pipeline/assets/139882461/49a0e915-a431-4c96-b5cb-42f79326cf1a)

## Building a Data Pipeline
- ### Create Kafka cluster using Amazon MSK:
1. First sign into the Management Console and open the Amazon MSK console, which should look like the picture below:
<img width="496" alt="MSK console 1" src="https://github.com/SoniyaMaheshwari/pinterest-data-pipeline/assets/139882461/06179586-e8a4-487f-94f8-30490d15fab9">

2. To create a new cluster, choose Create Cluster. You will be able to choose between a Quick create and a Custom create option.

3.Scroll down and choose 'Provisioned' and specify the Kafka version and broker type. The type chosen will depend on requirements and cost considerations.

<img width="507" alt="General cluster properties" src="https://github.com/SoniyaMaheshwari/pinterest-data-pipeline/assets/139882461/ff6b144d-ef95-4f3d-989a-f74bbaed2e09">

4. Once the desired cluster has been select, choose View client information to get the cluster information. This should prompt you to a new window, where you can find information about the Bootstrap servers under the Private endpoint section. The bootstrap brokers string will contain the number of brokers you provisioned when creating the cluster On the same page, you will find information about the Apache Zookeeper connection string. Make a note of both strings: the Boostrap server string and the Plaintext Apache Zookeeper connection string

- ### Create a client machine for the MSK cluster:
In this step, you will create an EC2 instance that will act as an Apache Kafka client instance. You will later use this instance to create topics in the cluster.

To create an EC2 instance, open the EC2 console, specifically the Instances tab and choose Launch instances. Keep the default Amazon Machine Image, and for Instance type select the t2.micro.

Under Key pair(login) select Create a new key pair, and enter a name for this pair. Then choose Download Key Pair. Alternatively you can use an existing key pair. Finally, choose Launch instance.
 1. Allow client machine to send data to the cluster
 
    Make sure the client machine can send data to the MSK cluster, by checking the Security groups of the cluster Virtual Private Cloud (VPC). To access this, open the VPC console and under Security choose Security groups. Select the default security group associated with the cluster VPC.Now, choose Edit inbound rules and select Add rule. In the Type column choose All traffic. In the Source column add the ID of the security group of the client machine (this can be found in the EC2 console). Once you choose Save rules, your cluster will accept all traffic from the client machine.

2. Install Kafka on the client machine

    Connect to the EC2 client machine using the terminal. On the EC2 console you should choose Connect, and you will see something like the picture below:
 <img width="503" alt="Connect EC2" src="https://github.com/SoniyaMaheshwari/pinterest-data-pipeline/assets/139882461/615c3302-0a7c-4927-b3ba-0e1d2fe7467b">

    First of all, you should be in the folder (in your terminal) where you saved you Private key file, then follow the steps in the image above.

Once inside the EC2 client we will first need to install Java by running the following command:

```
sudo yum install java-1.8.0
```

Then we will download Apache Kafka using the commands below:
```
wget https://archive.apache.org/dist/kafka/2.8.1/kafka_2.12-2.8.1.tgz
tar -xzf kafka_2.12-2.8.1.tgz
```

To connect to a cluster that uses IAM authentication, we will need to follow additional steps before we are ready to create a topic on our client machine.

First, navigate to your Kafka installation folder and then in the libs folder. Inside here we will download the IAM MSK authentication package from Github, using the following command:

```
wget https://github.com/aws/aws-msk-iam-auth/releases/download/v1.1.5/aws-msk-iam-auth-1.1.5-all.jar
```

#### CLASSPATH environment variable

The CLASSPATH environment variable is used by Java applications to specify the directories or JAR files that contain the required classes and resources. By adding the path to the aws-msk-iam-auth-1.1.5-all.jar file to the CLASSPATH, the Kafka client will be able to locate and utilize the necessary Amazon MSK IAM libraries when executing commands.

To set up the CLASSPATH environment variable, you can use the following command:

```
export CLASSPATH=/home/ec2-user/kafka_2.12-2.8.1/libs/aws-msk-iam-auth-1.1.5-all.jar
```


### Configure Kafka client to use AWS IAM:

To configure a Kafka client to use AWS IAM for authentication you should first navigate to your Kafka installation folder, and then in the bin folder.

Here, you should create a client.properties file, using the following command:

nano client.properties

The client's configuration file should contain the following:

```
# Sets up TLS for encryption and SASL for authN.
security.protocol = SASL_SSL

# Identifies the SASL mechanism to use.
sasl.mechanism = AWS_MSK_IAM

# Binds SASL client implementation.
sasl.jaas.config = software.amazon.msk.auth.iam.IAMLoginModule required awsRoleArn="Your Access Role";

# Encapsulates constructing a SigV4 signature based on extracted credentials.
# The SASL client bound by "sasl.jaas.config" invokes this class.
sasl.client.callback.handler.class = software.amazon.msk.auth.iam.IAMClientCallbackHandler
```

### Create a topic on a client machine:

To create a topic, make sure you are inside your <KAFKA_FOLDER>/bin and then run the following command, replacing BoostrapServerString with the connection string you have previously saved, and <topic_name> with your desired topic name:

```
./kafka-topics.sh --bootstrap-server BootstrapServerString --command-config client.properties --create --topic <topic_name>
```

For this project, I created three topics. One each for the pinterest_data, geolocation_data, and user_data outlined above.

### Delivering messages to Kafka cluster
Now that our cluster is up and running, and the client is configured to access the cluster and create topics, it's possible to use the client to create producers for streaming messages to the cluster, and consumers for accessing those messages.

However, for this project I used the Confluent package to set up a REST API on the client that listens for requests and interacts with the Kafka cluster accordingly.

To do this, first download the Confluent package to the client from the client's command line:

```
sudo wget https://packages.confluent.io/archive/7.2/confluent-7.2.0.tar.gz
tar -xvzf confluent-7.2.0.tar.gz 
```

You should now be able to see a confluent-7.2.0 directory on your EC2 instance. To configure the REST proxy to communicate with the desired MSK cluster, and to perform IAM authentication you first need to navigate to confluent-7.2.0/etc/kafka-rest. Inside here run the following command to modify the kafka-rest.properties file:

```
nano kafka-rest.properties
```
Firstly, you need to modify the bootstrap.servers and the zookeeper.connect variables in this file, with the corresponding Boostrap server string and Plaintext Apache Zookeeper connection string respectively (check-out the MSK Essential lesson to see how to obtain these). This will allow the REST proxy to connect to our MSK cluster.

Secondly, to surpass the IAM authentication of the MSK cluster, we will make use of the IAM MSK authentication package again (can be found here: https://github.com/aws/aws-msk-iam-auth). That means, you should add the following to your kafka-rest.properties file:

```
# Sets up TLS for encryption and SASL for authN.
client.security.protocol = SASL_SSL

# Identifies the SASL mechanism to use.
client.sasl.mechanism = AWS_MSK_IAM

# Binds SASL client implementation.
client.sasl.jaas.config = software.amazon.msk.auth.iam.IAMLoginModule required awsRoleArn="Your Access Role";

# Encapsulates constructing a SigV4 signature based on extracted credentials.
# The SASL client bound by "sasl.jaas.config" invokes this class.
client.sasl.client.callback.handler.class = software.amazon.msk.auth.iam.IAMClientCallbackHandler
```

Before sending messages to the API, in order to make sure they are consumed in MSK, we need to start our REST proxy. To do this, first navigate to the confluent-7.2.0/bin folder, and then run the following command:

```
./kafka-rest-start /home/ec2-user/confluent-7.2.0/etc/kafka-rest/kafka-rest.properties
```

### Connect MSK cluster to s3 Bucket:
1. Create the S3 Bucket:
Open the Amazon S3 console and choose Create bucket. For the bucket name select your desired name. Make sure to select the same AWS Region (in our case us-east-1) as the region in which you created your MSK cluster. Finally, choose Create bucket.

<img width="474" alt="Create Bucket" src="https://github.com/SoniyaMaheshwari/pinterest-data-pipeline/assets/139882461/88986e67-a4f5-4bf1-8f15-24cbea946fff">

2. Create an IAM role that can write to the destination bucket

Navigate to the IAM console, and select Roles under the Access management section. Choose Create role to create a new IAM role.

Under Trusted entity type, select AWS service, and under the Use case field select S3 in the Use cases for other AWS services field


<img width="468" alt="IAM Role Trusted Entity" src="https://github.com/SoniyaMaheshwari/pinterest-data-pipeline/assets/139882461/8220dc08-f92c-4d6d-a212-6288651e2643">

In the permission tab, select Create policy. This will open a new tab where you can create the desired policy. Select the JSON tab. Replace the existing text with the following policy:

```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "VisualEditor0",
            "Effect": "Allow",
            "Action": [
                "s3:ListBucket",
                "s3:DeleteObject",
                "s3:GetBucketLocation"
            ],
            "Resource": [
                "arn:aws:s3:::<DESTINATION_BUCKET>",
                "arn:aws:s3:::<DESTINATION_BUCKET>/*"
            ]
        },
        {
            "Sid": "VisualEditor1",
            "Effect": "Allow",
            "Action": [
                "s3:PutObject",
                "s3:GetObject",
                "s3:ListBucketMultipartUploads",
                "s3:AbortMultipartUpload",
                "s3:ListMultipartUploadParts"
            ],
            "Resource": "*"
        },
        {
            "Sid": "VisualEditor2",
            "Effect": "Allow",
            "Action": "s3:ListAllMyBuckets",
            "Resource": "*"
        }
    ]
}
```
This policy creates the necessary permissions to write to the destination bucket. Skip the rest of the pages until you reach the Create policy button.

Now back to the main tab for the IAM role, you should be able to find the policy you have just created, and then select it. Skip the rest of the pages until you reach the Create role button. Once you have select it, the new IAM role will be created.

In the IAM console, choose the role you have just created, and select the Trust relationships tab. In the Trusted entities tab you should add the following trust policy:

```{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Service": "kafkaconnect.amazonaws.com"
            },
            "Action": "sts:AssumeRole"
        }
    ]
}

```

This trust relationship allows MSK Connect to assume the role to which we attached the policy created above. Finally select the Update Trust Policy.

3. Create a VPC endpoint to S3.
In the VPC console, select Endpoints under the Virtual private cloud tab and then choose Create endpoint.

Under Service Name choose com.amazonaws.us-east-1.s3 and the Gateway type. Choose the VPC that corresponds to the MSK cluster's VPC from the drop-down menu in VPC section. Finally, select Create endpoint.
<img width="449" alt="VPC Endpoint" src="https://github.com/SoniyaMaheshwari/pinterest-data-pipeline/assets/139882461/bab4279a-79a6-427a-9e9d-0b62608b20a4">

#### Create the custom plugin
A plugin will contain the code that defines the logic of our connector. We will use the client EC2 machine we have previously used (check out MSK Essentials lesson) to connect to our cluster for this step.

First connect to your client EC2 machine. We will download the Confluent.io Amazon S3 Connector on our machine, and then copy it to the S3 bucket we have previously created. This connector is a sink connector that exports data from Kafka topics to S3 objects in either JSON, Avro or Bytes format. To do download & copy this connector run the code below inside your client machine:

```
# assume admin user privileges
sudo -u ec2-user -i
# create directory where we will save our connector 
mkdir kafka-connect-s3 && cd kafka-connect-s3
# download connector from Confluent
wget https://d1i4a15mxbxib1.cloudfront.net/api/plugins/confluentinc/kafka-connect-s3/versions/10.0.3/confluentinc-kafka-connect-s3-10.0.3.zip
# copy connector to our S3 bucket
aws s3 cp ./confluentinc-kafka-connect-s3-10.0.3.zip s3://<BUCKET_NAME>/kafka-connect-s3/
```

Now, open the MSK console and select Custom plugins under the MSK Connect section on the left side of the console. Choose Create custom plugin.

In the list of buckets, find the bucket where you upload the Confluent connector ZIP file. Then, in the list of objects in that bucket select the ZIP file and select the Choose button. Give the plugin a name and press Create custom plugin.

<img width="467" alt="Custom plugin" src="https://github.com/SoniyaMaheshwari/pinterest-data-pipeline/assets/139882461/606c4353-e539-4321-9555-c81bb78c97ac">

Once the plugin has been created you should see the following message at the top of your browser window:

plugin <PLUGIN_NAME> was successfully created. The custom plugin was created. You can now create a connector using this custom plugin

#### Create the connector

In the MSK console, select Connectors under the MSK Connect section on the left side of the console. Choose Create connector.

In the list of plugin, select the plugin you have just created, and then click Next. For the connector name choose the desired name, and then choose your MSK cluster from the cluster list.

In the Connector configuration settings copy the following configuration

```
connector.class=io.confluent.connect.s3.S3SinkConnector
# same region as our bucket and cluster
s3.region=us-east-1
flush.size=1
schema.compatibility=NONE
tasks.max=3
# include nomeclature of topic name, given here as an example will read all data from topic names starting with msk.topic....
topics.regex=<YOUR_UUID>.*
format.class=io.confluent.connect.s3.format.json.JsonFormat
partitioner.class=io.confluent.connect.storage.partitioner.DefaultPartitioner
value.converter.schemas.enable=false
value.converter=org.apache.kafka.connect.json.JsonConverter
storage.class=io.confluent.connect.s3.storage.S3Storage
key.converter=org.apache.kafka.connect.storage.StringConverter
s3.bucket.name=<BUCKET_NAME>
```
Leave the rest of the configurations as default, except for:

Worker Configuration, select "Use a customised configuration", then pick "confluent-worker"
Access permissions, where you should select the IAM role you have created previously.
Skip the rest of the pages until you get to Create connector button page. Once your connector is up and running you will be able to visualise it in the Connectors tab in the MSK console.


### AWS API Gateway
Upon opening the AWS API Gateway from the AWS Services dashboard, you will be met with this landing page:
<img width="493" alt="API Gateway Console" src="https://github.com/SoniyaMaheshwari/pinterest-data-pipeline/assets/139882461/6ed097a5-5e01-43a9-a9ed-fd8df0931613">

After selecting Create API, you can chose the type of API you want to build (HTTP, REST or WebSocket) or import your externally developed API.


<img width="508" alt="APIs Types" src="https://github.com/SoniyaMaheshwari/pinterest-data-pipeline/assets/139882461/eca96b29-e274-4aef-a788-e5c6c6a4492c">

For this project, we will be building a new REST API. Select Build from the REST API option to create a new REST API.

Under Choose the protocol select REST API, and under Create new API select New API. Name the API, and provide a description.

<img width="497" alt="Create API" src="https://github.com/SoniyaMaheshwari/pinterest-data-pipeline/assets/139882461/1ab78b29-0d28-42c3-b76e-c4b9ecd194c8">

On the Actions dropdown list, you will be presented with the various options for creating resources and methods:

<img width="516" alt="Create Resource" src="https://github.com/SoniyaMaheshwari/pinterest-data-pipeline/assets/139882461/19c7b373-af8e-458c-a0b7-a276484ccfe6">

We will create a new child resource for our API. Select Configure as proxy resource. For Resource Name enter proxy and for Resource Path enter /{proxy+}. Finally, select Enable API Gateway CORS and choose Create Resource.
<img width="476" alt="New Child Resource" src="https://github.com/SoniyaMaheshwari/pinterest-data-pipeline/assets/139882461/9c3c6c20-64e9-4840-97a6-ed3c03bf0a81">

For Integration type select HTTP Proxy. HTTP proxy integration is a simple, yet powerful way of building APIs that allow web applicaitons to access multiple resources on the integrated HTTP endpoint. In HTTP proxy integration, API Gateway simply passes client-submitted method requests to the backend. In turn the backend HTTP endpoint parses the incoming data request to determine the appropiate return responses.

For the Endpoint URL, you will need to enter your Kafka Client Amazon EC2 Instance PublicDNS. You can obtain your EC2 Instance Public DNS by navigating to the EC2 console. Here, select your client EC2 machine and look for Public IPv4 DNS and copy this. The endpoint URL should have the following format:

```
http://KafkaClientEC2InstancePublicDNS:8082/{proxy}
```

<img width="492" alt="APIs Integration" src="https://github.com/SoniyaMaheshwari/pinterest-data-pipeline/assets/139882461/ab42cc2b-3fda-4e9d-b8a8-7a86fda174af">

#### Deploy API

Make note of the Invoke URL after deploying the API. Your external Kafka REST Proxy, which was exposed through API Gateway will look like:

```
https://YourAPIInvokeURL/test/topics/<AllYourTopics>
```

### Send Data to the API
Using batch_data.py send data to  Kafka topics using API Invoke URL.
Send data from the three tables to their corresponding Kafka topic.


## Processing Batch Data on Databricks
Using Apache spark batch data is processed on Databricks.
In order to clean and query batch data, we will need to read this data from the s3 bucket into Databricks. To do this, we will need to mount the desired S3 bucket to the Databricks account.
s3_batch_data_processing.ipynb file has all the required steps to mount the s3 bucket and read data.

Here 3 dataframes are created
- df_pin for the Pinterest post data
- df_geo for the geolocation data
- df_user for the user data.

After that we have perforemed cleaning and computations using Apache spark.

#### Orchestrate Databricks Workloads on AWS MWAA
MWAA was used to automate the process of running the batch processing on Databricks. The file 0a70d64d47bd_dag.py is the Python code for a directed acyclic graph (DAG) that orchestrates the running of the batch processing notebook described above. The file was uploaded to the MWAA environment, where Airflow is utilised to connect to and run the Databricks notebook at scheduled intervals, in this case @daily.

## Stream Processing: AWS Kinesis

Using Kinesis Data Streams create three data streams, one for each Pinterest table.

Navigate to the Kinesis console, and select the Data Streams section. Choose the Create stream button.

<img width="500" alt="Create Stream" src="https://github.com/SoniyaMaheshwari/pinterest-data-pipeline/assets/139882461/36373d41-b7f5-4a33-8a89-fc4dd079cd1e">

Choose the desired name for your stream and input this in the Data stream name field. For our use case we will use the Provisioned capacity mode.

<img width="409" alt="Data Stream Config" src="https://github.com/SoniyaMaheshwari/pinterest-data-pipeline/assets/139882461/e94ab884-9193-411c-b7c9-85c6795258cc">

For this project , three streams are created
1. stream-pin
2. stream-geo
3. stream-user

#### Configure an API with Kinesis proxy Integration.
Configure the previously created REST API to allow it to invoke Kinesis actions.

API invokes the following actions:

- List streams in Kinesis
- Create, describe and delete streams in Kinesis
- Add records to streams in Kinesis

#### Send Data to Kinesis Streams
Running the script kinesis_streaming.py starts an infinite loop that, that retrieves records from the RDS database and sends them via the new API to Kinesis.

#### Process stream Data in Databricks.
The notebook kinesis_stream_processing.ipynb contains all the code necessary for retrieving the streams from Kinesis,cleaning the data, and then writing the data into Delta tables on the Databricks cluster






