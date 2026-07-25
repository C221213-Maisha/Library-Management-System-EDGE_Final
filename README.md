# The Archive - Library Management System

A Django web application for managing a library's book catalog, borrowing, returns, and overdue fines, with separate capabilities for staff and regular members.

## Overview

The Archive lets members browse and search a book catalog, borrow and return copies, and track any fines owed for late returns. Staff accounts can additionally add, edit, and remove books from the catalog. Copy availability is computed dynamically from active borrow records rather than stored as a separate counter, so it can't drift out of sync.

## Features

**Accounts**
- User registration and login/logout (Django's built-in auth views plus a custom registration form)
- A profile page summarizing a member's active borrows, overdue items, and total fines owed

**Catalog**
- Paginated book listing (9 books per page) with search by title and filters by publisher and category
- Staff-only add, edit, and delete of catalog entries, with validation on publication year, copy count, and ISBN format
- Category choices: Fiction, Non-fiction, Science, History, Technology, Biography, Other

**Borrowing**
- Borrow a book if a copy is available and the member doesn't already have it checked out
- Fixed 7-day borrowing period
- Return a book, with an automatic fine calculation for late returns ($1/day overdue)
- "My Borrowed Books" view showing a member's current and past borrows
- Dedicated fines view listing overdue borrows and the total amount owed

**Admin**
- Django admin integration for `Book` and `Borrow` models, with list filters and search on title, author, ISBN, username, and book title

## Data Model

### `Book`
| Field | Type | Notes |
|---|---|---|
| title | CharField | |
| authors | CharField | |
| publisher | CharField | |
| year_of_publishing | PositiveIntegerField | Cannot be in the future |
| isbn | CharField | Optional, unique, 10 or 13 digits |
| category | CharField | Choice field |
| description | TextField | Optional |
| copies_total | PositiveIntegerField | Must be at least 1; cannot be set below the number currently checked out |

Computed properties: `copies_borrowed`, `copies_available`, `is_available`.

### `Borrow`
| Field | Type | Notes |
|---|---|---|
| user | ForeignKey → User | |
| book | ForeignKey → Book | |
| borrowed_date | DateField | Auto-set on creation |
| due_date | DateField | Defaults to 7 days after borrowing |
| returned | BooleanField | |
| returned_date | DateField | Optional |

Computed properties: `is_overdue`, `days_overdue`, `fine_amount`.

## Routes

| URL | View | Description |
|---|---|---|
| `/` | `home` | Landing page |
| `/register/` | `register` | Create an account |
| `/login/`, `/logout/` | Django auth views | Log in / out |
| `/accounts/profile/` | `profile` | Member summary |
| `/books/` | `book_list` | Browse/search/filter catalog |
| `/books/add/`, `/books/edit/<id>/` | `book_form` | Staff-only add/edit |
| `/books/delete/<id>/` | `book_delete` | Staff-only delete |
| `/books/borrow/<id>/` | `borrow_book` | Borrow a book |
| `/books/return/<id>/` | `return_book` | Return a book |
| `/borrowed/` | `borrowed_books` | A member's borrow history |
| `/search/` | `search_books` | Title search |
| `/fines/` | `fines` | Overdue borrows and total owed |
| `/admin/` | Django admin | Catalog and borrow management |

## Requirements

- Python 3
- Django >= 5.1, < 5.2 (see `requirements.txt`)

## Setup

1. Clone the repository.
2. (Recommended) create and activate a virtual environment.
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Apply database migrations:
   ```bash
   python manage.py migrate
   ```
5. (Optional) create a staff account to manage the catalog:
   ```bash
   python manage.py createsuperuser
   ```
6. Run the development server:
   ```bash
   python manage.py runserver
   ```
7. Visit `http://127.0.0.1:8000/` in your browser.

## Project Structure

```
library_management/      # Project configuration
├── __init__.py
├── asgi.py
├── settings.py
├── urls.py               # Root URL configuration (includes library.urls)
└── wsgi.py

library/                  # Main application
├── __init__.py
├── admin.py              # Admin site registration for Book, Borrow
├── apps.py
├── forms.py              # BookForm, UserRegistrationForm
├── models.py             # Book, Borrow
├── tests.py
├── urls.py                # App routes
└── views.py               # Catalog, borrowing, auth, and fines logic

templates/
├── base.html              # Shared layout ("The Archive")
└── library/
    └── login.html          # Login page (and other library/*.html templates)

manage.py                 # Django's command-line management utility
requirements.txt
db.sqlite3                 # SQLite database (development)
```

## Notes

- `DEBUG` is set to `True` and the `SECRET_KEY` is a Django-generated development key in `settings.py`; both should be changed before any production deployment.
- Fine calculation applies at $1 per day overdue and continues to accrue against the due date even for books not yet returned.
