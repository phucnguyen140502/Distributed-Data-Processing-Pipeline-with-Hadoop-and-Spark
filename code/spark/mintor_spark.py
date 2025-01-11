import psutil
import pandas as pd
import time
import os
from datetime import datetime
import subprocess

# Đường dẫn tới file CSV chung để lưu thông tin log
csv_file_path = "/home/hadoopuser/auto_resource_monitor_log.csv"

# Hàm ghi log tài nguyên hệ thống vào CSV
def log_system_resources(process_name, description, pid, core, thread_count, cpu_per_core, ram_usage, file_being_read, block_info):
    # Khởi tạo DataFrame để lưu thông tin CPU, RAM, tiến trình
    data = {
        "Timestamp": [],
        "Process_Name": [],
        "Process_Description": [],
        "PID": [],
        "CPU_Core": [],
        "Thread_Count": [],
        "CPU_Usage_Per_Core": [],
        "RAM_Usage(MB)": [],
        "Total_CPU_Usage(%)": [],
        "Total_RAM_Usage(%)": [],
        "File_Being_Read": [],
        "Block_Info": []
    }

    # Lặp qua để ghi thông số trong vòng 10 giây
    for _ in range(10):  
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cpu_usage_per_core = psutil.cpu_percent(interval=1, percpu=True)  # Mức độ sử dụng CPU theo từng core
        total_cpu_usage = psutil.cpu_percent(interval=1)  # Tổng mức độ sử dụng CPU
        ram_usage_per_process = psutil.Process(pid).memory_info().rss / (1024 * 1024)  # RAM sử dụng của tiến trình (MB)
        total_ram_usage = psutil.virtual_memory().percent  # Tổng mức sử dụng RAM của hệ thống

        # Thêm dữ liệu vào bảng
        data["Timestamp"].append(timestamp)
        data["Process_Name"].append(process_name)
        data["Process_Description"].append(description)
        data["PID"].append(pid)
        data["CPU_Core"].append(core)
        data["Thread_Count"].append(thread_count)
        data["CPU_Usage_Per_Core"].append(cpu_usage_per_core)  # Lưu thông tin CPU theo từng core
        data["RAM_Usage(MB)"].append(ram_usage_per_process)
        data["Total_CPU_Usage(%)"].append(total_cpu_usage)
        data["Total_RAM_Usage(%)"].append(total_ram_usage)
        data["File_Being_Read"].append(file_being_read)  # Lưu tên file đang đọc
        data["Block_Info"].append(block_info)  # Lưu thông tin block đang đọc

    # Chuyển DataFrame và ghi vào CSV với chế độ append
    df = pd.DataFrame(data)
    print("chuẩn bị ghi file")
    if os.path.exists(csv_file_path):
        df.to_csv(csv_file_path, mode="a", header=False, index=False)
    else:
        df.to_csv(csv_file_path, mode="w", header=True, index=False)

    print(f"Đã ghi log vào file {csv_file_path}.")

# Hàm kiểm tra xem file có phải HDFS không và lấy block
def get_hdfs_block_info(file_path):
    try:
        # Lệnh HDFS để lấy thông tin block của file
        hdfs_command = f"hdfs fs -stat %b {file_path}"
        block_info = subprocess.check_output(hdfs_command, shell=True).decode('utf-8').strip()
        return block_info
    except Exception as e:
        return "Không phải HDFS hoặc không thể lấy block"

# Hàm giám sát các tiến trình
def monitor_processes():
    print("Bắt đầu giám sát các tiến trình...")  # Được in ra khi hàm này bắt đầu chạy
    while True:
        for process in psutil.process_iter(attrs=["pid", "name", "cmdline", "cpu_num", "num_threads"]):
            try:
                process_name = process.info["name"]
                pid = process.info["pid"]
                core = process.info["cpu_num"]  # Số core của tiến trình
                thread_count = process.info["num_threads"]  # Số lượng threads của tiến trình

                # Kiểm tra cmdline và xử lý
                cmdline = process.info["cmdline"]
                
                print(process_name)
                print(cmdline)
                
                # Kiểm tra nếu cmdline là một iterable hợp lệ
                if cmdline is None:
                    cmdline = []  # Nếu không có cmdline, ta gán một danh sách trống để tránh lỗi
                elif not isinstance(cmdline, list):
                    cmdline = [cmdline]  # Nếu cmdline không phải là list, ta chuyển nó thành list

                # Lấy thông tin CPU sử dụng cho từng core
                cpu_per_core = psutil.cpu_percent(interval=1, percpu=True)

                # Kiểm tra nếu là tiến trình đọc file Python
                if process_name == "python" and "read_file" in " ".join(cmdline):
                    print("bắt đầu tiến trình với file .py")
                    # Lấy tên file và block đang được đọc từ cmdline
                    file_being_read = [arg for arg in cmdline if ".txt" in arg or ".csv" in arg or ".log" in arg]
                    file_path = file_being_read[0] if file_being_read else "N/A"
                    
                    # Kiểm tra nếu là file HDFS, lấy block
                    if "hdfs://" in file_path:
                        block_info = get_hdfs_block_info(file_path)
                    else:
                        block_info = "Không áp dụng block"

                    log_system_resources(process_name, "Đang đọc file lớn", pid, core, thread_count, cpu_per_core, 0, file_path, block_info)
                    # Sau khi hoàn thành, xuất file log ngay lập tức
                    continue  # Quay lại vòng lặp giám sát để tìm tiến trình tiếp theo

                # Kiểm tra nếu là tiến trình chạy lệnh SQL
                elif process_name == "psql":
                    log_system_resources(process_name, "Đang chạy lệnh SQL", pid, core, thread_count, cpu_per_core, 0, "N/A", "N/A")
                    # Sau khi hoàn thành, xuất file log ngay lập tức
                    continue  # Quay lại vòng lặp giám sát để tìm tiến trình tiếp theo

            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue

        # Nghỉ 5 giây trước khi kiểm tra tiếp
        time.sleep(5)

# Chạy giám sát

if not os.path.exists(os.path.dirname(csv_file_path)):
    print("Bắt đầu tạo thư mục cho log")  # Sẽ in ra khi thư mục chưa có
    os.makedirs(os.path.dirname(csv_file_path))  # Tạo thư mục lưu log nếu chưa tồn tại
else:
    print("Đã có file")  # Sẽ in ra khi thư mục đã tồn tại

print("Bắt đầu chạy monitor")
monitor_processes()
