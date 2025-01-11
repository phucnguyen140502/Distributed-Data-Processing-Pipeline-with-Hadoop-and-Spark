from concurrent.futures import ThreadPoolExecutor, as_completed
import pandas as pd
import time
import psutil
import os
import pyarrow.parquet as pq
import pyarrow as pa


def count_french_words(chunk):
    """Đếm từ 'french' trong chunk"""
    try:
        french_word = "french"
        # Calculate count in 'name' and 'country' columns using optimized string operations
        return (
            chunk['name'].str.lower().str.contains(french_word).sum() +
            chunk['country'].str.lower().str.contains(french_word).sum()
        )
    except Exception as e:
        print(f"Error in count_french_words: {e}")
        return 0


def process_chunk(chunk, chunk_index):
    """Xử lý chunk và trả kết quả"""
    try:
        start_time = time.time()
        
        # Đếm từ 'french' trong chunk
        count = count_french_words(chunk)
        processing_time = time.time() - start_time
        
        # Log each chunk's processing time every 10th chunk
        if chunk_index % 10 == 0:
            cpu_percent, ram_percent = get_process_resources(os.getpid())
            print(f"[Thread-{chunk_index}] Thời gian xử lý: {processing_time:.2f}s, CPU: {cpu_percent}% | RAM: {ram_percent}% | Số từ 'french': {count}")
        
        # Giải phóng GIL bằng cách thêm sleep
        time.sleep(0.1)  # Nhả GIL để các thread khác có thể thực thi

        return len(chunk), count, processing_time
    except Exception as e:
        print(f"[Thread-{chunk_index}] Lỗi: {e}")
        return 0, 0, 0


def get_process_resources(pid=None):
    """Lấy tài nguyên của process (CPU, RAM)"""
    try:
        process = psutil.Process(pid)
        cpu_percent = process.cpu_percent(interval=0.1)
        memory_info = process.memory_info()
        memory_percent = (memory_info.rss / psutil.virtual_memory().total) * 100
        return cpu_percent, memory_percent
    except psutil.NoSuchProcess:
        return 0, 0


def create_parquet_from_csv(csv_file, parquet_file):
    """Tạo file Parquet từ CSV nếu chưa có"""
    if not os.path.exists(parquet_file):
        print(f"File {parquet_file} chưa tồn tại, đang chuyển đổi...")
        df = pd.read_csv(csv_file, usecols=['name', 'country'])
        table = pa.Table.from_pandas(df)
        pq.write_table(table, parquet_file)
        print(f"File Parquet {parquet_file} đã được tạo.")
    else:
        print(f"File Parquet {parquet_file} đã tồn tại, sẽ đọc từ đó.")


def read_and_process_parquet(file_path, chunk_size, num_workers):
    total_count = 0
    total_rows = 0
    total_processing_time = 0

    start_time = time.time()

    # Đọc dữ liệu từ file Parquet
    parquet_file = pq.ParquetFile(file_path)
    
    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        futures = []
        
        # Read row groups with a chunk of rows for efficient memory usage
        for chunk_index in range(parquet_file.num_row_groups):
            try:
                # Read a row group and convert it to pandas DataFrame (with specific columns)
                chunk = parquet_file.read_row_group(chunk_index).to_pandas()[['name', 'country']]
                
                # Send chunk for processing
                future = executor.submit(process_chunk, chunk, chunk_index)
                futures.append(future)
            except Exception as e:
                print(f"Lỗi khi đọc row group {chunk_index}: {e}")
                continue

        # Wait for all threads to complete and aggregate results
        for future in as_completed(futures):
            try:
                rows, count, processing_time = future.result()
                total_rows += rows
                total_count += count
                total_processing_time += processing_time
            except Exception as e:
                print(f"Lỗi khi xử lý chunk: {e}")

    end_time = time.time()
    print(f"Tổng số dòng: {total_rows}, tổng số từ 'french': {total_count}")
    print(f"Tổng thời gian: {end_time - start_time:.2f} giây")
    print(f"Tổng thời gian thực tế của các chunks: {total_processing_time:.2f} giây")


# Thực thi
csv_file_path = r"D:\Data Engineer\dwh and etl\lesson\lesson 2\documents\Talend\Sync Hadoop to DWH\citizens_data.csv"
parquet_file_path = r"D:\Data Engineer\dwh and etl\lesson\lesson 2\documents\Talend\Sync Hadoop to DWH\citizens_data.parquet"
chunk_size = 22_500_000  # Kích thước chunk
num_workers = 4         # Sử dụng 32 worker threads nếu hệ thống hỗ trợ

# Kiểm tra và tạo file Parquet nếu chưa có
create_parquet_from_csv(csv_file_path, parquet_file_path)

# Đọc và xử lý dữ liệu từ file Parquet
read_and_process_parquet(parquet_file_path, chunk_size, num_workers)
