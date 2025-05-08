# The Enchanted Library Management System

![Enchanted Library](https://img.shields.io/badge/Enchanted-Library-purple)
![Version](https://img.shields.io/badge/Version-1.0-blue)
![Python](https://img.shields.io/badge/Python-3.7+-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

The Enchanted Library is an intelligent and secure book management system designed for the Grand Library of Eldoria. This system manages book lending, visitor authentication, section access, and archival preservation using object-oriented design principles and various design patterns.

## Table of Contents

- [Features](#features)
- [System Requirements](#system-requirements)
- [Installation](#installation)
- [Getting Started](#getting-started)
- [User Guide](#user-guide)
  - [Command Line Interface](#command-line-interface)
  - [Graphical User Interface](#graphical-user-interface)
- [System Architecture](#system-architecture)
- [Design Patterns](#design-patterns)
- [Object-Oriented Principles](#object-oriented-principles)
- [License](#license)

## Features

- **Book Management**: Add, view, search, and manage different types of books (General, Rare, Ancient)
- **User Management**: Register and manage different types of users (Librarians, Scholars, Guests)
- **Lending System**: Check out and return books with due date tracking
- **Access Control**: Role-based access to library sections and features
- **Late Fee Calculation**: Automatic calculation of late fees based on book type
- **Book Recommendations**: Smart book recommendations based on user history
- **Preservation Tracking**: Flag books for restoration based on condition
- **Event Notifications**: Notify relevant parties about library events
- **Dual Interface**: Both command-line and graphical user interfaces

## System Requirements

- Python 3.7 or higher
- Tkinter (for GUI)

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/enchanted-library.git
   cd enchanted-library
   ```

2. No additional dependencies are required beyond Python's standard library.

## Getting Started

To start the Enchanted Library system:

```
python main.py
```

This will prompt you to choose between the command-line interface (CLI) or the graphical user interface (GUI).

To directly launch the GUI:

```
python main.py gui
```

## User Guide

### Command Line Interface

The CLI provides a text-based interface for interacting with the library system.

#### Available Commands

- `help` - Show the help menu
- `login` - Log in to the system
- `logout` - Log out of the system
- `list books` - List all books
- `list users` - List all users (librarians only)
- `list sections` - List all library sections
- `search <term>` - Search for books
- `view book <id>` - View details of a book
- `view user <id>` - View details of a user
- `checkout <book_id>` - Check out a book
- `return <book_id>` - Return a book
- `add book` - Add a new book (librarians only)
- `add user` - Add a new user (librarians only)
- `recommend` - Get book recommendations
- `restore <book_id>` - Send a book for restoration
- `save data` - Save library data to JSON files
- `load data` - Load library data from JSON files
- `undo` - Undo the last command
- `exit` - Exit the system

#### Sample Usage

```
Enter command: login
Email: alice@library.com
Password: password123
Logged in as Alice Johnson

Enter command: search hobbit
Books matching 'hobbit':
--------------------------------------------------------------------------------
ID                                 | Title                          | Author                 | Status    
--------------------------------------------------------------------------------
9f7e5d3c-1a2b-3c4d-5e6f-7g8h9i0j1k | The Hobbit                    | J.R.R. Tolkien        | AVAILABLE 

Enter command: view book 9f7e5d3c-1a2b-3c4d-5e6f-7g8h9i0j1k
Book Details:
ID:             9f7e5d3c-1a2b-3c4d-5e6f-7g8h9i0j1k
Title:          The Hobbit
Author:         J.R.R. Tolkien
Year Published: 1937
ISBN:           9780547928227
Condition:      GOOD
Status:         AVAILABLE
Location:       N/A
Type:           General Book
Genre:          Fantasy
Is Bestseller:  False

Availability:   Book is available
```

### Graphical User Interface

The GUI provides a more user-friendly interface with the following features:

#### Login Screen

- Enter your email and password to log in
- Sample credentials are provided for testing

#### Dashboard

- View your user information
- See your currently borrowed books
- View library statistics
- Check recent activity

#### Book Management

- **Book List**: View all books in the library
- **Add Book**: Add new books to the library (librarians only)
- **Book Details**: View detailed information about a book

#### User Management (Librarians Only)

- **User List**: View all registered users
- **Add User**: Register new users
- **User Details**: View detailed information about a user

#### Lending Management

- **My Borrowed Books**: View and return your borrowed books
- **Overdue Books**: View all overdue books (librarians only)
- **Checkout Book**: Search for and check out books
- **Return Book**: Return your borrowed books

#### Search & Recommendations

- **Basic Search**: Search for books by title or author
- **Advanced Search**: Search with multiple criteria
- **Recommendations**: Get personalized book recommendations

## System Architecture

The Enchanted Library system is built using a modular architecture:

- **Models**: Core data structures (Book, User, Lending)
- **Patterns**: Implementation of design patterns
- **Services**: Business logic services
- **Security**: Access control and authentication
- **UI**: User interfaces (CLI and GUI)

## Design Patterns

The system implements various design patterns:

### Creational Patterns

- **Factory Pattern**: Create book and user objects
- **Singleton Pattern**: Ensure a single central catalog
- **Builder Pattern**: Create customized book entries

### Structural Patterns

- **Facade Pattern**: Provide a simplified library interface
- **Adapter Pattern**: Integrate legacy data
- **Decorator Pattern**: Add features dynamically

### Behavioral Patterns

- **Observer Pattern**: Notify about library events
- **Strategy Pattern**: Implement different lending rules
- **Command Pattern**: Allow undoable actions
- **State Pattern**: Track book status

## Object-Oriented Principles

The system demonstrates core OOP principles:

- **Encapsulation**: Private attributes with getters/setters
- **Inheritance**: Book and User hierarchies
- **Polymorphism**: Different implementations of abstract methods
- **Abstraction**: High-level interfaces hiding implementation details

## License

This project is licensed under the MIT License - see the LICENSE file for details.

---

© 2023 The Enchanted Library Team
