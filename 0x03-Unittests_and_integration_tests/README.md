#!/usr/bin/env python3
# Unit Tests and Integration Tests

This project contains unit tests and integration tests for a GitHub organization client.

## Learning Objectives

- Understand the difference between unit and integration tests
- Learn common testing patterns: mocking, parametrization, fixtures
- Practice writing comprehensive test suites
- Master `unittest.mock` for patching external calls

## Requirements

- Python 3.7+
- Ubuntu 18.04 LTS
- pycodestyle 2.5
- parameterized
- requests

## Project Structure

```
0x03-Unittests_and_integration_tests/
├── utils.py              # Utility functions
├── client.py             # GitHub org client
├── fixtures.py           # Test fixtures
├── test_utils.py         # Unit tests for utils
├── test_client.py        # Unit and integration tests for client
└── README.md
```

## Installation

```bash
pip install parameterized requests
```

## Running Tests

### Run all tests
```bash
python -m unittest discover
```

### Run specific test file
```bash
python -m unittest test_utils.py
python -m unittest test_client.py
```

### Run specific test class
```bash
python -m unittest test_utils.TestAccessNestedMap
python -m unittest test_client.TestGithubOrgClient
```

### Run specific test method
```bash
python -m unittest test_utils.TestAccessNestedMap.test_access_nested_map
```

## Test Coverage

### test_utils.py

#### TestAccessNestedMap
- **test_access_nested_map**: Tests `access_nested_map` with various nested structures
  - Input: `{"a": 1}, ("a",)` → Output: `1`
  - Input: `{"a": {"b": 2}}, ("a",)` → Output: `{"b": 2}`
  - Input: `{"a": {"b": 2}}, ("a", "b")` → Output: `2`

- **test_access_nested_map_exception**: Tests KeyError exceptions
  - Input: `{}, ("a",)` → Raises KeyError
  - Input: `{"a": 1}, ("a", "b")` → Raises KeyError

#### TestGetJson
- **test_get_json**: Tests HTTP GET requests with mocked responses
  - Mocks `requests.get` to avoid actual HTTP calls
  - Verifies correct URL is called
  - Verifies correct JSON payload is returned

#### TestMemoize
- **test_memoize**: Tests memoization decorator
  - Verifies method is called only once
  - Verifies cached result is returned on subsequent calls

### test_client.py

#### TestGithubOrgClient
- **test_org**: Tests `GithubOrgClient.org` property with parameterized orgs
  - Tests with "google" and "abc" organizations
  - Mocks `get_json` to avoid API calls

- **test_public_repos_url**: Tests `_public_repos_url` property
  - Mocks `org` property
  - Verifies correct repos URL is returned

- **test_public_repos**: Tests `public_repos` method
  - Mocks `get_json` and `_public_repos_url`
  - Verifies correct repo names are returned
  - Verifies mocks are called correctly

- **test_has_license**: Tests `has_license` static method
  - Tests with matching license
  - Tests with non-matching license

#### TestIntegrationGithubOrgClient
- **Integration tests**: End-to-end testing with fixtures
  - Uses `@parameterized_class` with fixture data
  - Mocks only `requests.get` (external HTTP calls)
  - Tests `public_repos` without filters
  - Tests `public_repos` with license filter

## Key Concepts

### Unit Testing
Tests individual functions in isolation. Mocks all external dependencies.

Example:
```python
@patch('client.get_json')
def test_org(self, mock_get_json):
    # Test only the org method logic
    # Mock get_json to avoid HTTP calls
```

### Integration Testing
Tests multiple components working together. Only mocks external calls (HTTP, DB, etc).

Example:
```python
@classmethod
def setUpClass(cls):
    # Mock only requests.get
    # Let all internal methods work together
    cls.get_patcher = patch('requests.get')
```

### Mocking
Replacing real objects with mock objects to control behavior.

```python
with patch('module.function') as mock_func:
    mock_func.return_value = "test"
    # function now returns "test"
```

### Parametrization
Running same test with different inputs.

```python
@parameterized.expand([
    ("input1", "expected1"),
    ("input2", "expected2"),
])
def test_function(self, input_val, expected):
    self.assertEqual(function(input_val), expected)
```

### Fixtures
Predefined test data used across multiple tests.

```python
TEST_PAYLOAD = [
    (org_payload, repos_payload, expected_repos, apache2_repos)
]
```

## Testing Patterns

### 1. Mock External Calls
```python
@patch('requests.get')
def test_get_json(self, mock_get):
    mock_get.return_value.json.return_value = {"key": "value"}
    # Now requests.get is mocked
```

### 2. Mock Properties
```python
with patch.object(MyClass, 'my_property', new_callable=PropertyMock) as mock_prop:
    mock_prop.return_value = "test"
    # Property is now mocked
```

### 3. Assert Mock Calls
```python
mock_function.assert_called_once()
mock_function.assert_called_once_with("expected_arg")
mock_function.assert_called()
```

### 4. Parameterized Tests
```python
@parameterized.expand([
    (input1, expected1),
    (input2, expected2),
])
def test_function(self, input_val, expected):
    self.assertEqual(function(input_val), expected)
```

### 5. Class-level Fixtures
```python
@classmethod
def setUpClass(cls):
    cls.patcher = patch('module.function')
    cls.patcher.start()

@classmethod
def tearDownClass(cls):
    cls.patcher.stop()
```

## Example Test Run

```bash
$ python -m unittest test_utils.py
........
----------------------------------------------------------------------
Ran 8 tests in 0.002s

OK

$ python -m unittest test_client.py
........
----------------------------------------------------------------------
Ran 8 tests in 0.003s

OK
```

## Common Errors and Solutions

### Error: `ModuleNotFoundError: No module named 'parameterized'`
**Solution**: `pip install parameterized`

### Error: `AssertionError: Expected 'mock' to have been called once...`
**Solution**: Check that you're using the correct assertion method and that the mock is being called

### Error: `KeyError` in nested map access
**Solution**: Ensure the path exists in the nested structure

## Documentation

All modules, classes, and functions have proper documentation:

```bash
python3 -c 'print(__import__("utils").__doc__)'
python3 -c 'print(__import__("utils").access_nested_map.__doc__)'
python3 -c 'print(__import__("client").GithubOrgClient.__doc__)'
```

## Style

All code follows pycodestyle (version 2.5):

```bash
pycodestyle utils.py client.py test_utils.py test_client.py
```

## Type Annotations

All functions are type-annotated:

```python
def access_nested_map(nested_map: Mapping, path: Sequence) -> Any:
    """Access nested map with key path."""
    ...
```

## Author

ALX Software Engineering Program

## License

MIT License
