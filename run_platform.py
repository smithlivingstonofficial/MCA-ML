"""
Integrated Hospital Operations Intelligence Platform
Single-command launcher and system integrity verification script.
"""

import os
import sys
import subprocess
import argparse


def check_system_integrity():
    print("=" * 70)
    print("🏥 Antigravity Health Intelligence Platform — Integrity Verification")
    print("=" * 70)

    # 1. Python Virtual Environment Check
    print(f"[*] Python Executable: {sys.executable}")
    print(f"[*] Python Version: {sys.version.split()[0]}")

    # 2. Database Check
    db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "hospital.db"))
    if os.path.exists(db_path):
        size_kb = os.path.getsize(db_path) / 1024
        print(f"[+] SQLite Database: {db_path} ({size_kb:.1f} KB) [FOUND]")
    else:
        print(f"[!] Warning: Database not found at {db_path}. Run migrations/seeds first.")

    # 3. Serialized ML Artifacts
    m1_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "backend/ml/models/ed_arrival_model.joblib"))
    m6_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "backend/ml/models/readmission_model.joblib"))

    print(f"[{'+' if os.path.exists(m1_path) else '!'}] Module 1 ML Model: {m1_path} [{'FOUND' if os.path.exists(m1_path) else 'MISSING'}]")
    print(f"[{'+' if os.path.exists(m6_path) else '!'}] Module 6 ML Model: {m6_path} [{'FOUND' if os.path.exists(m6_path) else 'MISSING'}]")

    # 4. Frontend Dist Check
    dist_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "frontend/dist"))
    print(f"[{'+' if os.path.exists(dist_path) else '!'}] Frontend Production Build: {dist_path} [{'BUILT' if os.path.exists(dist_path) else 'NOT BUILT'}]")

    print("=" * 70)


def run_tests():
    print("[*] Launching complete 47-test pytest suite across Phases 1 to 7...")
    cmd = [sys.executable, "-m", "pytest", "-v"]
    result = subprocess.run(cmd)
    sys.exit(result.returncode)


def run_server(port: int = 8000, host: str = "127.0.0.1", reload: bool = True):
    print(f"[*] Starting FastAPI Uvicorn Server on http://{host}:{port} ...")
    cmd = [
        sys.executable, "-m", "uvicorn",
        "backend.app.main:app",
        "--host", host,
        "--port", str(port)
    ]
    if reload:
        cmd.append("--reload")

    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\n[!] Server stopped by user.")


def main():
    parser = argparse.ArgumentParser(description="Integrated Hospital Operations Intelligence Platform")
    parser.add_argument("--check", action="store_true", help="Run system integrity diagnostics")
    parser.add_argument("--test", action="store_true", help="Run automated pytest verification suite")
    parser.add_argument("--port", type=int, default=8000, help="Backend port (default: 8000)")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Backend host (default: 127.0.0.1)")
    parser.add_argument("--no-reload", action="store_true", help="Disable auto-reloading")

    args = parser.parse_args()

    if args.check:
        check_system_integrity()
    elif args.test:
        run_tests()
    else:
        check_system_integrity()
        run_server(port=args.port, host=args.host, reload=not args.no_reload)


if __name__ == "__main__":
    main()
