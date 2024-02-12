# MOTA [![PySide6](https://img.shields.io/badge/PySide6-blue?logo=qt&logoColor=red)](https://www.pythonguis.com/pyside6-book/)

*A finance management application designed for freelancers*

## Description

MOTA focuses on providing a clear overview of your freelance earnings. See monthly totals at a glance and easily drill down into daily transaction details for specific periods.  This empowers you to analyze your income trends quickly.

## Features

**Current:**

* **Client Management:**
    * Add, edit, and view client information.
    * Delete clients without associated transactions.
* **Income Management:**
    * View monthly summaries by year.
    * Track daily transactions.
    * Add, edit, and delete transactions with ease.

**Planned:**

* **Visualizations:**  Charts and graphs showcasing earnings trends.
* **Income Predictions:** Estimates for tax planning.
* **Reports:** Comprehensive monthly summaries and detailed reports.

## Technology Stack

* [![Python](https://img.shields.io/badge/python-3973B3?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
* [![PySide6](https://img.shields.io/badge/PySide6-blue?logo=qt&logoColor=red)](https://www.pythonguis.com/pyside6-book/)
* [![SQLite](https://img.shields.io/badge/SQLite-07405E?style=for-the-badge&logo=sqlite&logoColor=white)](https://www.sqlite.org/index.html)


## Project Structure
```
  project_root/
      main.py               # Your application's entry point, UI setup
      models.py             # Classes defining Client, Transaction, etc.
      database.py           # Database interaction & query logic
      ui/
          __init__.py       # Makes ui a "package" if you add lots of UI files
          client_view.py    # UI logic for the client section
          transactions_view.py 
          reports_view.py   # (for future reporting UI)
      requirements.txt      # Python dependencies
      tests/
          test_client.py
          test_income_records

```

## License

Distributed under the GNU GPLv3 license.  See [LICENSE.txt](license.txt) for details.

