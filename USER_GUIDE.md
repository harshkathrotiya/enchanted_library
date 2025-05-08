# Enchanted Library - User Guide

This comprehensive guide will help you navigate and use all the features of the Enchanted Library Management System.

## Table of Contents

- [Getting Started](#getting-started)
  - [Launching the Application](#launching-the-application)
  - [Logging In](#logging-in)
- [Command Line Interface (CLI)](#command-line-interface-cli)
  - [Basic Navigation](#basic-navigation)
  - [Book Operations](#book-operations-cli)
  - [User Operations](#user-operations-cli)
  - [Lending Operations](#lending-operations-cli)
  - [Advanced Features](#advanced-features-cli)
- [Graphical User Interface (GUI)](#graphical-user-interface-gui)
  - [Navigation](#navigation)
  - [Dashboard](#dashboard)
  - [Book Management](#book-management)
  - [User Management](#user-management)
  - [Lending Management](#lending-management)
  - [Search & Recommendations](#search--recommendations)
- [User Roles and Permissions](#user-roles-and-permissions)
- [Troubleshooting](#troubleshooting)

## Getting Started

### Launching the Application

1. Open a terminal or command prompt
2. Navigate to the Enchanted Library directory
3. Run the application:
   ```
   python main.py
   ```
4. Choose your preferred interface:
   - Enter `1` for Command Line Interface
   - Enter `2` for Graphical User Interface

Alternatively, you can directly launch the GUI:
```
python main.py gui
```

### Logging In

The system comes with pre-configured sample accounts:

| Role      | Email                 | Password    |
|-----------|----------------------|-------------|
| Librarian | alice@library.com    | password123 |
| Librarian | bob@library.com      | password123 |
| Scholar   | carol@university.edu | password123 |
| Scholar   | david@university.edu | password123 |
| Guest     | eve@example.com      | password123 |

## Command Line Interface (CLI)

### Basic Navigation

- Type commands at the prompt and press Enter
- Use `help` to see available commands
- Use `exit` to quit the application

### Book Operations (CLI)

#### Viewing Books
```
list books
```
Lists all books in the library with their basic information.

#### Searching for Books
```
search <term>
```
Searches for books by title or author.

Example:
```
search tolkien
```

#### Viewing Book Details
```
view book <book_id>
```
Shows detailed information about a specific book.

#### Adding a Book (Librarians Only)
```
add book
```
Starts the interactive book addition process. You'll be prompted for:
- Book type (general/rare/ancient)
- Title, author, year published, ISBN
- Type-specific details

### User Operations (CLI)

#### Viewing Users (Librarians Only)
```
list users
```
Lists all users registered in the system.

#### Viewing User Details
```
view user <user_id>
```
Shows detailed information about a specific user.

#### Adding a User (Librarians Only)
```
add user
```
Starts the interactive user registration process.

### Lending Operations (CLI)

#### Checking Out a Book
```
checkout <book_id>
```
Borrows a book if it's available and you have permission.

#### Returning a Book
```
return <book_id>
```
Returns a book you've borrowed. You'll be asked if the book's condition has changed.

### Advanced Features (CLI)

#### Getting Book Recommendations
```
recommend
```
Shows book recommendations based on your borrowing history.

#### Restoring a Book
```
restore <book_id>
```
Marks a book for restoration (changes its status to RESTORATION).

#### Saving and Loading Data
```
save data
load data
```
Saves the current library state to JSON files or loads from them.

#### Undoing Commands
```
undo
```
Undoes the last command (if it's undoable).

## Graphical User Interface (GUI)

### Navigation

The GUI features a sidebar with navigation buttons:
- **Dashboard**: Overview of your account and library statistics
- **Search**: Find books and get recommendations
- **Books**: Manage books in the library
- **Lending**: Manage book borrowing and returns
- **Users**: Manage library users (librarians only)

### Dashboard

The dashboard provides an overview of:
- Your user information
- Your currently borrowed books
- Library statistics
- Recent activity in the library

### Book Management

#### Book List
- View all books in the library
- Double-click on a book to see its details
- Use the refresh button to update the list

#### Add Book (Librarians Only)
1. Select the book type (General, Rare, or Ancient)
2. Fill in the common book information (title, author, year, ISBN)
3. Fill in the type-specific information
4. Click "Add Book"

#### Book Details
- View comprehensive information about a book
- Check out or return the book directly from this screen
- See lending history and availability status

### User Management

#### User List (Librarians Only)
- View all users registered in the system
- Double-click on a user to see their details
- Use the refresh button to update the list

#### Add User (Librarians Only)
1. Select the user type (Librarian, Scholar, or Guest)
2. Fill in the common user information (name, email, password)
3. Fill in the role-specific information
4. Click "Add User"

#### User Details (Librarians Only)
- View comprehensive information about a user
- See their borrowed books
- Activate or deactivate their account

### Lending Management

#### My Borrowed Books
- View all books you've currently borrowed
- See due dates and overdue status
- Return books directly from this tab

#### Overdue Books (Librarians Only)
- View all overdue books in the library
- See who has borrowed them and for how long
- Check calculated late fees

#### Checkout Book
1. Search for a book by title or author
2. Select the book you want to borrow
3. Click "Checkout Selected Book"

#### Return Book
1. Select the book you want to return
2. Indicate if the book's condition has changed
3. Click "Return Selected Book"

### Search & Recommendations

#### Basic Search
1. Enter a search term (title or author)
2. Click "Search"
3. View the results in the list
4. Double-click on a book to see its details

#### Advanced Search
1. Fill in any combination of search criteria
2. Select book type and status filters
3. Click "Search"
4. View the filtered results

#### Recommendations
- View personalized book recommendations
- See why each book is recommended
- Double-click on a book to see its details

## User Roles and Permissions

### Librarian
- Full access to all system features
- Can add, edit, and manage books
- Can manage user accounts
- Can view all lending records
- Can access restricted sections

### Scholar
- Can borrow more books than guests
- Can access some restricted sections
- Cannot manage books or users
- Gets specialized recommendations

### Guest
- Basic borrowing privileges
- Limited to general sections
- Cannot manage books or users
- Limited number of simultaneous loans

## Troubleshooting

### Common Issues

**Problem**: Cannot log in
**Solution**: Verify your email and password. If using sample accounts, make sure you're using the exact credentials listed in this guide.

**Problem**: Cannot check out a book
**Solution**: Check if:
- The book is available (not already borrowed)
- You have permission to access the book's section
- You haven't reached your borrowing limit
- Your membership is valid (for guests)

**Problem**: GUI doesn't launch
**Solution**: Ensure you have Tkinter installed with your Python distribution. Most Python installations include Tkinter by default.

For additional help or to report issues, please contact the library administrator.

---

© 2023 The Enchanted Library Team
