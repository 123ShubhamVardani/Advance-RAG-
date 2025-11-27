"""
Health check and monitoring utilities
"""

import psutil
import os
from datetime import datetime
from typing import Dict, Any

class HealthChecker:
    """System health monitoring"""
    
    @staticmethod
    def get_system_health() -> Dict[str, Any]:
        """Get current system health metrics"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "system": {
                    "cpu_percent": cpu_percent,
                    "memory_percent": memory.percent,
                    "memory_available_gb": memory.available / (1024**3),
                    "disk_percent": disk.percent,
                    "disk_free_gb": disk.free / (1024**3)
                },
                "application": {
                    "cache_files": len([f for f in os.listdir('.') if f.startswith('cache_')]),
                    "log_files": len([f for f in os.listdir('logs') if f.endswith('.log')]) if os.path.exists('logs') else 0
                }
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    @staticmethod
    def cleanup_old_files():
        """Clean up old cache and log files"""
        try:
            # Remove cache files older than 24 hours
            current_time = datetime.now().timestamp()
            for file in os.listdir('.'):
                if file.startswith('cache_') and file.endswith('.json'):
                    file_time = os.path.getctime(file)
                    if current_time - file_time > 86400:  # 24 hours
                        os.remove(file)
            
            # Remove old log files (keep last 7 days)
            if os.path.exists('logs'):
                for file in os.listdir('logs'):
                    if file.endswith('.log'):
                        file_path = os.path.join('logs', file)
                        file_time = os.path.getctime(file_path)
                        if current_time - file_time > 604800:  # 7 days
                            os.remove(file_path)
            
            return True
        except Exception:
            return False
