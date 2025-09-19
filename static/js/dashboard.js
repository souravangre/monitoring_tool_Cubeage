// Minimal System Monitor Dashboard

class SystemMonitor {
    constructor() {
        this.updateInterval = 3000; // 3 seconds
        this.intervalId = null;
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.fetchMetrics();
        this.startAutoUpdate();
    }

    setupEventListeners() {
        // Refresh button
        const refreshBtn = document.getElementById('refresh-btn');
        refreshBtn.addEventListener('click', () => {
            this.fetchMetrics();
            this.animateRefreshButton(refreshBtn);
        });

        // Pause updates when tab is hidden
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                this.stopAutoUpdate();
            } else {
                this.startAutoUpdate();
                this.fetchMetrics();
            }
        });
    }

    animateRefreshButton(button) {
        const icon = button.querySelector('i');
        icon.classList.add('fa-spin');
        setTimeout(() => icon.classList.remove('fa-spin'), 1000);
    }

    async fetchMetrics() {
        try {
            this.showLoading(true);
            
            const response = await fetch('/api/metrics');
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            
            const data = await response.json();
            this.updateUI(data);
            this.updateLastUpdate(data.timestamp);
            
        } catch (error) {
            console.error('Error fetching metrics:', error);
            this.showError('Failed to load metrics');
        } finally {
            this.showLoading(false);
        }
    }

    updateUI(data) {
        // Update CPU
        this.updateMetricCard('cpu-usage', `${data.cpu}%`, data.cpu);
        this.updateProgressBar('cpu-progress', data.cpu);

        // Update Memory
        this.updateMetricCard('memory-usage', `${data.memory.percent}%`, data.memory.percent);
        this.updateElement('memory-details', `${data.memory.used_gb}GB / ${data.memory.total_gb}GB`);
        this.updateProgressBar('memory-progress', data.memory.percent);

        // Update Disk
        this.updateMetricCard('disk-usage', `${data.disk.percent}%`, data.disk.percent);
        this.updateElement('disk-details', `${data.disk.used_gb}GB / ${data.disk.total_gb}GB`);
        this.updateProgressBar('disk-progress', data.disk.percent);

        // Update Uptime
        this.updateElement('uptime', data.uptime);

        // Update Network
        this.updateNetworkStats(data.network);

        // Update Process Tables
        this.updateProcessTable('cpu-processes', data.processes.by_cpu, 'cpu');
        this.updateProcessTable('memory-processes', data.processes.by_memory, 'memory');
    }

    updateMetricCard(elementId, value, percentage) {
        const element = document.getElementById(elementId);
        if (element) {
            element.textContent = value;
            element.className = `metric-value ${this.getStatusClass(percentage)}`;
        }
    }

    updateElement(elementId, value) {
        const element = document.getElementById(elementId);
        if (element) {
            element.textContent = value;
        }
    }

    updateProgressBar(elementId, percentage) {
        const progressBar = document.getElementById(elementId);
        if (progressBar) {
            progressBar.style.width = `${percentage}%`;
            progressBar.className = `progress-bar ${this.getProgressBarClass(percentage)}`;
        }
    }

    updateNetworkStats(network) {
        // Use appropriate unit (MB or GB)
        const downloadValue = network.recv_gb > 1 ? `${network.recv_gb} GB` : `${network.recv_mb} MB`;
        const uploadValue = network.sent_gb > 1 ? `${network.sent_gb} GB` : `${network.sent_mb} MB`;

        this.updateElement('network-download', downloadValue);
        this.updateElement('network-upload', uploadValue);
    }

    updateProcessTable(tableId, processes, type) {
        const tbody = document.getElementById(tableId);
        if (!tbody) return;

        if (processes.length === 0) {
            tbody.innerHTML = '<tr><td colspan="3" class="text-center text-muted">No processes found</td></tr>';
            return;
        }

        tbody.innerHTML = processes.map(proc => `
            <tr>
                <td class="process-name" title="${proc.name}">${proc.name}</td>
                <td><code>${proc.pid}</code></td>
                <td>
                    <span class="badge bg-${this.getProcessBadgeColor(type === 'cpu' ? proc.cpu_percent : proc.memory_percent)}">
                        ${type === 'cpu' ? proc.cpu_percent : proc.memory_percent}%
                    </span>
                </td>
            </tr>
        `).join('');
    }

    getStatusClass(percentage) {
        if (percentage < 60) return 'text-success';
        if (percentage < 80) return 'text-warning';
        return 'text-danger';
    }

    getProgressBarClass(percentage) {
        if (percentage < 60) return 'bg-success';
        if (percentage < 80) return 'bg-warning';
        return 'bg-danger';
    }

    getProcessBadgeColor(percentage) {
        if (percentage < 20) return 'success';
        if (percentage < 50) return 'warning';
        return 'danger';
    }

    updateLastUpdate(timestamp) {
        const element = document.getElementById('last-update');
        if (element) {
            element.innerHTML = `<i class="fas fa-clock me-1"></i>Last: ${timestamp}`;
        }
    }

    showLoading(show) {
        const loading = document.getElementById('loading');
        if (loading) {
            loading.classList.toggle('d-none', !show);
        }
    }

    showError(message) {
        // Simple error notification
        const alert = document.createElement('div');
        alert.className = 'alert alert-danger alert-dismissible fade show position-fixed';
        alert.style.cssText = 'top: 20px; right: 20px; z-index: 10000; min-width: 300px;';
        alert.innerHTML = `
            <i class="fas fa-exclamation-triangle me-2"></i>${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        document.body.appendChild(alert);

        // Auto remove after 5 seconds
        setTimeout(() => {
            if (alert.parentNode) {
                alert.remove();
            }
        }, 5000);
    }

    startAutoUpdate() {
        if (this.intervalId) {
            clearInterval(this.intervalId);
        }
        
        this.intervalId = setInterval(() => {
            this.fetchMetrics();
        }, this.updateInterval);
    }

    stopAutoUpdate() {
        if (this.intervalId) {
            clearInterval(this.intervalId);
            this.intervalId = null;
        }
    }

    // Change update interval
    setUpdateInterval(milliseconds) {
        this.updateInterval = milliseconds;
        if (this.intervalId) {
            this.stopAutoUpdate();
            this.startAutoUpdate();
        }
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    const monitor = new SystemMonitor();
    
    // Make available globally for debugging
    window.systemMonitor = monitor;
    
    // Keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + R: Refresh
        if ((e.ctrlKey || e.metaKey) && e.key === 'r') {
            e.preventDefault();
            monitor.fetchMetrics();
        }
    });

    console.log('🚀 System Monitor initialized');
});