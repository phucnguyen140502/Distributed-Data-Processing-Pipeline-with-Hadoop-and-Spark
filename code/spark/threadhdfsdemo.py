from pyspark.sql import SparkSession
from datetime import datetime
import logging
import threading
import subprocess

# Khởi tạo Spark session
spark = SparkSession.builder.appName("DetailedHDFSReadLogging").getOrCreate()

# Cấu hình logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger("BlockLogger")

# Hàm để lấy thông tin block từ HDFS
def get_hdfs_block_info(hdfs_path):
    # Dùng `hdfs fsck` để lấy thông tin block (yêu cầu quyền truy cập vào lệnh hdfs)
    result = subprocess.run(["hdfs", "fsck", hdfs_path, "-files", "-blocks", "-locations"], 
                            capture_output=True, text=True)
    return result.stdout

# Ghi log thông tin partition khi đọc file từ HDFS
def log_partition_info(iterator, hdfs_path):
    thread_id = threading.get_ident()
    start_time = datetime.now()

    # Lấy thông tin block từ HDFS
    hdfs_info = get_hdfs_block_info(hdfs_path)
    log.info(f"Thread ID {thread_id} started reading partition at {start_time}. HDFS Info:\n{hdfs_info}")

    for record in iterator:
        yield record

    end_time = datetime.now()
    log.info(f"Thread ID {thread_id} finished reading partition at {end_time}. Duration: {end_time - start_time}")

# Đường dẫn tới file HDFS và đọc dữ liệu
hdfs_path = "hdfs://172.30.2.147:9000/demo_directory/citizens_data.csv"
rdd = spark.sparkContext.textFile(hdfs_path)

# Áp dụng hàm log_partition_info trên mỗi partition
rdd.mapPartitions(lambda x: log_partition_info(x, hdfs_path)).count()

spark.stop()