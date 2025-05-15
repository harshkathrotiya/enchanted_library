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

def check_database_exists(db_name, user, password, host='localhost', port=5432):
    """Check if the database exists."""
    cmd = [
        'psql',
        '-h', host,
        '-p', str(port),
        '-U', user,
        '-c', f"SELECT 1 FROM pg_database WHERE datname='{db_name}'",
        'postgres'
    ]
    
    env = os.environ.copy()
    env['PGPASSWORD'] = password
    
    result = subprocess.run(cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    return '1 row' in result.stdout

def create_database(db_name, user, password, host='localhost', port=5432):
    """Create the database."""
    cmd = [
        'psql',
        '-h', host,
        '-p', str(port),
        '-U', user,
        '-c', f"CREATE DATABASE {db_name}",
        'postgres'
    ]
    
    env = os.environ.copy()
    env['PGPASSWORD'] = password
    
    result = subprocess.run(cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    if result.returncode != 0:
        print(f"Error creating database: {result.stderr}")
        return False
    
    return True

def update_config_file(db_name, user, password, host='localhost', port=5432):
    """Update the database configuration file."""
    config_path = 'database/config.py'
    
    # Create the content for the config file
    content = f'''import os

DATABASE_URL = os.environ.get(
    'DATABASE_URL', 
    'postgresql://{user}:{password}@{host}:{port}/{db_name}'
)

# Default database configuration
DB_CONFIG = {{
    'host': '{host}',
    'port': {port},
    'database': '{db_name}',
    'user': '{user}',
    'password': '{password}'
}}'''
    
    # Write the content to the config file
    with open(config_path, 'w') as f:
        f.write(content)
    
    print(f"Updated configuration in {config_path}")
    return True

def main():
    print("Enchanted Library Database Setup")
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
    
    # Check if the database exists
    if check_database_exists(db_name, user, password, host, int(port)):
        print(f"Database '{db_name}' already exists.")
    else:
        print(f"Creating database '{db_name}'...")
        if create_database(db_name, user, password, host, int(port)):
            print(f"Database '{db_name}' created successfully.")
        else:
            print(f"Failed to create database '{db_name}'.")
            sys.exit(1)
    
    # Update the configuration file
    if update_config_file(db_name, user, password, host, int(port)):
        print("Database configuration updated successfully.")
    else:
        print("Failed to update database configuration.")
        sys.exit(1)
    
    print("\nDatabase setup completed successfully!")
    print("You can now run the application with:")
    print("  python main.py")

if __name__ == "__main__":
    main()
