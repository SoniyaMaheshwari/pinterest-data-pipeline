# pinterest-data-pipeline

## Table of contents
- [Project Introduction](#project-introduction)
- [Dependencies](#dependencies)
- [Tools Used](#tools-used)
- [Pinterest Data](#pinterest-data)
- [Pinterest Architecture](#pinterest-architecture)














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




