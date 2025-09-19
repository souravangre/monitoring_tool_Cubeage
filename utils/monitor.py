import psutil
import time
import json
from datetime import datetime

def get_system_metrics():
    metrics = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),  # readable format
        "cpu_usage_percent": f"{psutil.cpu_percent(interval=1)}%",  # add %
        "memory_usage_percent": f"{psutil.virtual_memory().percent}%", 
        "disk_usage_percent": f"{psutil.disk_usage('/').percent}%",
        "network_io": {
            "bytes_sent_MB": f"{psutil.net_io_counters().bytes_sent / (1024*1024):.2f} MB",
            "bytes_recv_MB": f"{psutil.net_io_counters().bytes_recv / (1024*1024):.2f} MB"
        }
    }
    return metrics

if __name__ == "__main__":
    while True:
        data = get_system_metrics()
        print(json.dumps(data, indent=4))
        time.sleep(2)  # adjust refresh rate
