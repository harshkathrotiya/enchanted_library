#!/usr/bin/env python3

import os
import sys
import subprocess
import getpass

def check_postgres_installed():
    """Check if PostgreSQL is installed."""
    try:
        subprocess.run(['which', 'psql'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except subprocess.CalledProcessError:
        return False

def reset_database(db_name, user, password, host='localhost', port=5432):
    """Reset the database by dropping and recreating it."""
    # Drop the database
    drop_cmd = [
        'psql',
        '-h', host,
        '-p', str(port),
        '-U', user,
        '-c', f"DROP DATABASE IF EXISTS {db_name}",
        'postgres'
    ]
    
    env = os.environ.copy()
    env['PGPASSWORD'] = password
    
    result = subprocess.run(drop_cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    if result.returncode != 0:
        print(f"Error dropping database: {result.stderr}")
        return False
    
    # Create the database
    create_cmd = [
        'psql',
        '-h', host,
        '-p', str(port),
        '-U', user,
        '-c', f"CREATE DATABASE {db_name}",
        'postgres'
    ]
    
    result = subprocess.run(create_cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    if result.returncode != 0:
        print(f"Error creating database: {result.stderr}")
        return False
    
    print(f"Database '{db_name}' has been reset successfully.")
    return True

def main():
    print("Enchanted Library Database Reset")
    print("===============================")
    
    # Check if PostgreSQL is installed
    if not check_postgres_installed():
        print("PostgreSQL is not installed or not in PATH.")
        print("Please install PostgreSQL and try again.")
        sys.exit(1)
    
    # Get database connection details
    db_name = input("Database name [enchanted_library]: ").strip() or "enchanted_library"
    host = input("Database host [localhost]: ").strip() or "localhost"
    port = input("Database port [5432]: ").strip() or "5432"
    user = input("Database user [postgres]: ").strip() or "postgres"
    password = getpass.getpass("Database password: ")
    
    # Confirm reset
    confirm = input(f"Are you sure you want to reset the database '{db_name}'? This will delete all data. (y/n): ")
    if confirm.lower() != 'y':
        print("Database reset cancelled.")
        sys.exit(0)
    
    # Reset the database
    if reset_database(db_name, user, password, host, int(port)):
        print("\nDatabase reset completed successfully!")
        print("You can now run the application with:")
        print("  python main.py")
    else:
        print("\nDatabase reset failed.")
        sys.exit(1)

if __name__ == "__main__":
    main()
