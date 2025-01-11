from pyspark.sql import SparkSession
import time
import logging
import psutil
import threading
import os

# # Cấu hình logging với mức DEBUG để ghi log chi tiết
# logging.basicConfig(
#     filename="spark_logs/detailed_log_rdd_local.log",  # Đường dẫn tới file log
#     level=logging.DEBUG,
#     format="%(asctime)s - %(levelname)s - %(message)s - [Thread: %(threadName)s]"
# )

# def log_system_details(step_name="Unknown", description="Unknown"):
#     # Lấy thông tin hệ thống
#     cpu_usage = psutil.cpu_percent(interval=1)
#     ram_usage = psutil.virtual_memory().percent
#     io_counters = psutil.disk_io_counters()
#     cpu_core = psutil.Process().cpu_num()  # Core đang hoạt động
#     cpu_affinity = psutil.Process().cpu_affinity()  # Danh sách CPU mà tiến trình có thể chạy
    
#     # Ghi log chi tiết về CPU, RAM, I/O, core và block
#     logging.debug(f"Step: {step_name} | Description: {description} | CPU Usage: {cpu_usage}% | RAM Usage: {ram_usage}% | "
#                   f"Disk Read: {io_counters.read_bytes} bytes | Disk Write: {io_counters.write_bytes} bytes | "
#                   f"CPU Core: {cpu_core} | CPU Affinity: {cpu_affinity}")

# def log_block_info(rdd_data, partition_id, step_name="Unknown"):
#     # Ghi log chi tiết về các block trong từng partition
#     block_info = f"Partition {partition_id} đang xử lý {len(rdd_data)} dòng dữ liệu: {rdd_data[:5]}..."  # Ghi lại một vài dòng dữ liệu để dễ theo dõi
#     logging.debug(f"{step_name} | {block_info}")

# Khởi tạo SparkSession với cấu hình tối ưu hóa bộ nhớ và xử lý
spark = SparkSession.builder \
    .appName("RDD local Block Logging") \
    .master("Local[2]") \
    .config("spark.driver.memory", "1g") \
    .config("spark.executor.memory", "1g") \
    .config("spark.network.timeout", "12000s") \
    .config("spark.driver.maxResultSize", "2g") \
    .config("spark.executor.heartbeatInterval", "2000s") \
    .config("spark.sql.shuffle.partitions", "100") \
    .config("spark.default.parallelism", "100") \
    .config("spark.executor.memoryOverhead", "1g") \
    .config("spark.driver.maxResultSize", "2g") \
    .getOrCreate()

# # Đọc dữ liệu từ local và tính thời gian
# logging.info("Bắt đầu đọc dữ liệu từ Local")
# log_system_details("Bắt đầu đọc dữ liệu từ Local", "Bắt đầu đọc")

start_time_local_rdd = time.time()
# citizens_rdd_local = spark.sparkContext.textFile("file:///home/hadoopuser/citizens_data.csv")
# citizens_rdd_local = citizens_rdd_local.repartition(100)  # Tăng số lượng partition nếu quá ít

# Log thông tin block khi đọc dữ liệu từ local
# citizens_rdd_local = citizens_rdd_local.mapPartitionsWithIndex(lambda idx, it: [log_block_info(list(it), idx, "Đọc dữ liệu từ local")] + list(it))

# # Loại bỏ header
# header = citizens_rdd_local.first()  # Lấy dòng đầu tiên làm header
# data_citizens_rdd_local = citizens_rdd_local.filter(lambda line: line != header)

# # Log thông tin block sau khi loại bỏ header
# # log_block_info(data_citizens_rdd_local.take(5), "Filter stage", "Sau khi sử dụng filter")

# # Ghi lại thông tin hệ thống khi bắt đầu xử lý
# # log_system_details("Bắt đầu xử lý dữ liệu", "Bắt đầu xử lý")

# # Xử lý dữ liệu (map, reduce)

# # Sử dụng map để xử lý dữ liệu
# data_citizens_rdd_local = data_citizens_rdd_local.map(lambda x: (x.split(",")[4], 1))

# # Log thông tin block sau khi sử dụng map
# # log_block_info(data_citizens_rdd_local.take(5), "Map stage", "Sau khi sử dụng map")

# # Reduce để tính tổng số lượng các thành phố
# cities_in_country_local = data_citizens_rdd_local.reduceByKey(lambda x, y: x + y)

# # Log thông tin block sau khi sử dụng reduce
# # log_block_info(cities_in_country_local.take(5), "Reduce stage", "Sau khi sử dụng reduce")

# # Log thông tin về kết quả cuối cùng
# cities_in_country_local.take(5)
# time.sleep(1)

# Ghi lại thông tin hệ thống khi kết thúc xử lý
# log_system_details("Kết thúc xử lý dữ liệu", "Kết thúc xử lý")

# Tính thời gian kết thúc
end_time_local_rdd = time.time()
time_local_rdd = end_time_local_rdd - start_time_local_rdd
# logging.info(f"Thời gian xử lý Local RDD: {time_local_rdd:.2f} giây")

# Kết quả ra màn hình
print(f"Thời gian xử lý bằng RDD chạy với local: {time_local_rdd:.2f} giây")
# print(f"Số lượng patition của rdd đầu tiên: {citizens_rdd_local.getNumPartitions():.2f}")
# print(f"Số lượng patition của rdd cuối cùng: {cities_in_country_local.getNumPartitions():.2f}")

