import subprocess
import os

exe_path = r"C:\Users\Brandon Owens\AppData\Local\Temp\WinGet\PostgreSQL.PostgreSQL.16.16.15-1\postgresql-16.15-1-windows-x64.exe"
if not os.path.exists(exe_path):
    print(f"Error: {exe_path} not found")
    exit(1)

args = [
    exe_path,
    "--mode", "unattended",
    "--unattendedmodeui", "none",
    "--superpassword", "postgres",
    "--serverport", "5432",
]

print("Starting PostgreSQL 16 unattended installation...")
res = subprocess.run(args)
print(f"PostgreSQL installation finished with return code: {res.returncode}")
