#!/usr/bin/env python3
"""
Advanced System Health Monitoring GUI with Screenshot Export
Features: Real-time monitoring, visual dashboard, data export to JPEG
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import time
import platform
import subprocess
import psutil
from datetime import datetime, timedelta
from PIL import Image, ImageDraw, ImageFont
import os


class HealthStatus:
    """Health status levels and colors."""
    CRITICAL = "CRITICAL"
    WARNING = "WARNING"
    CAUTION = "CAUTION"
    HEALTHY = "HEALTHY"
    UNKNOWN = "UNKNOWN"
    
    # RGB Color codes
    COLOR_CRITICAL = "#FF4444"  # Red
    COLOR_WARNING = "#FFAA00"   # Orange
    COLOR_CAUTION = "#4488FF"   # Blue
    COLOR_HEALTHY = "#44AA44"   # Green
    COLOR_UNKNOWN = "#888888"   # Gray
    COLOR_NEUTRAL = "#FFFFFF"   # White
    COLOR_BG = "#1E1E1E"        # Dark background
    COLOR_TEXT = "#E0E0E0"      # Light text


class SystemHealthGUI:
    """GUI-based system health monitor with export capabilities."""
    
    THRESHOLDS = {
        'cpu_critical': 90, 'cpu_warning': 80, 'cpu_caution': 60,
        'memory_critical': 95, 'memory_warning': 85, 'memory_caution': 70,
        'disk_critical': 95, 'disk_warning': 85, 'disk_caution': 70,
        'temp_critical': 100, 'temp_warning': 85, 'temp_caution': 70,
        'battery_critical': 10, 'battery_warning': 20, 'battery_caution': 50,
    }
    
    def __init__(self, root):
        """Initialize the GUI."""
        self.root = root
        self.root.title("Advanced System Health Monitor")
        self.root.geometry("1400x900")
        self.root.configure(bg=HealthStatus.COLOR_BG)
        
        self.os_type = platform.system()
        self.prev_disk_io = psutil.disk_io_counters()
        self.prev_net_io = psutil.net_io_counters()
        self.prev_time = time.time()
        self.monitoring = False
        self.monitor_thread = None
        
        # Store current metrics for export
        self.current_metrics = {}
        
        self.setup_ui()
        self.start_monitoring()
    
    def setup_ui(self):
        """Setup the user interface."""
        # Top control panel
        control_frame = ttk.Frame(self.root)
        control_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(control_frame, text="System Health Monitor", font=("Arial", 16, "bold")).pack(side=tk.LEFT)
        
        self.status_label = ttk.Label(control_frame, text="Status: Initializing...", font=("Arial", 10))
        self.status_label.pack(side=tk.RIGHT, padx=5)
        
        button_frame = ttk.Frame(control_frame)
        button_frame.pack(side=tk.RIGHT, padx=5)
        
        ttk.Button(button_frame, text="Refresh", command=self.force_refresh).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Export as JPEG", command=self.export_to_jpeg).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Export as PNG", command=self.export_to_png).pack(side=tk.LEFT, padx=2)
        
        # Main content area with notebook (tabs)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create tabs
        self.create_overview_tab()
        self.create_cpu_tab()
        self.create_memory_tab()
        self.create_disk_tab()
        self.create_network_tab()
        self.create_battery_tab()
        self.create_system_tab()
    
    def create_overview_tab(self):
        """Create overview dashboard tab."""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Overview")
        
        # Create canvas for drawing
        self.overview_canvas = tk.Canvas(frame, bg=HealthStatus.COLOR_BG, highlightthickness=0, height=600)
        self.overview_canvas.pack(fill=tk.BOTH, expand=True)
    
    def create_cpu_tab(self):
        """Create CPU monitoring tab."""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="CPU")
        
        self.cpu_text = tk.Text(frame, bg=HealthStatus.COLOR_BG, fg=HealthStatus.COLOR_TEXT, 
                               font=("Courier", 10), height=30)
        self.cpu_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        scrollbar = ttk.Scrollbar(self.cpu_text)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.cpu_text.config(yscrollcommand=scrollbar.set)
    
    def create_memory_tab(self):
        """Create memory monitoring tab."""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Memory")
        
        self.memory_text = tk.Text(frame, bg=HealthStatus.COLOR_BG, fg=HealthStatus.COLOR_TEXT, 
                                  font=("Courier", 10), height=30)
        self.memory_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    def create_disk_tab(self):
        """Create disk monitoring tab."""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Disk")
        
        self.disk_text = tk.Text(frame, bg=HealthStatus.COLOR_BG, fg=HealthStatus.COLOR_TEXT, 
                                font=("Courier", 10), height=30)
        self.disk_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    def create_network_tab(self):
        """Create network monitoring tab."""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Network")
        
        self.network_text = tk.Text(frame, bg=HealthStatus.COLOR_BG, fg=HealthStatus.COLOR_TEXT, 
                                   font=("Courier", 10), height=30)
        self.network_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    def create_battery_tab(self):
        """Create battery monitoring tab."""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Battery")
        
        self.battery_text = tk.Text(frame, bg=HealthStatus.COLOR_BG, fg=HealthStatus.COLOR_TEXT, 
                                   font=("Courier", 10), height=30)
        self.battery_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    def create_system_tab(self):
        """Create system info tab."""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="System Info")
        
        self.system_text = tk.Text(frame, bg=HealthStatus.COLOR_BG, fg=HealthStatus.COLOR_TEXT, 
                                  font=("Courier", 10), height=30)
        self.system_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    def get_status_color(self, metric_type, value):
        """Get color based on health status."""
        if value is None:
            return HealthStatus.COLOR_UNKNOWN
        
        if metric_type == 'cpu':
            if value >= self.THRESHOLDS['cpu_critical']:
                return HealthStatus.COLOR_CRITICAL
            elif value >= self.THRESHOLDS['cpu_warning']:
                return HealthStatus.COLOR_WARNING
            elif value >= self.THRESHOLDS['cpu_caution']:
                return HealthStatus.COLOR_CAUTION
            return HealthStatus.COLOR_HEALTHY
        
        elif metric_type == 'memory' or metric_type == 'disk':
            if value >= self.THRESHOLDS[f'{metric_type}_critical']:
                return HealthStatus.COLOR_CRITICAL
            elif value >= self.THRESHOLDS[f'{metric_type}_warning']:
                return HealthStatus.COLOR_WARNING
            elif value >= self.THRESHOLDS[f'{metric_type}_caution']:
                return HealthStatus.COLOR_CAUTION
            return HealthStatus.COLOR_HEALTHY
        
        elif metric_type == 'temperature':
            if value >= self.THRESHOLDS['temp_critical']:
                return HealthStatus.COLOR_CRITICAL
            elif value >= self.THRESHOLDS['temp_warning']:
                return HealthStatus.COLOR_WARNING
            elif value >= self.THRESHOLDS['temp_caution']:
                return HealthStatus.COLOR_CAUTION
            return HealthStatus.COLOR_HEALTHY
        
        elif metric_type == 'battery':
            if value <= self.THRESHOLDS['battery_critical']:
                return HealthStatus.COLOR_CRITICAL
            elif value <= self.THRESHOLDS['battery_warning']:
                return HealthStatus.COLOR_WARNING
            elif value <= self.THRESHOLDS['battery_caution']:
                return HealthStatus.COLOR_CAUTION
            return HealthStatus.COLOR_HEALTHY
        
        return HealthStatus.COLOR_NEUTRAL
    
    def get_status_text(self, metric_type, value):
        """Get status text based on health."""
        if value is None:
            return "UNKNOWN"
        
        if metric_type == 'cpu':
            if value >= self.THRESHOLDS['cpu_critical']:
                return "CRITICAL"
            elif value >= self.THRESHOLDS['cpu_warning']:
                return "WARNING"
            elif value >= self.THRESHOLDS['cpu_caution']:
                return "CAUTION"
            return "HEALTHY"
        
        elif metric_type in ['memory', 'disk']:
            if value >= self.THRESHOLDS[f'{metric_type}_critical']:
                return "CRITICAL"
            elif value >= self.THRESHOLDS[f'{metric_type}_warning']:
                return "WARNING"
            elif value >= self.THRESHOLDS[f'{metric_type}_caution']:
                return "CAUTION"
            return "HEALTHY"
        
        elif metric_type == 'battery':
            if value <= self.THRESHOLDS['battery_critical']:
                return "CRITICAL"
            elif value <= self.THRESHOLDS['battery_warning']:
                return "WARNING"
            elif value <= self.THRESHOLDS['battery_caution']:
                return "CAUTION"
            return "HEALTHY"
        
        return "HEALTHY"
    
    def format_bytes(self, bytes_val):
        """Convert bytes to human-readable format."""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_val < 1024.0:
                return f"{bytes_val:.2f} {unit}"
            bytes_val /= 1024.0
        return f"{bytes_val:.2f} PB"
    
    def format_speed(self, bytes_per_sec):
        """Convert bytes/sec to human-readable format."""
        return f"{self.format_bytes(bytes_per_sec)}/s"
    
    def get_cpu_metrics(self):
        """Get CPU metrics."""
        cpu_percent = psutil.cpu_percent(interval=0.1, percpu=True)
        cpu_avg = psutil.cpu_percent(interval=0.1)
        cpu_freq = psutil.cpu_freq()
        
        try:
            temps = psutil.sensors_temperatures()
            temp = None
            if temps:
                for key in ['coretemp', 'acpitz']:
                    if key in temps:
                        temp = temps[key][0].current
                        break
        except:
            temp = None
        
        return {
            'average': cpu_avg,
            'per_core': cpu_percent,
            'frequency': cpu_freq.current if cpu_freq else None,
            'temperature': temp,
            'cores': psutil.cpu_count(logical=False),
            'threads': psutil.cpu_count(logical=True)
        }
    
    def get_memory_metrics(self):
        """Get memory metrics."""
        mem = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        return {
            'total': mem.total,
            'available': mem.available,
            'used': mem.used,
            'percent': mem.percent,
            'swap_total': swap.total,
            'swap_used': swap.used,
            'swap_percent': swap.percent
        }
    
    def get_disk_metrics(self):
        """Get disk metrics."""
        disk_path = 'C:\\' if os.name == 'nt' else '/'
        disk_usage = psutil.disk_usage(disk_path)
        
        current_disk_io = psutil.disk_io_counters()
        current_time = time.time()
        time_delta = current_time - self.prev_time
        
        disk_read_speed = (current_disk_io.read_bytes - self.prev_disk_io.read_bytes) / time_delta if time_delta > 0 else 0
        disk_write_speed = (current_disk_io.write_bytes - self.prev_disk_io.write_bytes) / time_delta if time_delta > 0 else 0
        
        self.prev_disk_io = current_disk_io
        
        return {
            'total': disk_usage.total,
            'used': disk_usage.used,
            'free': disk_usage.free,
            'percent': disk_usage.percent,
            'read_speed': disk_read_speed,
            'write_speed': disk_write_speed
        }
    
    def get_network_metrics(self):
        """Get network metrics."""
        current_net_io = psutil.net_io_counters()
        current_time = time.time()
        time_delta = current_time - self.prev_time
        
        upload_speed = (current_net_io.bytes_sent - self.prev_net_io.bytes_sent) / time_delta if time_delta > 0 else 0
        download_speed = (current_net_io.bytes_recv - self.prev_net_io.bytes_recv) / time_delta if time_delta > 0 else 0
        
        self.prev_net_io = current_net_io
        
        return {
            'upload_speed': upload_speed,
            'download_speed': download_speed
        }
    
    def get_battery_metrics(self):
        """Get battery metrics."""
        try:
            battery = psutil.sensors_battery()
            if battery:
                return {
                    'percent': battery.percent,
                    'is_charging': battery.power_plugged,
                    'time_left': battery.secsleft
                }
        except:
            pass
        
        return {'percent': None, 'is_charging': None, 'time_left': None}
    
    def update_overview(self):
        """Update overview tab with dashboard."""
        self.overview_canvas.delete("all")
        
        cpu = self.get_cpu_metrics()
        mem = self.get_memory_metrics()
        disk = self.get_disk_metrics()
        net = self.get_network_metrics()
        battery = self.get_battery_metrics()
        
        width = self.overview_canvas.winfo_width()
        height = self.overview_canvas.winfo_height()
        
        if width < 2 or height < 2:
            width, height = 1400, 600
        
        # Title
        self.overview_canvas.create_text(width // 2, 30, text="SYSTEM HEALTH OVERVIEW",
                                        font=("Arial", 20, "bold"), fill=HealthStatus.COLOR_TEXT)
        self.overview_canvas.create_text(width // 2, 60, text=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                        font=("Arial", 10), fill=HealthStatus.COLOR_TEXT)
        
        # Draw metric boxes
        box_width = 250
        box_height = 140
        x_start = 50
        y_start = 100
        spacing = 30
        
        metrics = [
            ("CPU", f"{cpu['average']:.1f}%", 'cpu', cpu['average']),
            ("Memory", f"{mem['percent']:.1f}%", 'memory', mem['percent']),
            ("Disk", f"{disk['percent']:.1f}%", 'disk', disk['percent']),
            ("Temp", f"{cpu['temperature']:.1f}°C" if cpu['temperature'] else "N/A", 'temperature', cpu['temperature']),
        ]
        
        col = 0
        for metric_name, metric_value, metric_type, metric_num in metrics:
            x = x_start + col * (box_width + spacing)
            y = y_start
            
            color = self.get_status_color(metric_type, metric_num)
            status = self.get_status_text(metric_type, metric_num)
            
            # Draw box
            self.overview_canvas.create_rectangle(x, y, x + box_width, y + box_height,
                                                 fill=HealthStatus.COLOR_BG, outline=color, width=3)
            
            # Draw text
            self.overview_canvas.create_text(x + box_width // 2, y + 30, text=metric_name,
                                            font=("Arial", 14, "bold"), fill=HealthStatus.COLOR_TEXT)
            self.overview_canvas.create_text(x + box_width // 2, y + 60, text=metric_value,
                                            font=("Arial", 18, "bold"), fill=color)
            self.overview_canvas.create_text(x + box_width // 2, y + 90, text=status,
                                            font=("Arial", 10), fill=color)
            
            col += 1
        
        # Battery section
        if battery['percent'] is not None:
            x = x_start + 4 * (box_width + spacing)
            y = y_start
            color = self.get_status_color('battery', battery['percent'])
            status = self.get_status_text('battery', battery['percent'])
            
            self.overview_canvas.create_rectangle(x, y, x + box_width, y + box_height,
                                                 fill=HealthStatus.COLOR_BG, outline=color, width=3)
            self.overview_canvas.create_text(x + box_width // 2, y + 30, text="Battery",
                                            font=("Arial", 14, "bold"), fill=HealthStatus.COLOR_TEXT)
            self.overview_canvas.create_text(x + box_width // 2, y + 60, text=f"{battery['percent']:.1f}%",
                                            font=("Arial", 18, "bold"), fill=color)
            
            charging = "Charging" if battery['is_charging'] else "Discharging"
            self.overview_canvas.create_text(x + box_width // 2, y + 90, text=charging,
                                            font=("Arial", 10), fill=HealthStatus.COLOR_TEXT)
        
        # Network info
        y_net = y_start + box_height + spacing + 50
        self.overview_canvas.create_text(x_start, y_net, text="NETWORK",
                                        font=("Arial", 14, "bold"), fill=HealthStatus.COLOR_TEXT, anchor="w")
        self.overview_canvas.create_text(x_start, y_net + 30, 
                                        text=f"Download: {self.format_speed(net['download_speed'])} | Upload: {self.format_speed(net['upload_speed'])}",
                                        font=("Arial", 12), fill=HealthStatus.COLOR_TEXT, anchor="w")
        
        # System info
        y_sys = y_net + 80
        boot_time = datetime.fromtimestamp(psutil.boot_time())
        uptime = datetime.now() - boot_time
        uptime_str = f"{uptime.days}d {uptime.seconds // 3600}h {(uptime.seconds % 3600) // 60}m"
        
        self.overview_canvas.create_text(x_start, y_sys, text="SYSTEM",
                                        font=("Arial", 14, "bold"), fill=HealthStatus.COLOR_TEXT, anchor="w")
        self.overview_canvas.create_text(x_start, y_sys + 30,
                                        text=f"OS: {self.os_type} | Uptime: {uptime_str}",
                                        font=("Arial", 12), fill=HealthStatus.COLOR_TEXT, anchor="w")
    
    def update_cpu_tab(self):
        """Update CPU information tab."""
        self.cpu_text.config(state=tk.NORMAL)
        self.cpu_text.delete(1.0, tk.END)
        
        cpu = self.get_cpu_metrics()
        status = self.get_status_text('cpu', cpu['average'])
        freq_text = f"{cpu['frequency']:.2f} MHz" if cpu['frequency'] else "N/A"
        temp_text = f"{cpu['temperature']:.2f}°C" if cpu['temperature'] else "N/A"
        
        text = f"""
