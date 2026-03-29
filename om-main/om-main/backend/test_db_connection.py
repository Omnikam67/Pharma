#!/usr/bin/env python
"""Test database connection with diagnostic info"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Ensure Windows terminals that default to cp1252 don't crash on Unicode output.
try:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

print("=" * 60)
print("DATABASE CONNECTION DIAGNOSTICS")
print("=" * 60)

# Check .env file exists
env_file = Path(__file__).parent / '.env'
# Prefer backend/.env over any pre-set environment variables (common in Windows shells).
load_dotenv(env_file, override=True)
print(f"\n.env file exists: {env_file.exists()}")
print(f"   Path: {env_file}")

if env_file.exists():
    with open(env_file) as f:
        content = f.read()
        # Print only database config lines
        for line in content.split('\n'):
            if 'MYSQL_' in line:
                if line.startswith("MYSQL_PASSWORD="):
                    print("   MYSQL_PASSWORD=<hidden>")
                else:
                    print(f"   {line}")

print(f"\nEnvironment Variables Loaded:")
print(f"   MYSQL_USER: {os.getenv('MYSQL_USER', 'NOT SET')}")
password = os.getenv('MYSQL_PASSWORD', 'NOT SET')
password_len = len(password) if password != 'NOT SET' else 0
print(f"   MYSQL_PASSWORD: <hidden> (length: {password_len})")
print(f"   MYSQL_HOST: {os.getenv('MYSQL_HOST', 'NOT SET')}")
print(f"   MYSQL_PORT: {os.getenv('MYSQL_PORT', 'NOT SET')}")
print(f"   MYSQL_DB: {os.getenv('MYSQL_DB', 'NOT SET')}")

# Test direct pymysql connection
print(f"\nTesting direct PyMySQL connection...")
try:
    import pymysql
    conn = pymysql.connect(
        host=os.getenv('MYSQL_HOST', 'localhost'),
        user=os.getenv('MYSQL_USER', 'root'),
        password=os.getenv('MYSQL_PASSWORD', ''),
        database=os.getenv('MYSQL_DB', 'pharmacy_db')
    )
    print(f"   OK: PyMySQL connection successful!")
    conn.close()
except Exception as e:
    print(f"   FAIL: PyMySQL connection failed: {e}")

# Test SQLAlchemy connection
print(f"\nTesting SQLAlchemy connection...")
try:
    from app.core.database import engine, DATABASE_URL
    try:
        from sqlalchemy.engine.url import make_url
        safe_url = make_url(DATABASE_URL).render_as_string(hide_password=True)
    except Exception:
        safe_url = "<unable to render safely>"
    print(f"   Database URL: {safe_url}")
    conn = engine.connect()
    print(f"   OK: SQLAlchemy connection successful!")
    conn.close()
except Exception as e:
    print(f"   FAIL: SQLAlchemy connection failed: {e}")

print("\n" + "=" * 60)
