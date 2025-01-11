from concurrent.futures import ThreadPoolExecutor, as_completed
import pandas as pd
import time
import psutil
import os

def count_french_words(chunk):
    """Hàm đếm từ 'french' trong chunk"""
    try:
        french_word = "french"
        return (
            chunk['name'].str.lower().str.count(french_word).sum() +
            chunk['country'].str.lower().str.count(french_word).sum()
        )
    except Exception as e:
        print(f"Error in count_french_words: {e}")
        return 0

def process_chunk(chunk, chunk_index):
    """Xử lý từng chunk và thông báo chi tiết"""
    try:
        start_time = time.time()
        print(f"[Thread-{chunk_index}] Bắt đầu xử lý chunk với {len(chunk)} dòng...")
        
        # Đếm từ 'french' trong chunk
        count = count_french_words(chunk)
        processing_time = time.time() - start_time
        
        # Lấy thông tin tài nguyên (CPU, RAM) của thread đang xử lý
        cpu_percent, ram_percent = get_process_resources(os.getpid())
        print(f"[Thread-{chunk_index}] Đã hoàn thành xử lý trong {processing_time:.2f}s.")
        print(f"[Thread-{chunk_index}] CPU: {cpu_percent}% | RAM: {ram_percent}% | Số từ 'french': {count}")
        
        return len(chunk), count, processing_time
    except Exception as e:
        print(f"[Thread-{chunk_index}] Lỗi: {e}")
        return 0, 0, 0

def get_process_resources(pid=None):
    """Lấy thông tin tài nguyên của process (CPU, RAM)"""
    try:
        process = psutil.Process(pid)
        cpu_percent = process.cpu_percent(interval=0.1)  # % CPU
        memory_info = process.memory_info()  # RAM info (in bytes)
        memory_percent = (memory_info.rss / psutil.virtual_memory().total) * 100  # % RAM
        return cpu_percent, memory_percent
    except psutil.NoSuchProcess:
        return 0, 0

def read_and_process_csv(file_path, chunk_size, num_workers):
    total_count = 0
    total_rows = 0
    total_processing_time = 0

    start_time = time.time()

    with ThreadPoolExecutor(max_workers=num_workers) as executor:  # Sử dụng ThreadPoolExecutor
        futures = {}
        for chunk_index, chunk in enumerate(
            print("read từ disk lên ram")
            pd.read_csv(file_path, chunksize=chunk_size, usecols=['name', 'country'])
        ):
            try:
                # Gửi chunk tới executor
                future = executor.submit(process_chunk, chunk, chunk_index)
                futures[future] = chunk_index
            except Exception as e:
                print(f"Error while submitting chunk {chunk_index}: {e}")
                continue

        # Đợi kết quả từ tất cả các thread
        for future in as_completed(futures):
            chunk_index = futures[future]
            try:
                rows, count, processing_time = future.result()
                total_rows += rows
                total_count += count
                total_processing_time += processing_time
            except Exception as e:
                print(f"[Thread-{chunk_index}] Xử lý thất bại với lỗi: {e}")

    end_time = time.time()
    print(f"Tổng số dòng: {total_rows}, tổng số từ 'french': {total_count}")
    print(f"Tổng thời gian xử lý: {end_time - start_time:.2f} giây")
    print(f"Tổng thời gian thực tế của các chunks: {total_processing_time:.2f} giây")

# Thực thi
file_path = r"D:\Data Engineer\dwh and etl\lesson\lesson 2\documents\Talend\Sync Hadoop to DWH\citizens_data.csv"
chunk_size = 22_500_000  # Tăng kích thước chunk citizens_data.csv
num_workers = 4         # Sử dụng 6 luồng (threads) để chạy song song

read_and_process_csv(file_path, chunk_size, num_workers)