╔══════════════════════════════════════════════════════════════╗
║                    CPU MONITORING                            ║
╚══════════════════════════════════════════════════════════════╝

Status:              {status}
Average Usage:       {cpu['average']:.2f}%
CPU Cores:           {cpu['cores']}
Logical Threads:     {cpu['threads']}
Frequency:           {freq_text}
Temperature:         {temp_text}

Per-Core Usage:
────────────────────────────────────────────────────────────────
"""
        for i, core in enumerate(cpu['per_core']):
            bar_length = int(core / 5)
            bar = '█' * bar_length + '░' * (20 - bar_length)
            text += f"Core {i:2d}: {bar} {core:6.2f}%\n"
        
        text += f"""
────────────────────────────────────────────────────────────────

Health Thresholds:
  • Healthy:   0-{self.THRESHOLDS['cpu_caution']}%
  • Caution:   {self.THRESHOLDS['cpu_caution']}-{self.THRESHOLDS['cpu_warning']}%
  • Warning:   {self.THRESHOLDS['cpu_warning']}-{self.THRESHOLDS['cpu_critical']}%
  • Critical:  {self.THRESHOLDS['cpu_critical']}%+
"""
        
        self.cpu_text.insert(1.0, text)
        self.cpu_text.config(state=tk.DISABLED)
    
    def update_memory_tab(self):
        """Update Memory information tab."""
        self.memory_text.config(state=tk.NORMAL)
        self.memory_text.delete(1.0, tk.END)
        
        mem = self.get_memory_metrics()
        status = self.get_status_text('memory', mem['percent'])
        
        ram_bar = int(mem['percent'] / 5)
        swap_bar = int(mem['swap_percent'] / 5)
        
        text = f"""
