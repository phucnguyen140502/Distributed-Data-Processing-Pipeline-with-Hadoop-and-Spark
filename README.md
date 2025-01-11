# Distributed Data Processing Pipeline with Hadoop and Spark

![image](https://github.com/user-attachments/assets/2148671d-7b28-414c-bdab-d97c689244ca)

This document describes a basic design for a distributed data processing pipeline that handles daily-generated CSV files, specifically a 6GB file named `citizens_data.csv`. The processed results are stored in a PostgreSQL Data Warehouse for further analysis. This project has been a learning experience, focusing on the fundamental aspects of Hadoop and Apache Spark.

## 1. Hadoop Cluster Setup

### Cluster Deployment
- **VPS 1 (172.30.2.147)**: Configured as both NameNode and DataNode.
- **VPS 2 (172.30.2.207)**: Set up as an additional DataNode.

### HDFS Configuration
- Configured HDFS to store the `citizens_data.csv` file, ensuring it is distributed across DataNodes with replication enabled for fault tolerance.

## 2. Dataset Upload
- Automated the daily upload of `citizens_data.csv` into HDFS for storage.

## 3. ETL from MySQL to HDFS using Talend

### Talend Configuration
- Utilized Talend Open Studio to extract data from MySQL, transform it as needed, and load it into HDFS.

## 4. Automation with Airflow
- Created an Airflow Directed Acyclic Graph (DAG) to automate the daily ETL job, running Talend jobs as part of the pipeline.

## 5. Apache Spark Setup

### Spark Installation
- Installed Apache Spark on both VPSs:
  - **VPS 1**: Acts as Spark Master and Worker 1.
  - **VPS 2**: Configured as Spark Worker 2.

### Data Processing
- Configured Spark to read the `citizens_data.csv` file from HDFS and perform data transformations and analysis using PySpark.

## 6. Store Results in Data Warehouse
- After processing, Spark writes the results into a PostgreSQL Data Warehouse using an ETL job written in Python.

## 7. Automation and Scheduling with Airflow
- The entire pipeline is deployed on Apache Airflow, automating daily tasks:
  - Load data into HDFS with Talend.
  - Process data with Spark.
  - Store results in PostgreSQL DWH.
