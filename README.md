# Distributed Data Processing Pipeline with Hadoop and Spark

![image](https://github.com/user-attachments/assets/2148671d-7b28-414c-bdab-d97c689244ca)

## 1. Hadoop Cluster Setup

### Cluster Deployment
- **VPS 1 (172.30.2.147)**: Configured as both NameNode and DataNode.
- **VPS 2 (172.30.2.207)**: Set up as an additional DataNode.

### HDFS Configuration
- HDFS is configured to store the `citizens_data.csv` file, ensuring it is distributed across DataNodes with replication enabled for fault tolerance.

## 2. Dataset Upload
- An automated process is established to upload the `citizens_data.csv` file daily into HDFS for storage.

## 3. ETL from MySQL to HDFS using Talend

### Talend Configuration
- Talend Open Studio is used to extract data from MySQL, transform it as needed, and load it into HDFS.

## 4. Automation with Airflow
- An Airflow Directed Acyclic Graph (DAG) is created to automate the daily ETL job, running Talend jobs as part of the pipeline.

## 5. Apache Spark Setup

### Spark Installation
- Apache Spark is installed on both VPSs:
  - **VPS 1**: Acts as Spark Master and Worker 1.
  - **VPS 2**: Configured as Spark Worker 2.

### Data Processing
- Spark is configured to read the `citizens_data.csv` file from HDFS, performing data transformations and analysis using PySpark.

## 6. Store Results in Data Warehouse
- After processing, Spark writes the results into a PostgreSQL Data Warehouse using an ETL job written in Python.

## 7. Automation and Scheduling with Airflow
- The entire pipeline is deployed on Apache Airflow, automating daily tasks:
  - Load data into HDFS with Talend.
  - Process data with Spark.
  - Store results in PostgreSQL DWH.

## Value Gained
- **Hadoop Basics**: Understanding of setting up a Hadoop cluster and managing data storage in HDFS.
- **Spark Basics**: Knowledge of Spark’s master-worker architecture for distributed data processing.
- **Automation Skills**: Experience in automating data loading, processing, and storage using Airflow for seamless daily operations.

This pipeline effectively manages large daily datasets through automation and distributed computing, ensuring efficient data handling and analysis.
