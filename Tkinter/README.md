This is the Tkinter version I had initially started working on, but I switched to Pyside6. 
- **There won't be further developments for this version.**

## Features

**Current:**

* **Client Management:**
    * Add, edit, and view client information.
    * Delete clients without associated transactions.
* **Transaction Management:**
    * View monthly summaries by year.
    * Track daily transactions.
    * Add, edit, and delete transactions with ease.

## Tech stack
* Python
* Tkinter UI
* SQLite database

## File structure

```
mota/
    Tkinter/
            database.py
            client.py
            transactions.py
            main.py
            finance_management.sqlite
```

## Getting Started

**Prerequisites:**

* Python 3.11.x
* Tkinter(comes pre-installed in Python)

**Installation**

1. Clone the repository: `git clone https://github.com/Sylvester254/MOTA`
2. **(Optional but Recommended):**  Create virtual environment.

**Usage** 

* Run `python3 Tkinter/main.py`. This will launch the application GUI.
