from flask import Flask, jsonify
import psutil
from datetime import datetime, timedelta

app = Flask(__name__)

def get_uptime():
    """Return system uptime in human-readable format"""
    boot_time = datetime.fromtimestamp(psutil.boot_time())
    uptime = datetime.now() - boot_time
    return str(timedelta(seconds=int(uptime.total_seconds())))

def get_metrics():
    """Collect system metrics and return as dictionary"""
    # CPU
    cpu_usage = psutil.cpu_percent(interval=1)

    # Memory
    mem = psutil.virtual_memory()
    mem_usage = mem.percent

    # Disk
    disk = psutil.disk_usage('/')
    disk_usage = disk.percent

    # Network
    net_io = psutil.net_io_counters()
    net_stats = {
        "bytes_sent_mb": round(net_io.bytes_sent / (1024 * 1024), 2),
        "bytes_recv_mb": round(net_io.bytes_recv / (1024 * 1024), 2)
    }

    # Uptime
    uptime = get_uptime()

    # Top processes
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
        processes.append(proc.info)
    top_cpu = sorted(processes, key=lambda p: p['cpu_percent'], reverse=True)[:3]
    top_mem = sorted(processes, key=lambda p: p['memory_percent'], reverse=True)[:3]

    return {
        "cpu_usage": cpu_usage,
        "memory_usage": mem_usage,
        "disk_usage": disk_usage,
        "uptime": uptime,
        "network": net_stats,
        "top_processes_cpu": top_cpu,
        "top_processes_mem": top_mem
    }

@app.route('/metrics', methods=['GET'])
def metrics():
    """API endpoint to get system metrics"""
    return jsonify(get_metrics())

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
