import psutil
import time
from loguru import logger

class SystemMonitor:
    def __init__(self, threshold_cpu: float = 80.0, threshold_mem: float = 80.0):
        self.threshold_cpu = threshold_cpu
        self.threshold_mem = threshold_mem

    def check_health(self):
        cpu_usage = psutil.cpu_percent(interval=1)
        mem_usage = psutil.virtual_memory().percent
        
        logger.info(f"System Health -> CPU: {cpu_usage}% | RAM: {mem_usage}%")
        
        if cpu_usage > self.threshold_cpu:
            logger.warning(f"High CPU Usage Detected: {cpu_usage}%")
        
        if mem_usage > self.threshold_mem:
            logger.warning(f"High Memory Usage Detected: {mem_usage}%")
            
        return {
            "cpu": cpu_usage,
            "memory": mem_usage,
            "status": "Healthy" if cpu_usage < self.threshold_cpu else "Warning"
        }

if __name__ == "__main__":
    monitor = SystemMonitor()
    while True:
        monitor.check_health()
        time.sleep(10)
