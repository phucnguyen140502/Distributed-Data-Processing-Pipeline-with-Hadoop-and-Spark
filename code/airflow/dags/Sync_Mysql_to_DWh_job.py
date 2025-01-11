from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
import requests
import logging

# Thiết lập thông số cho DAG
default_args = {
    'owner': 'airflow',
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Khởi tạo DAG
dag = DAG(
    'talend_job_dag_Sync_Mysql_to_DWh_job',
    default_args=default_args,
    description='DAG để chạy job Talend và thông báo qua Telegram',
    schedule_interval='0 8 * * *',
    start_date=datetime(2024, 10, 5),
)

# Hàm gửi thông báo qua Telegram
def send_telegram_message(message):
    TELEGRAM_BOT_TOKEN = "7156222811:AAE6ZMErEqxTXn9--NvylOfQDUNXP_uphp8"  # Lấy từ biến môi trường
    CHAT_ID = "-4560962078"  # Lấy từ biến môi trường
    if not TELEGRAM_BOT_TOKEN or not CHAT_ID:
        logging.error("Token Telegram hoặc Chat ID không được cung cấp!")
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {'chat_id': CHAT_ID, 'text': message}
    try:
        response = requests.post(url, data=payload)
        response.raise_for_status()  # Kiểm tra phản hồi HTTP
        logging.info(f"Gửi thành công: {response.json()}")
    except requests.exceptions.HTTPError as http_err:
        logging.error(f"HTTP error occurred: {http_err}")
    except Exception as err:
        logging.error(f"An error occurred: {err}")

# Task để chạy job Talend
run_talend_job = BashOperator(
    task_id='run_talend_job',
    bash_command='"/opt/Sync_Mysql_to_DWH_Job/run_Sync_Mysql_to_DWH_job.sh"',  # Đường dẫn trực tiếp
    dag=dag,
)

# Task để gửi thông báo thành công
def notify_success_callback(**context):
    task_instance = context['task_instance']
    message = (
        f"Job Talend trên Airflow đã chạy thành công!\n"
        f"Task: {task_instance.task_id}\n"
        f"Thời gian bắt đầu: {task_instance.start_date}\n"
        f"Thời gian kết thúc: {task_instance.end_date}\n"
        f"Execution Date: {task_instance.execution_date}\n"
    )
    send_telegram_message(message)

notify_success = PythonOperator(
    task_id='notify_success',
    python_callable=notify_success_callback,
    provide_context=True,
    dag=dag,
)

# Task để gửi thông báo thất bại
def notify_failure_callback(context):
    try:
        task_instance = context['task_instance']
        exception = context.get('exception', 'Không rõ lỗi')
        log_url = task_instance.log_url  # URL log của task
        message = (
            f"Job Talend đã thất bại!\n"
            f"Task: {task_instance.task_id}\n"
            f"Execution Date: {task_instance.execution_date}\n"
            f"Lỗi: {exception}\n"
            f"Thời gian bắt đầu: {task_instance.start_date}\n"
            f"Thời gian kết thúc: {task_instance.end_date}\n"
            f"Log URL: {log_url}\n"
        )
        send_telegram_message(message)
    except Exception as e:
        logging.error(f"Error in failure callback: {e}")

# Gán callback cho việc thất bại
run_talend_job.on_failure_callback = notify_failure_callback

# Xác định luồng công việc: Chạy job Talend trước, sau đó gửi thông báo thành công
run_talend_job >> notify_success