╔══════════════════════════════════════════════════════════════╗
║                   MEMORY MONITORING                          ║
╚══════════════════════════════════════════════════════════════╝

Status:              {status}
RAM Usage:           {mem['percent']:.2f}%
Swap Usage:          {mem['swap_percent']:.2f}%

RAM Details:
────────────────────────────────────────────────────────────────
Total:               {self.format_bytes(mem['total'])}
Used:                {self.format_bytes(mem['used'])} ({mem['percent']:.1f}%)
Available:           {self.format_bytes(mem['available'])}

Visual:              {'█' * ram_bar}{'░' * (20 - ram_bar)}

SWAP Details:
────────────────────────────────────────────────────────────────
Total:               {self.format_bytes(mem['swap_total'])}
Used:                {self.format_bytes(mem['swap_used'])} ({mem['swap_percent']:.1f}%)

Visual:              {'█' * swap_bar}{'░' * (20 - swap_bar)}

Health Thresholds:
  • Healthy:   0-{self.THRESHOLDS['memory_caution']}%
  • Caution:   {self.THRESHOLDS['memory_caution']}-{self.THRESHOLDS['memory_warning']}%
  • Warning:   {self.THRESHOLDS['memory_warning']}-{self.THRESHOLDS['memory_critical']}%
  • Critical:  {self.THRESHOLDS['memory_critical']}%+

