# 🔍 Unit Testing Overview: `test_utils.py`

This repository focuses on unit testing for the `access_nested_map` function in `utils.py`. It is part of the ALX Backend Python coursework under the `0x03-Unittests_and_integration_tests` module.

---

## 📂 Project Layout

alx-backend-python/
└── 0x03-Unittests_and_integration_tests/
    ├── utils.py
    ├── test_utils.py
    └── __pycache__
---

## 🧠 Objective

The goal is to ensure that `access_nested_map` operates reliably by applying unit tests using Python’s `unittest` module along with the `parameterized` testing helper.

Specifically, the tests check:
- Proper retrieval of deeply nested values.
- Expected failure (via `KeyError`) when invalid keys are provided.

---

##  Test Coverage

### `test_access_nested_map`
Verifies that values within nested dictionaries are accessed accurately.

**Test Scenarios:**
- `{"x": 100}`, path `("x",)` returns `100`
- `{"x": {"y": 200}}`, path `("x", "y")` returns `200`

---

### `test_access_nested_map_exception`
Ensures the function raises appropriate exceptions when invalid keys are used.

**Test Scenarios:**
- `{}`, path `("missing",)` raises `KeyError: 'missing'`
- `{"x": {"y": 200}}`, path `("x", "z")` raises `KeyError: 'z'`

---

##  Running the Tests

From inside the `0x03-Unittests_and_integration_tests` folder, execute either of the following commands:

```bash
# Run all tests using unittest discovery mode
python -m unittest test_utils.py

# Or invoke the test script directly
python test_utils.py
