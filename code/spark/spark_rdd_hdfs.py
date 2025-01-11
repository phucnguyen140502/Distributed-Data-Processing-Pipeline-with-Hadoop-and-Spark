import os
import logging
from pyspark.sql import SparkSession
import time
import psutil

# Define log directory and file path
log_dir = "D:\\Data Engineer\\dwh and etl\\lesson\\lesson 2\\documents\\Hadoop\\spark_logs"
log_file = os.path.join(log_dir, "detailed_log_rdd_hdfs.log")

# Create the log directory if it does not exist
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# Set up logging configuration
logging.basicConfig(
    filename=log_file,
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s - [Thread: %(threadName)s]"
)

def log_system_details(step_name="Unknown", description="Unknown"):
    # Get system information
    cpu_usage = psutil.cpu_percent(interval=1)
    ram_usage = psutil.virtual_memory().percent
    io_counters = psutil.disk_io_counters()
    cpu_count = psutil.cpu_count(logical=True)  # Total logical CPU cores
    cpu_affinity = psutil.Process().cpu_affinity()  # List of CPUs the process can run on
    
    # Log detailed CPU, RAM, I/O, core, and affinity info
    logging.debug(f"Step: {step_name} | Description: {description} | CPU Usage: {cpu_usage}% | RAM Usage: {ram_usage}% | "
                  f"Disk Read: {io_counters.read_bytes} bytes | Disk Write: {io_counters.write_bytes} bytes | "
                  f"Total CPU Cores: {cpu_count} | CPU Affinity: {cpu_affinity}")

def log_block_info(rdd_data, partition_id, step_name="Unknown"):
    # Log detailed information about blocks in each partition
    block_info = f"Partition {partition_id} is processing {len(rdd_data)} rows: {rdd_data[:5]}..."  # Log first few rows for tracking
    logging.debug(f"{step_name} | {block_info}")

# Initialize SparkSession
# Initialize SparkSession
spark = SparkSession.builder \
    .appName("RDD HDFS Block Logging") \
    .master("local[2]") \
    .config("spark.driver.memory", "4g") \
    .config("spark.executor.memory", "4g") \
    .config("spark.network.timeout", "30000s") \
    .config("spark.executor.heartbeatInterval", "12000s") \
    .getOrCreate()



# Read data from HDFS and log system details
logging.info("Starting data read from HDFS")
log_system_details("Starting data read from HDFS", "Reading data")

start_time_hdfs_rdd = time.time()
citizens_rdd_hdfs = spark.sparkContext.textFile("hdfs://172.30.2.147:9000/demo_directory/citizens_data.csv")
# Adjust the number of partitions for better load distribution
citizens_rdd_hdfs = citizens_rdd_hdfs.repartition(10)  # Use a suitable number based on your setup

# Log information about blocks while reading data
citizens_rdd_hdfs = citizens_rdd_hdfs.mapPartitionsWithIndex(lambda idx, it: [log_block_info(list(it), idx, "Reading data from HDFS")] + list(it))
# Cache the RDD after loading to reuse it across actions
citizens_rdd_hdfs = citizens_rdd_hdfs.cache()


# Filter out the header
header = citizens_rdd_hdfs.first()
data_citizens_rdd_hdfs = citizens_rdd_hdfs.filter(lambda line: line != header)

# Process data (map, reduce)
data_citizens_rdd_hdfs = data_citizens_rdd_hdfs.map(lambda x: (x.split(",")[4], 1))
cities_in_country_hdfs = data_citizens_rdd_hdfs.reduceByKey(lambda x, y: x + y)

# Collect final results
cities_in_country_hdfs.collect()
time.sleep(1)

# Log system details at the end of processing
log_system_details("Data processing complete", "Processing complete")

# Calculate processing time
end_time_hdfs_rdd = time.time()
time_hdfs_rdd = end_time_hdfs_rdd - start_time_hdfs_rdd
logging.info(f"Processing time for HDFS RDD: {time_hdfs_rdd:.2f} seconds")

# Print the processing time
print(f"Processing time using RDD with HDFS: {time_hdfs_rdd:.2f} seconds")
