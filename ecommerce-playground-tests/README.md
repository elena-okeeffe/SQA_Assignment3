# ecommerce-playground-tests

Cross-platform Selenium + pytest test suite for the demo store.

Prereqs
- Python 3.8+
- pip

Install
```
pip install -r requirements.txt
```

Run
- Run all tests (headless by default):
```
pytest
```

- Run a single test file:
```
pytest tests/test_search.py -q -s
```

Environment variables
- EP_BASE_URL : override the base URL (default: the LambdaTest playground site)
- EP_BROWSER : choose browser: `chrome` or `firefox` (default runs both via param fixture)
- EP_HEADLESS : `0` to disable headless mode, any other value or unset to enable headless
