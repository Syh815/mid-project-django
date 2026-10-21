import os
import subprocess
import sys

def stop_server_on_port(port=8000):
    print("=" * 60)
    print(f"  [關閉中] 正在尋找佔用 Port {port} 之服務/進程...")
    print("=" * 60)
    
    try:
        # 執行 netstat 查詢
        raw_output = subprocess.check_output(f"netstat -ano", shell=True)
        try:
            output = raw_output.decode('utf-8')
        except UnicodeDecodeError:
            output = raw_output.decode('cp950', errors='ignore')
            
        pids = set()
        for line in output.splitlines():
            line_clean = line.strip()
            # 尋找監聽 8000 port 的 TCP 服務
            if f":{port} " in line_clean and "LISTENING" in line_clean:
                parts = line_clean.split()
                if parts:
                    pid_str = parts[-1]
                    if pid_str.isdigit() and int(pid_str) > 0:
                        pids.add(int(pid_str))

        if not pids:
            print(f"\n>> [提示] 目前沒有偵測到任何佔用 Port {port} 的 Django 服務。")
        else:
            print(f"\n>> 偵測到佔用 Port {port} 的行程 PID: {list(pids)}")
            for pid in pids:
                print(f">> 正在終止 PID: {pid} ...")
                subprocess.run(f"taskkill /F /PID {pid}", shell=True, capture_output=True)
            print(f"\n>> [成功] 已成功關閉 Port {port} 之 Django 伺服器！")

    except Exception as e:
        print(f"\n>> [錯誤] 執行過程中發生異常: {e}")

if __name__ == '__main__':
    stop_server_on_port(8000)
