# Enchanted Library Management System

A comprehensive library management system with PostgreSQL database support.

## Features

- Book management (add, update, remove, search)
- User management (librarians, scholars, guests)
- Lending system with due dates and late fees
- Section management with access control
- Preservation service for rare and ancient books
- Recommendation system
- Command-line and graphical user interfaces

## Database Setup:

The Enchanted Library Management System uses PostgreSQL for data storage. Follow these steps to set up the database:

1. Install PostgreSQL if you haven't already:
   - **macOS**: `brew install postgresql`
   - **Linux**: `sudo apt-get install postgresql`
   - **Windows**: Download and install from [postgresql.org](https://www.postgresql.org/download/windows/)

2. Run the database setup script:
   ```
   python setup_database.py
   ```
   
   This script will:
   - Check if PostgreSQL is installed
   - Create a new database (default name: `enchanted_library`)
   - Update the database configuration file

3. The script will prompt you for:
   - Database name (default: `enchanted_library`)
   - Host (default: `localhost`)
   - Port (default: `5432`)
   - Username (default: `postgres`)
   - Password

## Running the Application

After setting up the database, you can run the application:

```
python main.py
```

The first time you run the application, it will:
1. Initialize the database tables
2. Create sample data if the database is empty
3. Start the application

You can choose between:
- Command-line interface (CLI)
- Graphical user interface (GUI)

To directly start the GUI:

```
python main.py gui
```

## Data Persistence

The application uses PostgreSQL for data persistence. All changes are automatically saved to the database.

The legacy JSON-based persistence is still available for backward compatibility but is not recommended for new installations.

## System Requirements

- Python 3.7 or higher
- PostgreSQL 10 or higher
- Required Python packages:
  - sqlalchemy
  - psycopg2-binary

## Installation

1. Clone the repository
2. Install the required packages:
   ```
   pip install sqlalchemy psycopg2-binary
   ```
3. Set up the database as described above
4. Run the application

## License

This project is licensed under the MIT License - see the LICENSE file for details.
