# python monitor_memory.py
# Monitors system memory and restarts Ollama if memory is low

import psutil
import time
import subprocess

def check_memory():
    mem = psutil.virtual_memory()
    print(f"Total: {mem.total / (1024**3):.1f}GB")
    print(f"Available: {mem.available / (1024**3):.1f}GB")
    print(f"Used: {mem.percent}%")
    
    # Find Ollama process
    for proc in psutil.process_iter(['name', 'memory_info']):
        if 'ollama' in proc.info['name'].lower():
            mem_mb = proc.info['memory_info'].rss / (1024**2)
            print(f"Ollama: {mem_mb:.0f}MB")
    
    if mem.available < 1.5 * (1024**3):  # Less than 1.5GB
        print("⚠️  LOW MEMORY! Consider restarting Ollama")
        return False
    return True

if __name__ == "__main__":
    while True:
        print("\n" + "="*50)
        if not check_memory():
            print("\nRestarting Ollama...")
            subprocess.run(["taskkill", "/F", "/IM", "ollama.exe"])
            time.sleep(3)
            subprocess.Popen(["ollama", "serve"])
        time.sleep(60)  # Check every minute

