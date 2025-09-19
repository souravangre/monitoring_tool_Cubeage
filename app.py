from flask import Flask, jsonify, render_template
import psutil
from datetime import datetime, timedelta

app = Flask(__name__)

def get_uptime():
    """Get system uptime"""
    try:
        boot_time = datetime.fromtimestamp(psutil.boot_time())
        uptime = datetime.now() - boot_time
        return str(timedelta(seconds=int(uptime.total_seconds())))
    except:
        return "Unknown"

def get_top_processes():
    """Get top 5 processes by CPU and Memory"""
    try:
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                pinfo = proc.info
                processes.append({
                    'pid': pinfo['pid'],
                    'name': pinfo['name'][:20],  # Truncate long names
                    'cpu_percent': round(pinfo['cpu_percent'], 1),
                    'memory_percent': round(pinfo['memory_percent'], 1)
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        
        # Sort by CPU and get top 5
        cpu_processes = sorted(processes, key=lambda x: x['cpu_percent'], reverse=True)[:5]
        # Sort by Memory and get top 5
        memory_processes = sorted(processes, key=lambda x: x['memory_percent'], reverse=True)[:5]
        
        return {
            'by_cpu': cpu_processes,
            'by_memory': memory_processes
        }
    except:
        return {'by_cpu': [], 'by_memory': []}

def get_metrics():
    """Get all system metrics"""
    try:
        # CPU Usage
        cpu_usage = psutil.cpu_percent(interval=1)
        
        # Memory Usage
        mem = psutil.virtual_memory()
        
        # Disk Usage (root partition)
        try:
            disk = psutil.disk_usage('/')
        except:
            # For Windows, try C: drive
            try:
                disk = psutil.disk_usage('C:')
            except:
                disk = None
        
        # Network I/O
        net_io = psutil.net_io_counters()
        
        # Top Processes
        processes = get_top_processes()
        
        return {
            "cpu": round(cpu_usage, 1),
            "memory": {
                "percent": round(mem.percent, 1),
                "used_gb": round(mem.used / (1024**3), 1),
                "total_gb": round(mem.total / (1024**3), 1)
            },
            "disk": {
                "percent": round((disk.used / disk.total) * 100, 1) if disk else 0,
                "used_gb": round(disk.used / (1024**3), 1) if disk else 0,
                "total_gb": round(disk.total / (1024**3), 1) if disk else 0
            },
            "uptime": get_uptime(),
            "network": {
                "sent_mb": round(net_io.bytes_sent / (1024 * 1024), 2),
                "recv_mb": round(net_io.bytes_recv / (1024 * 1024), 2),
                "sent_gb": round(net_io.bytes_sent / (1024**3), 2),
                "recv_gb": round(net_io.bytes_recv / (1024**3), 2)
            },
            "processes": processes,
            "timestamp": datetime.now().strftime("%H:%M:%S")
        }
    except Exception as e:
        print(f"Error getting metrics: {e}")
        return {
            "cpu": 0, "memory": {"percent": 0, "used_gb": 0, "total_gb": 0},
            "disk": {"percent": 0, "used_gb": 0, "total_gb": 0},
            "uptime": "Unknown", "network": {"sent_mb": 0, "recv_mb": 0, "sent_gb": 0, "recv_gb": 0},
            "processes": {"by_cpu": [], "by_memory": []}, "timestamp": "00:00:00"
        }

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')

@app.route('/api/metrics')
def api_metrics():
    """API endpoint for all metrics"""
    return jsonify(get_metrics())

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    print("🚀 Starting System Monitor...")
    print("📊 Dashboard: http://localhost:5000")
    print("🔌 API: http://localhost:5000/api/metrics")
    app.run(debug=True, host='0.0.0.0', port=5000)