# ecommerce-playground-tests

Selenium + pytest test suite for the demo store.

Prereqs
- Python 3.8+
- pip

option from powershell:
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

Environment variables
- EP_BASE_URL : override the base URL (default: the LambdaTest playground site)
- EP_BROWSER : choose browser: `chrome` or `firefox` (default runs both via param fixture)
- EP_HEADLESS : `0` to disable headless mode, any other value or unset to enable headless