Recommendations:
  • Close unnecessary applications
  • Clear temporary files
  • Monitor for memory leaks
"""
        
        self.memory_text.insert(1.0, text)
        self.memory_text.config(state=tk.DISABLED)
    
    def update_disk_tab(self):
        """Update Disk information tab."""
        self.disk_text.config(state=tk.NORMAL)
        self.disk_text.delete(1.0, tk.END)
        
        disk = self.get_disk_metrics()
        status = self.get_status_text('disk', disk['percent'])
        
        disk_bar = int(disk['percent'] / 5)
        
        text = f"""
╔══════════════════════════════════════════════════════════════╗
║                   DISK MONITORING                            ║
╚══════════════════════════════════════════════════════════════╝

Status:              {status}
Disk Usage:          {disk['percent']:.2f}%

Capacity Details:
────────────────────────────────────────────────────────────────
Total:               {self.format_bytes(disk['total'])}
Used:                {self.format_bytes(disk['used'])} ({disk['percent']:.1f}%)
Free:                {self.format_bytes(disk['free'])}

Visual:              {'█' * disk_bar}{'░' * (20 - disk_bar)}

I/O Performance:
────────────────────────────────────────────────────────────────
Read Speed:          {self.format_speed(disk['read_speed'])}
Write Speed:         {self.format_speed(disk['write_speed'])}

