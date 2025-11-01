# ecommerce-playground-tests

Selenium + pytest test suite for the demo store.

Prereqs
- Python 3.8+
- pip

From Powershell: 

python -m venv .venv

. .venv\Scripts\Activate.ps1

python -m pip install --upgrade pip setuptools wheel

pip install -r requirements.txt

pip install selenium pytest


Run
- Run all tests (headless by default):
```
pytest
```

- Run a single test file:
```
 python -m pytest ecommerce-playground-tests/tests/test_homepage.py -q -s
```
