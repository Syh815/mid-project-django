"""
Django Server 啟動腳本
提供清晰終端資訊，完整支援 UTF-8 編碼與正常終止信號。
"""
import os
import sys
import subprocess

# 確保在 Windows 終端機能正確輸出繁體中文 UTF-8
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

def main():
    print("=" * 64)
    print("  [啟動中] 國立大學  網路選課系統 (Port 8000)")
    print("  本地網址: http://127.0.0.1:8000/")
    print("  Cloudflare Tunnel 連接埠: 8000")
    print("  若要關閉請按 Ctrl+C，或雙擊 stop_server.bat")
    print("=" * 64)
    print()

    # 切換至專案根目錄
    base_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(base_dir)

    manage_py = os.path.join(base_dir, "manage.py")
    cmd = [sys.executable, manage_py, "runserver", "0.0.0.0:8000"]

    try:
        proc = subprocess.run(cmd)
        sys.exit(proc.returncode)
    except KeyboardInterrupt:
        print("\n[提示] 伺服器已正常停止。")
        sys.exit(0)

if __name__ == '__main__':
    main()