Health Thresholds:
  • Healthy:   0-{self.THRESHOLDS['disk_caution']}%
  • Caution:   {self.THRESHOLDS['disk_caution']}-{self.THRESHOLDS['disk_warning']}%
  • Warning:   {self.THRESHOLDS['disk_warning']}-{self.THRESHOLDS['disk_critical']}%
  • Critical:  {self.THRESHOLDS['disk_critical']}%+

Recommendations:
  • Delete unnecessary files
  • Empty Recycle Bin
  • Run disk cleanup
  • Move data to external storage
"""
        
        self.disk_text.insert(1.0, text)
        self.disk_text.config(state=tk.DISABLED)
    
    def update_network_tab(self):
        """Update Network information tab."""
        self.network_text.config(state=tk.NORMAL)
        self.network_text.delete(1.0, tk.END)
        
        net = self.get_network_metrics()
        
        text = f"""
╔══════════════════════════════════════════════════════════════╗
║                  NETWORK MONITORING                          ║
╚══════════════════════════════════════════════════════════════╝

Real-Time Speeds:
────────────────────────────────────────────────────────────────
Download:            {self.format_speed(net['download_speed'])}
Upload:              {self.format_speed(net['upload_speed'])}

Network Interfaces:
────────────────────────────────────────────────────────────────
"""
        
        try:
            interfaces = psutil.net_if_stats()
            for name, stat in interfaces.items():
                status = "UP" if stat.isup else "DOWN"
                text += f"{name:20} Status: {status:6} MTU: {stat.mtu}\n"
        except:
            text += "Unable to retrieve interface information\n"
        
        text += """
