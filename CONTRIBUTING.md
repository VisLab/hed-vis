# Contributing to HEDTools

Thank you for your interest in contributing to HED visualization! This document provides guidelines and instructions for contributing to the project.

## Table of contents

- [Code of conduct](#code-of-conduct)
- [How can I contribute?](#how-can-i-contribute)
- [Coding standards](#coding-standards)
- [Testing guidelines](#testing-guidelines)
- [Pull request process](#pull-request-process)
- [Reporting bugs](#reporting-bugs)
- [Suggesting enhancements](#suggesting-enhancements)

## Code of conduct

This project adheres to a code of conduct that we expect all contributors to follow. Please be respectful and constructive in all interactions.

## How can I contribute?

### Types of contributions

- **Bug reports:** Help us identify and fix issues
- **Feature requests:** Suggest new functionality
- **Code contributions:** Submit bug fixes or new features
- **Documentation:** Improve guides, examples, or API docs
- **Testing:** Add test coverage or report test failures
- **Examples:** Share use cases and example code

## Coding standards

### Python style guide

- Follow [PEP 8](https://pep8.org/) style guidelines
- Maximum line length: 120 characters
- Use descriptive variable and function names
- Add docstrings to all public classes and functions

### Code quality tools

We use several tools to maintain code quality:

- **black:** For automatic code formatting

  ```bash
  # Check if code is formatted correctly
  black --check .

  # Automatically format all code
  black .

  # Format specific files or directories
  black hed/ tests/

  # Windows: Use --workers 1 if you encounter file I/O errors
  black --workers 1 .
  ```

- **ruff:** For linting, style checking, and import sorting

  ```bash
  ruff check hed/ tests/
  ```

  To automatically fix issues:

  ```bash
  ruff check --fix hed/ tests/
  ```

- **typos:** For spell checking

  ```bash
  typos
  ```

### Documentation style

- Use Google-style docstrings for all public APIs
- Include type hints where appropriate
- Provide examples for complex functionality

Example docstring:

```python
def validate_hed_string(hed_string, schema) -> list[dict]:
    """Validate a HED string against a schema.

    Parameters:
        hed_string (str): The HED string to validate.
        schema (HedSchema): The schema to validate against.

    Returns:
        list: A list of validation issues, empty if valid.

    Example:
        >>> schema = load_schema_version('8.4.0')
        >>> issues = validate_hed_string("Event", schema)
        >>> if not issues:
        ...     print("Valid!")
    """
    pass
```

## Testing guidelines

### Test structure

- Place tests in the `tests/` directory, mirroring the `hed/` structure
- Name test files with `test_` prefix
- Use descriptive test method names

### Writing tests

- Each test should be independent and isolated
- Use unittest framework (the project standard)
- Test both success and failure cases
- Include edge cases

Example test:

```python
import unittest
from hed import HedString, load_schema


class TestHedValidation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema = load_schema_version("8.4.0")

    def test_valid_hed_string(self):
        hed_string = HedString("Event", self.schema)
        issues = hed_string.validate()
        self.assertEqual(len(issues), 0)

    def test_invalid_hed_string(self):
        hed_string = HedString("InvalidTag", self.schema)
        issues = hed_string.validate()
        self.assertGreater(len(issues), 0)


if __name__ == "__main__":
    unittest.main()
```

### Running tests

Run all tests:

```bash
python -m unittest discover tests
```

Run specific test file:

```bash
python -m unittest tests/models/test_hed_string.py
```

Run specific test case:

```bash
python -m unittest tests.models.test_hed_string.TestHedString.test_constructor
```

## Pull request process

### Initial setup (one-time only)

**Important:** You cannot push directly to `hed-standard/hed-vis`. All contributions must come through pull requests from your personal fork.

1. **Fork the repository on GitHub:**

   - Go to https://github.com/hed-standard/hed-vis
   - Click the "Fork" button in the top-right corner
   - This creates a copy at `https://github.com/YOUR_USERNAME/hed-vis`

2. **Clone your fork to your local machine:**

   ```bash
   git clone https://github.com/YOUR_USERNAME/hed-vis.git
   cd hed-vis
   ```

   This creates a local copy with `origin` pointing to your fork.

3. **Add the upstream repository:**

   ```bash
   git remote add upstream https://github.com/hed-standard/hed-vis.git
   ```

   Now you have two remotes:

   - `origin`: your fork (where you push your changes)
   - `upstream`: the official repo (where you pull updates from)

   Verify with:

   ```bash
   git remote -v
   ```

### Making a contribution

Follow these steps each time you want to contribute:

1. **Sync your fork with the latest upstream changes:**

   ```bash
   # Switch to your main branch
   git checkout main

   # Fetch the latest changes from upstream
   git fetch upstream

   # Merge upstream's main into your local main
   git merge upstream/main

   # Push the updates to your fork on GitHub
   git push origin main
   ```

2. **Create a feature branch:**

   ```bash
   git checkout -b feature/your-feature-name
   ```

   Always create your feature branch from an up-to-date main branch.

3. **Make your changes** with clear, focused commits

4. **Run tests and checks:**

   ```bash
   # Run all tests
   python -m unittest discover tests

   # Check code style
   ruff check hedvis/ tests/
   ```

5. **Write descriptive commit messages:**

   ```
   Add validation for temporal extent

   - Implement temporal extent validation logic
   - Add unit tests for temporal validation
   - Update documentation with temporal examples
   ```

6. **Push your feature branch to your fork:**

   ```bash
   git push origin feature/your-feature-name
   ```

   This pushes to `YOUR_USERNAME/hed-vis`, not to `hed-standard/hed-vis`.

7. **Create a pull request on GitHub:**

   - Go to https://github.com/YOUR_USERNAME/hed-vis
   - GitHub will show a banner suggesting to create a PR for your recently pushed branch
   - Click "Compare & pull request"
   - Or click "Pull requests" → "New pull request" → "compare across forks"
   - Ensure:
     - Base repository: `hed-standard/hed-vis`
     - Base branch: `main`
     - Head repository: `YOUR_USERNAME/hed-vis`
     - Compare branch: `feature/your-feature-name`
   - Fill out the PR template completely
   - Link related issues
   - Add meaningful description of changes
   - Click "Create pull request"

### After submitting your PR

- A maintainer will review your PR within a few days
- If changes are requested:
  - Make the changes locally on your feature branch
  - Commit and push to the same branch: `git push origin feature/your-feature-name`
  - The PR will automatically update with your new commits
- Once approved, a maintainer will merge your PR
- After merge:
  - Delete your feature branch: `git branch -d feature/your-feature-name`
  - Sync your main again (repeat step 1 above)

### Keeping your PR up to date

If upstream's main branch changes while your PR is open:

```bash
# Switch to your main branch
git checkout main

# Sync with upstream
git fetch upstream
git merge upstream/main
git push origin main

# Switch back to your feature branch
git checkout feature/your-feature-name

# Merge the updated main into your feature branch
git merge main

# Push the updates
git push origin feature/your-feature-name
```

## Reporting bugs

### Before submitting a bug report

- Check the [existing issues](https://github.com/hed-standard/hed-vis/issues)
- Update to the latest version
- Verify the bug is reproducible

### How to submit a bug report

Create an issue with:

1. **Clear title** describing the problem
2. **Environment details:** OS, Python version, hedtools version
3. **Steps to reproduce** the issue
4. **Expected behavior**
5. **Actual behavior**
6. **Code sample** demonstrating the problem (if applicable)
7. **Error messages** or stack traces

Example:

````markdown
## Bug: Schema validation fails with custom schema

**Environment:**
- OS: Ubuntu 22.04
- Python: 3.10.5
- hedtools: 0.5.0

**Steps to Reproduce:**
1. Load custom schema from file
2. Validate HED string with tag "Event"
3. Observe error

**Expected:** Validation succeeds
**Actual:** Raises KeyError

**Code:**
\```python
from hed import load_schema, HedString
schema = load_schema('/path/to/schema.xml')
hed = HedString("Event")
issues = hed.validate(schema)  # KeyError here
\```

**Error:**
\```
KeyError: 'Event'
  at line 123 in validator.py
\```
````

## Suggesting enhancements

### How to suggest an enhancement

Create an issue with:

1. **Clear title** describing the enhancement
2. **Use case:** Why is this enhancement needed?
3. **Proposed solution:** How should it work?
4. **Alternatives considered:** Other approaches you've thought about
5. **Additional context:** Screenshots, mockups, or examples

## Questions?

- **Repo docs:** [https://www.hedtags.org/hed-vis](https://www.hedtags.org/hed-vis)
- **HED docs:** [https://www.hedtags.org/hed-resources](https://www.hedtags.org/hed-resources)
- **Issues:** [GitHub Issues](https://github.com/hed-standard/hed-vis/issues)
- **Questions or ideas:** [HED organization discussions](https://github.com/orgs/hed-standard/discussions)
- **Email:** [hed.maintainers@gmail.com](mailTo:hed.maintainers@gmail.com)

Thank you for contributing to HED visualization tools!
