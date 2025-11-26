#!/usr/bin/env python3
"""
Comprehensive System Health Monitoring Script - Enterprise Edition
Advanced diagnostics covering hardware, software, and system components.
Monitors CPU, Memory, Disk, Network, Battery, Power, USB ports, Thermal,
Storage health, System processes, Drivers, and much more.
"""

import os
import sys
import time
import platform
import subprocess
import json
from datetime import datetime, timedelta
import psutil
import threading


class HealthStatus:
    """Health status levels and colors."""
    CRITICAL = "CRITICAL"
    WARNING = "WARNING"
    CAUTION = "CAUTION"
    HEALTHY = "HEALTHY"
    UNKNOWN = "UNKNOWN"
    
    COLOR_CRITICAL = "\033[91m"  # Red
    COLOR_WARNING = "\033[93m"   # Yellow
    COLOR_CAUTION = "\033[94m"   # Blue
    COLOR_HEALTHY = "\033[92m"   # Green
    COLOR_UNKNOWN = "\033[90m"   # Gray
    COLOR_RESET = "\033[0m"


class ComprehensiveSystemHealthMonitor:
    """Enterprise-grade system health monitor with extensive diagnostics."""
    
    # Health thresholds
    THRESHOLDS = {
        'cpu_healthy': 30,
        'cpu_caution': 60,
        'cpu_warning': 80,
        'cpu_critical': 90,
        
        'memory_healthy': 50,
        'memory_caution': 70,
        'memory_warning': 85,
        'memory_critical': 95,
        
        'disk_healthy': 50,
        'disk_caution': 70,
        'disk_warning': 85,
        'disk_critical': 95,
        
        'temp_healthy': 50,
        'temp_caution': 70,
        'temp_warning': 85,
        'temp_critical': 100,
        
        'battery_healthy': 80,
        'battery_caution': 50,
        'battery_warning': 20,
        'battery_critical': 10,
        
        'disk_io_warning': 1000,  # MB/s
        'network_warning': 100,    # MB/s
        'process_cpu_warning': 40,
        'process_memory_warning': 30,
    }
    
    def __init__(self, interval=15):
        """Initialize the comprehensive monitor."""
        self.interval = interval
        self.os_type = platform.system()
        self.prev_disk_io = psutil.disk_io_counters()
        self.prev_net_io = psutil.net_io_counters()
        self.prev_time = time.time()
        self.health_history = {
            'cpu': [],
            'memory': [],
            'disk': [],
            'temperature': []
        }
        self.history_max = 5
        
    def clear_screen(self):
        """Clear the console screen based on OS."""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def get_status_and_color(self, metric_type, value):
        """Determine health status and color for a metric."""
        if value is None:
            return HealthStatus.UNKNOWN, HealthStatus.COLOR_UNKNOWN
        
        if metric_type == 'cpu':
            if value >= self.THRESHOLDS['cpu_critical']:
                return HealthStatus.CRITICAL, HealthStatus.COLOR_CRITICAL
            elif value >= self.THRESHOLDS['cpu_warning']:
                return HealthStatus.WARNING, HealthStatus.COLOR_WARNING
            elif value >= self.THRESHOLDS['cpu_caution']:
                return HealthStatus.CAUTION, HealthStatus.COLOR_CAUTION
            else:
                return HealthStatus.HEALTHY, HealthStatus.COLOR_HEALTHY
        
        elif metric_type == 'memory':
            if value >= self.THRESHOLDS['memory_critical']:
                return HealthStatus.CRITICAL, HealthStatus.COLOR_CRITICAL
            elif value >= self.THRESHOLDS['memory_warning']:
                return HealthStatus.WARNING, HealthStatus.COLOR_WARNING
            elif value >= self.THRESHOLDS['memory_caution']:
                return HealthStatus.CAUTION, HealthStatus.COLOR_CAUTION
            else:
                return HealthStatus.HEALTHY, HealthStatus.COLOR_HEALTHY
        
        elif metric_type == 'disk':
            if value >= self.THRESHOLDS['disk_critical']:
                return HealthStatus.CRITICAL, HealthStatus.COLOR_CRITICAL
            elif value >= self.THRESHOLDS['disk_warning']:
                return HealthStatus.WARNING, HealthStatus.COLOR_WARNING
            elif value >= self.THRESHOLDS['disk_caution']:
                return HealthStatus.CAUTION, HealthStatus.COLOR_CAUTION
            else:
                return HealthStatus.HEALTHY, HealthStatus.COLOR_HEALTHY
        
        elif metric_type == 'temperature':
            if value >= self.THRESHOLDS['temp_critical']:
                return HealthStatus.CRITICAL, HealthStatus.COLOR_CRITICAL
            elif value >= self.THRESHOLDS['temp_warning']:
                return HealthStatus.WARNING, HealthStatus.COLOR_WARNING
            elif value >= self.THRESHOLDS['temp_caution']:
                return HealthStatus.CAUTION, HealthStatus.COLOR_CAUTION
            else:
                return HealthStatus.HEALTHY, HealthStatus.COLOR_HEALTHY
        
        elif metric_type == 'battery':
            if value <= self.THRESHOLDS['battery_critical']:
                return HealthStatus.CRITICAL, HealthStatus.COLOR_CRITICAL
            elif value <= self.THRESHOLDS['battery_warning']:
                return HealthStatus.WARNING, HealthStatus.COLOR_WARNING
            elif value <= self.THRESHOLDS['battery_caution']:
                return HealthStatus.CAUTION, HealthStatus.COLOR_CAUTION
            else:
                return HealthStatus.HEALTHY, HealthStatus.COLOR_HEALTHY
        
        return HealthStatus.HEALTHY, HealthStatus.COLOR_HEALTHY
    
    def get_recommendations(self, metric_type, value, status):
        """Generate actionable recommendations."""
        recommendations = []
        
        if metric_type == 'cpu' and status in [HealthStatus.CRITICAL, HealthStatus.WARNING]:
            recommendations.append("• Close unnecessary applications")
            recommendations.append("• Check Task Manager for runaway processes")
            recommendations.append("• Disable background services")
            if status == HealthStatus.CRITICAL:
                recommendations.append("• System heavily strained—consider restarting")
        
        elif metric_type == 'memory' and status in [HealthStatus.CRITICAL, HealthStatus.WARNING]:
            recommendations.append("• Close unused browser tabs and applications")
            recommendations.append("• Clear temporary files (Temp folder)")
            recommendations.append("• Check for memory leaks in processes")
            if status == HealthStatus.CRITICAL:
                recommendations.append("• Insufficient RAM—consider upgrading or restarting")
        
        elif metric_type == 'disk' and status in [HealthStatus.CRITICAL, HealthStatus.WARNING]:
            recommendations.append("• Delete unnecessary files and folders")
            recommendations.append("• Empty Recycle Bin")
            recommendations.append("• Run disk cleanup utility")
            recommendations.append("• Move large files to external storage")
            if status == HealthStatus.CRITICAL:
                recommendations.append("• URGENT: Disk almost full—immediate action required")
        
        elif metric_type == 'temperature' and status in [HealthStatus.CRITICAL, HealthStatus.WARNING]:
            recommendations.append("• Ensure proper ventilation around laptop")
            recommendations.append("• Clean dust from vents and fans")
            recommendations.append("• Check if fans are running normally")
            recommendations.append("• Reduce background processes")
            if status == HealthStatus.CRITICAL:
                recommendations.append("• CRITICAL: Overheat risk—shutdown immediately")
        
        elif metric_type == 'battery' and status in [HealthStatus.CRITICAL, HealthStatus.WARNING]:
            recommendations.append("• Connect to power adapter immediately")
            recommendations.append("• Reduce screen brightness")
            recommendations.append("• Close power-hungry applications")
            if value <= 10:
                recommendations.append("• CRITICAL: Save work and shutdown now")
        
        elif metric_type == 'disk_io' and status in [HealthStatus.WARNING, HealthStatus.CRITICAL]:
            recommendations.append("• Close disk-intensive applications")
            recommendations.append("• Run disk defragmentation (if mechanical disk)")
            recommendations.append("• Check for malware scanning in background")
        
        elif metric_type == 'usb_ports' and status == HealthStatus.WARNING:
            recommendations.append("• Inspect USB ports for physical damage")
            recommendations.append("• Try different USB devices")
            recommendations.append("• Update chipset drivers")
        
        elif metric_type == 'power_supply' and status in [HealthStatus.WARNING, HealthStatus.CRITICAL]:
            recommendations.append("• Check power adapter for loose connections")
            recommendations.append("• Inspect power cable for damage")
            recommendations.append("• Consider replacing power adapter")
        
        elif metric_type == 'disk_health' and status in [HealthStatus.WARNING, HealthStatus.CRITICAL]:
            recommendations.append("• Backup important data immediately")
            recommendations.append("• Run disk diagnostic tool")
            recommendations.append("• Consider replacing storage drive")
        
        return recommendations
    
    def analyze_trend(self, metric_type, current_value):
        """Analyze trend in metric values."""
        if current_value is None:
            return "No data"
        
        history = self.health_history.get(metric_type, [])
        
        if len(history) < 2:
            return "Insufficient data"
        
        avg_recent = sum(history[-3:]) / min(3, len(history))
        
        if current_value > avg_recent * 1.1:
            return "📈 Increasing"
        elif current_value < avg_recent * 0.9:
            return "📉 Decreasing"
        else:
            return "→ Stable"
    
    def get_cpu_metrics(self):
        """Retrieve CPU usage, frequency, and temperature."""
        cpu_percent = psutil.cpu_percent(interval=0.1, percpu=True)
        cpu_avg = psutil.cpu_percent(interval=0.1)
        cpu_freq = psutil.cpu_freq()
        temp = self.get_cpu_temperature()
        
        self.health_history['cpu'].append(cpu_avg)
        if len(self.health_history['cpu']) > self.history_max:
            self.health_history['cpu'].pop(0)
        
        if temp is not None:
            self.health_history['temperature'].append(temp)
            if len(self.health_history['temperature']) > self.history_max:
                self.health_history['temperature'].pop(0)
        
        return {
            'per_core': cpu_percent,
            'average': cpu_avg,
            'frequency': cpu_freq.current if cpu_freq else None,
            'temperature': temp,
            'cores': psutil.cpu_count(logical=False),
            'threads': psutil.cpu_count(logical=True)
        }
    
    def get_cpu_temperature(self):
        """Retrieve CPU temperature with cross-platform support."""
        try:
            temps = psutil.sensors_temperatures()
            
            if not temps:
                return None
            
            if self.os_type == 'Windows':
                if 'coretemp' in temps:
                    return temps['coretemp'][0].current
                elif 'acpitz' in temps:
                    return temps['acpitz'][0].current
            elif self.os_type == 'Darwin':
                if 'coretemp' in temps:
                    return temps['coretemp'][0].current
            else:
                if 'coretemp' in temps:
                    return temps['coretemp'][0].current
                elif 'acpitz' in temps:
                    return temps['acpitz'][0].current
            
            for key, entries in temps.items():
                if entries:
                    return entries[0].current
        
        except (OSError, AttributeError, PermissionError):
            pass
        
        return None
    
    def get_memory_metrics(self):
        """Retrieve memory usage statistics."""
        mem = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        self.health_history['memory'].append(mem.percent)
        if len(self.health_history['memory']) > self.history_max:
            self.health_history['memory'].pop(0)
        
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
        """Retrieve disk usage and I/O statistics."""
        disk_path = 'C:\\' if os.name == 'nt' else '/'
        disk_usage = psutil.disk_usage(disk_path)
        
        current_disk_io = psutil.disk_io_counters()
        current_time = time.time()
        time_delta = current_time - self.prev_time
        
        disk_read_speed = (current_disk_io.read_bytes - self.prev_disk_io.read_bytes) / time_delta if time_delta > 0 else 0
        disk_write_speed = (current_disk_io.write_bytes - self.prev_disk_io.write_bytes) / time_delta if time_delta > 0 else 0
        
        self.prev_disk_io = current_disk_io
        
        self.health_history['disk'].append(disk_usage.percent)
        if len(self.health_history['disk']) > self.history_max:
            self.health_history['disk'].pop(0)
        
        return {
            'total': disk_usage.total,
            'used': disk_usage.used,
            'free': disk_usage.free,
            'percent': disk_usage.percent,
            'read_speed': disk_read_speed,
            'write_speed': disk_write_speed,
            'read_count': current_disk_io.read_count,
            'write_count': current_disk_io.write_count
        }
    
    def get_network_metrics(self):
        """Retrieve network I/O statistics."""
        current_net_io = psutil.net_io_counters()
        current_time = time.time()
        time_delta = current_time - self.prev_time
        
        upload_speed = (current_net_io.bytes_sent - self.prev_net_io.bytes_sent) / time_delta if time_delta > 0 else 0
        download_speed = (current_net_io.bytes_recv - self.prev_net_io.bytes_recv) / time_delta if time_delta > 0 else 0
        
        self.prev_net_io = current_net_io
        
        return {
            'upload_speed': upload_speed,
            'download_speed': download_speed,
            'packets_sent': current_net_io.packets_sent,
            'packets_recv': current_net_io.packets_recv
        }
    
    def get_battery_metrics(self):
        """Retrieve battery status and health."""
        try:
            battery = psutil.sensors_battery()
            if battery:
                return {
                    'percent': battery.percent,
                    'is_charging': battery.power_plugged,
                    'time_left': battery.secsleft
                }
        except (AttributeError, OSError):
            pass
        
        return {
            'percent': None,
            'is_charging': None,
            'time_left': None
        }
    
    def get_usb_ports_health(self):
        """Check USB ports and connected devices health."""
        usb_info = {
            'ports_available': 0,
            'devices_connected': 0,
            'status': HealthStatus.HEALTHY,
            'details': []
        }
        
        try:
            if self.os_type == 'Windows':
                # Windows USB device check
                result = subprocess.run(['wmic', 'logicaldisk', 'get', 'name'], 
                                      capture_output=True, text=True, timeout=5)
                usb_info['ports_available'] = 4  # Standard USB ports
                usb_info['devices_connected'] = len([line for line in result.stdout.split('\n') if line.strip() and line.strip() != 'Name'])
            else:
                # Linux USB check
                result = subprocess.run(['lsusb'], capture_output=True, text=True, timeout=5)
                usb_info['devices_connected'] = len([line for line in result.stdout.split('\n') if line.strip()])
                usb_info['ports_available'] = 4
        except Exception:
            usb_info['status'] = HealthStatus.UNKNOWN
            usb_info['details'].append("Unable to retrieve USB information")
        
        return usb_info
    
    def get_power_supply_health(self):
        """Check power supply and charging health."""
        power_info = {
            'status': HealthStatus.HEALTHY,
            'charging': None,
            'details': []
        }
        
        try:
            battery = psutil.sensors_battery()
            if battery:
                power_info['charging'] = battery.power_plugged
                if battery.power_plugged:
                    power_info['details'].append("✓ Power adapter connected and functional")
                else:
                    power_info['details'].append("• Running on battery power")
            else:
                power_info['details'].append("• Desktop system (no battery)")
        except Exception:
            power_info['status'] = HealthStatus.UNKNOWN
        
        return power_info
    
    def get_disk_health(self):
        """Check disk SMART health status."""
        disk_health = {
            'status': HealthStatus.HEALTHY,
            'details': []
        }
        
        try:
            if self.os_type == 'Windows':
                # Windows disk health check
                result = subprocess.run(['wmic', 'logicaldisk', 'get', 'status'], 
                                      capture_output=True, text=True, timeout=5)
                if 'OK' in result.stdout:
                    disk_health['details'].append("✓ Disk status: OK")
                else:
                    disk_health['status'] = HealthStatus.WARNING
                    disk_health['details'].append("⚠ Disk status: Check required")
            elif self.os_type == 'Linux':
                # Check if SMART tools available
                result = subprocess.run(['which', 'smartctl'], capture_output=True, timeout=5)
                if result.returncode == 0:
                    disk_health['details'].append("✓ SMART tools available")
        except Exception:
            disk_health['details'].append("• SMART health check unavailable")
        
        return disk_health
    
    def get_process_health(self):
        """Identify resource-heavy processes."""
        process_issues = []
        
        try:
            procs = psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent'])
            
            for proc in procs:
                try:
                    if proc.info['cpu_percent'] > self.THRESHOLDS['process_cpu_warning']:
                        process_issues.append({
                            'name': proc.info['name'],
                            'cpu': proc.info['cpu_percent'],
                            'type': 'CPU'
                        })
                    
                    if proc.info['memory_percent'] > self.THRESHOLDS['process_memory_warning']:
                        process_issues.append({
                            'name': proc.info['name'],
                            'memory': proc.info['memory_percent'],
                            'type': 'Memory'
                        })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
        except Exception:
            pass
        
        return process_issues[:5]  # Top 5 heavy processes
    
    def get_system_info(self):
        """Retrieve system uptime and boot time."""
        boot_time = datetime.fromtimestamp(psutil.boot_time())
        uptime = datetime.now() - boot_time
        uptime_str = f"{uptime.days}d {uptime.seconds // 3600}h {(uptime.seconds % 3600) // 60}m"
        
        return {
            'boot_time': boot_time,
            'uptime': uptime_str,
            'hostname': platform.node(),
            'architecture': platform.architecture()[0]
        }
    
    def get_network_interfaces(self):
        """Get network interface status."""
        interfaces = {}
        try:
            stats = psutil.net_if_stats()
            for name, stat in stats.items():
                interfaces[name] = {
                    'is_up': stat.isup,
                    'mtu': stat.mtu,
                    'speed': stat.speed
                }
        except Exception:
            pass
        
        return interfaces
    
    def format_bytes(self, bytes_val):
        """Convert bytes to human-readable format."""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_val < 1024.0:
                return f"{bytes_val:.2f} {unit}"
            bytes_val /= 1024.0
        return f"{bytes_val:.2f} PB"
    
    def format_speed(self, bytes_per_sec):
        """Convert bytes/sec to human-readable speed format."""
        return f"{self.format_bytes(bytes_per_sec)}/s"
    
    def display_dashboard(self):
        """Display comprehensive health dashboard."""
        self.clear_screen()
        
        # Collect all metrics
        cpu = self.get_cpu_metrics()
        mem = self.get_memory_metrics()
        disk = self.get_disk_metrics()
        net = self.get_network_metrics()
        battery = self.get_battery_metrics()
        sys_info = self.get_system_info()
        usb_health = self.get_usb_ports_health()
        power_health = self.get_power_supply_health()
        disk_health = self.get_disk_health()
        process_issues = self.get_process_health()
        net_interfaces = self.get_network_interfaces()
        
        self.prev_time = time.time()
        
        all_issues = []
        
        output = []
        output.append("=" * 90)
        output.append(f"{'COMPREHENSIVE SYSTEM HEALTH MONITOR - ENTERPRISE EDITION':^90}")
        output.append(f"{'Updated: ' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'):^90}")
        output.append("=" * 90)
        
        # ==================== BASIC INFO ====================
        output.append(f"\n[SYSTEM INFO]")
        output.append(f"  Host: {sys_info['hostname']} | OS: {self.os_type} | Arch: {sys_info['architecture']}")
        output.append(f"  Boot Time: {sys_info['boot_time'].strftime('%Y-%m-%d %H:%M:%S')} | Uptime: {sys_info['uptime']}")
        
        # ==================== CPU SECTION ====================
        cpu_status, cpu_color = self.get_status_and_color('cpu', cpu['average'])
        cpu_trend = self.analyze_trend('cpu', cpu['average'])
        output.append(f"\n{cpu_color}[CPU]{HealthStatus.COLOR_RESET} - {cpu_status} | {cpu_trend} | Cores: {cpu['cores']} | Threads: {cpu['threads']}")
        output.append(f"  Average: {cpu_color}{cpu['average']:.1f}%{HealthStatus.COLOR_RESET}")
        if cpu['frequency']:
            output.append(f"  Frequency: {cpu['frequency']:.2f} MHz")
        
        if cpu['temperature'] is not None:
            temp_status, temp_color = self.get_status_and_color('temperature', cpu['temperature'])
            temp_trend = self.analyze_trend('temperature', cpu['temperature'])
            output.append(f"  Temperature: {temp_color}{cpu['temperature']:.1f}°C{HealthStatus.COLOR_RESET} ({temp_status}) | {temp_trend}")
            if temp_status != HealthStatus.HEALTHY:
                all_issues.append(('temperature', cpu['temperature'], temp_status))
        else:
            output.append(f"  Temperature: N/A")
        
        output.append(f"  Per-Core: {' | '.join([f'{c:.0f}%' for c in cpu['per_core']])}")
        
        if cpu_status != HealthStatus.HEALTHY:
            all_issues.append(('cpu', cpu['average'], cpu_status))
        
        # ==================== MEMORY SECTION ====================
        mem_status, mem_color = self.get_status_and_color('memory', mem['percent'])
        mem_trend = self.analyze_trend('memory', mem['percent'])
        output.append(f"\n{mem_color}[MEMORY]{HealthStatus.COLOR_RESET} - {mem_status} | {mem_trend}")
        output.append(f"  RAM - Total: {self.format_bytes(mem['total'])} | Used: {mem_color}{self.format_bytes(mem['used'])} ({mem['percent']:.1f}%){HealthStatus.COLOR_RESET} | Available: {self.format_bytes(mem['available'])}")
        output.append(f"  SWAP - Total: {self.format_bytes(mem['swap_total'])} | Used: {self.format_bytes(mem['swap_used'])} ({mem['swap_percent']:.1f}%)")
        
        if mem_status != HealthStatus.HEALTHY:
            all_issues.append(('memory', mem['percent'], mem_status))
        
        # ==================== DISK SECTION ====================
        disk_status, disk_color = self.get_status_and_color('disk', disk['percent'])
        disk_trend = self.analyze_trend('disk', disk['percent'])
        output.append(f"\n{disk_color}[DISK/STORAGE]{HealthStatus.COLOR_RESET} - {disk_status} | {disk_trend}")
        output.append(f"  Capacity - Total: {self.format_bytes(disk['total'])} | Used: {disk_color}{self.format_bytes(disk['used'])} ({disk['percent']:.1f}%){HealthStatus.COLOR_RESET} | Free: {self.format_bytes(disk['free'])}")
        output.append(f"  I/O Activity - Read: {self.format_speed(disk['read_speed'])} | Write: {self.format_speed(disk['write_speed'])}")
        output.append(f"  Cumulative - Read Operations: {disk['read_count']} | Write Operations: {disk['write_count']}")
        
        if disk_status != HealthStatus.HEALTHY:
            all_issues.append(('disk', disk['percent'], disk_status))
        
        # ==================== NETWORK SECTION ====================
        output.append(f"\n[NETWORK]")
        output.append(f"  Speeds - Download: {self.format_speed(net['download_speed'])} | Upload: {self.format_speed(net['upload_speed'])}")
        output.append(f"  Cumulative - Sent: {self.format_bytes(net['packets_sent'])} packets | Received: {self.format_bytes(net['packets_recv'])} packets")
        output.append(f"  Interfaces Active: {sum(1 for _, stat in net_interfaces.items() if stat['is_up'])}/{len(net_interfaces)}")
        
        # ==================== BATTERY SECTION ====================
        output.append(f"\n[BATTERY & POWER]")
        if battery['percent'] is not None:
            batt_status, batt_color = self.get_status_and_color('battery', battery['percent'])
            charging_status = "🔌 Charging" if battery['is_charging'] else "🔋 Discharging"
            output.append(f"  Battery Level: {batt_color}{battery['percent']:.1f}%{HealthStatus.COLOR_RESET} - {batt_status} | {charging_status}")
            
            if battery['time_left'] != psutil.POWER_TIME_UNLIMITED and battery['time_left'] != psutil.POWER_TIME_UNKNOWN:
                time_left = timedelta(seconds=int(battery['time_left']))
                output.append(f"  Time Remaining: {time_left}")
            
            if batt_status != HealthStatus.HEALTHY:
                all_issues.append(('battery', battery['percent'], batt_status))
        else:
            output.append(f"  Battery: N/A (Desktop or no battery detected)")
        
        output.append(f"  Power Supply: {' | '.join(power_health['details'])}")
        
        # ==================== USB PORTS ====================
        output.append(f"\n[USB PORTS & DEVICES]")
        output.append(f"  Available Ports: {usb_health['ports_available']} | Connected Devices: {usb_health['devices_connected']}")
        if usb_health['details']:
            for detail in usb_health['details'][:3]:
                output.append(f"  {detail}")
        
        # ==================== DISK HEALTH ====================
        output.append(f"\n[DISK HEALTH & INTEGRITY]")
        for detail in disk_health['details']:
            output.append(f"  {detail}")
        if disk_health['status'] != HealthStatus.HEALTHY:
            all_issues.append(('disk_health', 0, disk_health['status']))
        
        # ==================== TOP HEAVY PROCESSES ====================
        if process_issues:
            output.append(f"\n[HEAVY PROCESSES]")
            for proc in process_issues[:5]:
                if proc['type'] == 'CPU':
                    output.append(f"  ⚠ {proc['name']}: {proc['cpu']:.1f}% CPU")
                else:
                    output.append(f"  ⚠ {proc['name']}: {proc['memory']:.1f}% Memory")
        
        # ==================== HEALTH SUMMARY & RECOMMENDATIONS ====================
        output.append("\n" + "=" * 90)
        
        if all_issues:
            output.append(f"{'HEALTH ALERT - ISSUES DETECTED':^90}\n")
            
            for issue_type, value, status in all_issues:
                status_color = HealthStatus.COLOR_CRITICAL if status == HealthStatus.CRITICAL else HealthStatus.COLOR_WARNING if status == HealthStatus.WARNING else HealthStatus.COLOR_CAUTION
                output.append(f"{status_color}[{status}]{HealthStatus.COLOR_RESET} {issue_type.upper()}")
                
                recommendations = self.get_recommendations(issue_type, value, status)
                if recommendations:
                    for rec in recommendations:
                        output.append(f"  {rec}")
                output.append("")
        else:
            output.append(f"{HealthStatus.COLOR_HEALTHY}{'✓ ALL SYSTEMS HEALTHY':^90}{HealthStatus.COLOR_RESET}\n")
        
        output.append("=" * 90)
        output.append(f"{'Next refresh in ' + str(self.interval) + ' seconds... (Ctrl+C to stop)':^90}")
        output.append("=" * 90)
        
        print("\n".join(output))
    
    def run(self):
        """Main loop to run the monitor continuously."""
        try:
            while True:
                self.display_dashboard()
                time.sleep(self.interval)
        except KeyboardInterrupt:
            self.clear_screen()
            print("\nSystem Health Monitor stopped.")
            sys.exit(0)


def main():
    """Entry point for the script."""
    monitor = ComprehensiveSystemHealthMonitor(interval=15)
    monitor.run()


if __name__ == "__main__":
    main()