Recommendations:
  • Monitor bandwidth usage
  • Check for network congestion
  • Verify stable connections
"""
        
        self.network_text.insert(1.0, text)
        self.network_text.config(state=tk.DISABLED)
    
    def update_battery_tab(self):
        """Update Battery information tab."""
        self.battery_text.config(state=tk.NORMAL)
        self.battery_text.delete(1.0, tk.END)
        
        battery = self.get_battery_metrics()
        
        if battery['percent'] is None:
            text = """
╔══════════════════════════════════════════════════════════════╗
║                  BATTERY INFORMATION                         ║
╚══════════════════════════════════════════════════════════════╝

No battery detected - Desktop system
"""
        else:
            status = self.get_status_text('battery', battery['percent'])
            charging_status = "Charging" if battery['is_charging'] else "Discharging"
            battery_bar = int(battery['percent'] / 5)
            
            time_left = ""
            if battery['time_left'] != psutil.POWER_TIME_UNLIMITED and battery['time_left'] != psutil.POWER_TIME_UNKNOWN:
                time_left_delta = timedelta(seconds=int(battery['time_left']))
                time_left = f"\nTime Remaining:      {time_left_delta}"
            
            text = f"""
╔══════════════════════════════════════════════════════════════╗
║                  BATTERY INFORMATION                         ║
╚══════════════════════════════════════════════════════════════╝

Status:              {status}
Charge Level:        {battery['percent']:.1f}%
Charging Status:     {charging_status}{time_left}

Visual:              {'█' * battery_bar}{'░' * (20 - battery_bar)}

Health Thresholds:
  • Healthy:   >{self.THRESHOLDS['battery_caution']}%
  • Caution:   {self.THRESHOLDS['battery_warning']}-{self.THRESHOLDS['battery_caution']}%
  • Warning:   {self.THRESHOLDS['battery_critical']}-{self.THRESHOLDS['battery_warning']}%
  • Critical:  <{self.THRESHOLDS['battery_critical']}%

Recommendations:
  • Connect power adapter if needed
  • Enable power saving mode for low battery
  • Check charger if not charging properly
"""
        
        self.battery_text.insert(1.0, text)
        self.battery_text.config(state=tk.DISABLED)
    
    def update_system_tab(self):
        """Update System information tab."""
        self.system_text.config(state=tk.NORMAL)
        self.system_text.delete(1.0, tk.END)
        
        boot_time = datetime.fromtimestamp(psutil.boot_time())
        uptime = datetime.now() - boot_time
        uptime_str = f"{uptime.days}d {uptime.seconds // 3600}h {(uptime.seconds % 3600) // 60}m"
        
        text = f"""
╔══════════════════════════════════════════════════════════════╗
║                   SYSTEM INFORMATION                         ║
╚══════════════════════════════════════════════════════════════╝

System Details:
────────────────────────────────────────────────────────────────
Hostname:            {platform.node()}
Operating System:    {platform.system()} {platform.release()}
Architecture:        {platform.architecture()[0]}
Processor:           {platform.processor()}

Uptime Information:
────────────────────────────────────────────────────────────────
Last Boot:           {boot_time.strftime('%Y-%m-%d %H:%M:%S')}
Current Uptime:      {uptime_str}

System Resources:
────────────────────────────────────────────────────────────────
Total Processes:     {len(psutil.pids())}
CPU Cores:           {psutil.cpu_count(logical=False)}
Logical CPUs:        {psutil.cpu_count(logical=True)}

Boot Disk:           C:\\  (Windows) or  /  (Unix-like)

