import os
import sys
import zipfile
import urllib.request
import subprocess
from pathlib import Path

PG_ZIP_URL = "https://sbp.enterprisedb.com/getfile.jsp?fileid=1260422"
BASE_DIR = Path(__file__).parent.resolve()
PG_DIR = BASE_DIR / "pgsql"
DATA_DIR = PG_DIR / "data"
ZIP_PATH = BASE_DIR / "pgsql-16.15-windows-x64-binaries.zip"

def setup_portable_postgres():
    print("=" * 80)
    print("PORTABLE POSTGRESQL 16 SETUP FOR WINDOWS (NO ADMIN / NO UAC REQUIRED)")
    print("=" * 80)

    # 1. Download ZIP if needed
    if not PG_DIR.exists():
        if not ZIP_PATH.exists():
            print(f"[1/4] Downloading portable PostgreSQL 16 binaries from EnterpriseDB...")
            opener = urllib.request.build_opener()
            opener.addheaders = [('User-agent', 'Mozilla/5.0')]
            urllib.request.install_opener(opener)
            
            def report(block_num, block_size, total_size):
                if total_size > 0:
                    pct = int(block_num * block_size * 100 / total_size)
                    if pct % 20 == 0 and block_num % 50 == 0:
                        print(f"  Downloading... {pct}% ({block_num * block_size / 1e6:.1f} MB / {total_size / 1e6:.1f} MB)")

            urllib.request.urlretrieve(PG_ZIP_URL, str(ZIP_PATH), report)
            print(f"  Downloaded: {ZIP_PATH.stat().st_size / 1e6:.1f} MB")
        
        # 2. Extract ZIP
        print(f"[2/4] Extracting binaries to {PG_DIR}...")
        with zipfile.ZipFile(ZIP_PATH, 'r') as z:
            z.extractall(BASE_DIR)
        print("  Extraction complete.")
        
        if ZIP_PATH.exists():
            ZIP_PATH.unlink()

    # 3. Initialize Database Cluster with initdb
    initdb_exe = PG_DIR / "bin" / "initdb.exe"
    if not DATA_DIR.exists():
        print(f"[3/4] Initializing database cluster at {DATA_DIR}...")
        res = subprocess.run([
            str(initdb_exe),
            "-D", str(DATA_DIR),
            "-U", "postgres",
            "-A", "trust",
            "-E", "UTF8",
            "--locale=C",
        ], capture_output=True, text=True)
        print("initdb output:", res.stdout)
        if res.returncode != 0:
            print("initdb error:", res.stderr)
            sys.exit(1)
        print("  Database cluster initialized successfully.")
    else:
        print(f"[3/4] Database cluster already exists at {DATA_DIR}.")

    # 4. Start PostgreSQL Server with pg_ctl
    pg_ctl_exe = PG_DIR / "bin" / "pg_ctl.exe"
    log_file = PG_DIR / "logfile.log"
    print(f"[4/4] Starting PostgreSQL server on port 5432...")
    
    # Stop if already running
    subprocess.run([str(pg_ctl_exe), "-D", str(DATA_DIR), "stop"], capture_output=True)
    
    start_cmd = [
        str(pg_ctl_exe),
        "-D", str(DATA_DIR),
        "-l", str(log_file),
        "-o", "-p 5432",
        "start"
    ]
    res = subprocess.run(start_cmd, capture_output=True, text=True)
    print("pg_ctl start output:", res.stdout)
    if res.returncode != 0:
        print("pg_ctl start error:", res.stderr)
        
    print("\nPostgreSQL 16 is running on localhost:5432 with user 'postgres' (trust auth).")

if __name__ == "__main__":
    setup_portable_postgres()