Mounted Partitions:
────────────────────────────────────────────────────────────────
"""
        
        try:
            partitions = psutil.disk_partitions()
            for partition in partitions:
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    text += f"{partition.device:20} {partition.mountpoint:20} {self.format_bytes(usage.total):>15}\n"
                except:
                    pass
        except:
            text += "Unable to retrieve partition information\n"
        
        text += f"""
System Monitoring:
────────────────────────────────────────────────────────────────
Monitor Update Interval:  15 seconds
Last Updated:            {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Note: This system health monitor provides real-time diagnostics
of your system's performance and health status. Use the export
feature to save reports for future reference.
"""
        
        self.system_text.insert(1.0, text)
        self.system_text.config(state=tk.DISABLED)
    
    def update_all_tabs(self):
        """Update all tabs with current information."""
        self.update_overview()
        self.update_cpu_tab()
        self.update_memory_tab()
        self.update_disk_tab()
        self.update_network_tab()
        self.update_battery_tab()
        self.update_system_tab()
    
    def monitor_loop(self):
        """Continuous monitoring loop."""
        self.monitoring = True
        while self.monitoring:
            try:
                self.root.after(0, self.update_all_tabs)
                self.root.after(0, lambda: self.status_label.config(
                    text=f"Status: Active | Last Update: {datetime.now().strftime('%H:%M:%S')}"
                ))
                time.sleep(15)
            except Exception as e:
                print(f"Monitoring error: {e}")
                break
    
    def start_monitoring(self):
        """Start the monitoring thread."""
        self.monitor_thread = threading.Thread(target=self.monitor_loop, daemon=True)
        self.monitor_thread.start()
        self.update_all_tabs()
    
    def force_refresh(self):
        """Force an immediate refresh of all tabs."""
        self.update_all_tabs()
        messagebox.showinfo("Refresh", "System data refreshed successfully!")
    
    def export_to_jpeg(self):
        """Export current dashboard as JPEG."""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".jpg",
            filetypes=[("JPEG files", "*.jpg"), ("All files", "*.*")],
            initialfile=f"system_health_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        )
        
        if file_path:
            try:
                self._save_dashboard_image(file_path, "JPEG")
                messagebox.showinfo("Export Success", f"Dashboard exported to:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export: {str(e)}")
    
    def export_to_png(self):
        """Export current dashboard as PNG."""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")],
            initialfile=f"system_health_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        )
        
        if file_path:
            try:
                self._save_dashboard_image(file_path, "PNG")
                messagebox.showinfo("Export Success", f"Dashboard exported to:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export: {str(e)}")
    
    def _save_dashboard_image(self, file_path, image_format):
        """Save dashboard as image file."""
        # Collect current metrics
        cpu = self.get_cpu_metrics()
        mem = self.get_memory_metrics()
        disk = self.get_disk_metrics()
        net = self.get_network_metrics()
        battery = self.get_battery_metrics()
        
        boot_time = datetime.fromtimestamp(psutil.boot_time())
        uptime = datetime.now() - boot_time
        uptime_str = f"{uptime.days}d {uptime.seconds // 3600}h"
        
        # Create image
        img_width = 1600
        img_height = 1200
        img = Image.new('RGB', (img_width, img_height), color=(30, 30, 30))
        draw = ImageDraw.Draw(img)
        
        try:
            title_font = ImageFont.truetype("arial.ttf", 40)
            header_font = ImageFont.truetype("arial.ttf", 24)
            text_font = ImageFont.truetype("arial.ttf", 18)
            small_font = ImageFont.truetype("arial.ttf", 14)
        except:
            title_font = ImageFont.load_default()
            header_font = ImageFont.load_default()
            text_font = ImageFont.load_default()
            small_font = ImageFont.load_default()
        
        y_pos = 40
        text_color = (224, 224, 224)
        
        # Title
        draw.text((40, y_pos), "SYSTEM HEALTH MONITOR REPORT", font=title_font, fill=text_color)
        y_pos += 60
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        draw.text((40, y_pos), f"Generated: {timestamp}", font=small_font, fill=text_color)
        y_pos += 40
        
        # Draw separator
        draw.line([(40, y_pos), (img_width - 40, y_pos)], fill=(100, 100, 100), width=2)
        y_pos += 30
        
        # CPU Section
        draw.text((40, y_pos), "CPU INFORMATION", font=header_font, fill=(68, 170, 68))
        y_pos += 35
        draw.text((60, y_pos), f"Average Usage: {cpu['average']:.1f}%", font=text_font, fill=text_color)
        y_pos += 28
        draw.text((60, y_pos), f"Cores: {cpu['cores']} | Threads: {cpu['threads']} | Frequency: {cpu['frequency']:.2f} MHz", 
                 font=text_font, fill=text_color)
        y_pos += 28
        if cpu['temperature']:
            draw.text((60, y_pos), f"Temperature: {cpu['temperature']:.1f}°C", font=text_font, fill=text_color)
        y_pos += 35
        
        # Memory Section
        draw.text((40, y_pos), "MEMORY INFORMATION", font=header_font, fill=(68, 170, 68))
        y_pos += 35
        draw.text((60, y_pos), f"RAM Usage: {mem['percent']:.1f}% | Used: {self.format_bytes(mem['used'])} / {self.format_bytes(mem['total'])}", 
                 font=text_font, fill=text_color)
        y_pos += 28
        draw.text((60, y_pos), f"SWAP Usage: {mem['swap_percent']:.1f}% | Used: {self.format_bytes(mem['swap_used'])} / {self.format_bytes(mem['swap_total'])}", 
                 font=text_font, fill=text_color)
        y_pos += 35
        
        # Disk Section
        draw.text((40, y_pos), "DISK INFORMATION", font=header_font, fill=(68, 170, 68))
        y_pos += 35
        draw.text((60, y_pos), f"Disk Usage: {disk['percent']:.1f}% | Used: {self.format_bytes(disk['used'])} / {self.format_bytes(disk['total'])}", 
                 font=text_font, fill=text_color)
        y_pos += 28
        draw.text((60, y_pos), f"Free Space: {self.format_bytes(disk['free'])} | Read: {self.format_speed(disk['read_speed'])} | Write: {self.format_speed(disk['write_speed'])}", 
                 font=text_font, fill=text_color)
        y_pos += 35
        
        # Network Section
        draw.text((40, y_pos), "NETWORK INFORMATION", font=header_font, fill=(68, 170, 68))
        y_pos += 35
        draw.text((60, y_pos), f"Download: {self.format_speed(net['download_speed'])} | Upload: {self.format_speed(net['upload_speed'])}", 
                 font=text_font, fill=text_color)
        y_pos += 35
        
        # Battery Section (if available)
        if battery['percent'] is not None:
            draw.text((40, y_pos), "BATTERY INFORMATION", font=header_font, fill=(68, 170, 68))
            y_pos += 35
            charging = "Charging" if battery['is_charging'] else "Discharging"
            draw.text((60, y_pos), f"Battery Level: {battery['percent']:.1f}% | Status: {charging}", 
                     font=text_font, fill=text_color)
            y_pos += 35
        
        # System Info Section
        draw.text((40, y_pos), "SYSTEM INFORMATION", font=header_font, fill=(68, 170, 68))
        y_pos += 35
        draw.text((60, y_pos), f"Hostname: {platform.node()} | OS: {self.os_type}", 
                 font=text_font, fill=text_color)
        y_pos += 28
        draw.text((60, y_pos), f"Uptime: {uptime_str} | Boot Time: {boot_time.strftime('%Y-%m-%d %H:%M:%S')}", 
                 font=text_font, fill=text_color)
        y_pos += 35
        
        # Footer
        draw.line([(40, img_height - 80), (img_width - 40, img_height - 80)], fill=(100, 100, 100), width=2)
        draw.text((40, img_height - 50), "Advanced System Health Monitor - Enterprise Edition", 
                 font=small_font, fill=(150, 150, 150))
        draw.text((img_width - 40, img_height - 50), "Comprehensive System Diagnostics", 
                 font=small_font, fill=(150, 150, 150), anchor="rm")
        
        # Save image
        if image_format == "JPEG":
            img.save(file_path, "JPEG", quality=95)
        else:
            img.save(file_path, "PNG")
    
    def on_closing(self):
        """Handle window closing."""
        self.monitoring = False
        self.root.destroy()


def main():
    """Main entry point."""
    root = tk.Tk()
    
    # Configure style
    style = ttk.Style()
    style.theme_use('clam')
    
    # Customize colors
    style.configure('TFrame', background=HealthStatus.COLOR_BG)
    style.configure('TLabel', background=HealthStatus.COLOR_BG, foreground=HealthStatus.COLOR_TEXT)
    style.configure('TButton', background=HealthStatus.COLOR_BG, foreground=HealthStatus.COLOR_TEXT)
    style.configure('TNotebook', background=HealthStatus.COLOR_BG)
    style.configure('TNotebook.Tab', padding=[20, 10])
    
    gui = SystemHealthGUI(root)
    root.protocol("WM_DELETE_WINDOW", gui.on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()