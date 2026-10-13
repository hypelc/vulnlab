# VulnLab — Web Security Learning Lab

A hands-on cybersecurity project built with Python, Flask, and SQLite to explore common web application vulnerabilities, implement security mitigations, and verify them with automated regression tests.

VulnLab combines manual security testing with Burp Suite, secure coding practices, pytest, and continuous integration through GitHub Actions.

## Overview

The goal of this project was to understand how common web application vulnerabilities work, investigate their impact in a controlled local environment, implement appropriate fixes, and write automated tests to prevent regressions.

The project covers five vulnerability classes:

- SQL Injection (SQLi)
- Insecure Direct Object Reference (IDOR)
- Reflected Cross-Site Scripting (XSS)
- Path Traversal
- Broken Access Control

After implementing the mitigations, I created a regression test suite with nine tests and configured GitHub Actions to execute them automatically on pushes and pull requests.

**Current status:** Security mitigations implemented, automated tests passing, and CI workflow configured.

## Tech Stack

- **Python** — application logic and security fixes
- **Flask** — web application framework
- **SQLite** — local database
- **pytest** — automated regression testing
- **Burp Suite** — manual HTTP request inspection and testing
- **Git and GitHub** — version control
- **GitHub Actions** — continuous integration

## Security Topics and Mitigations

### 1. SQL Injection (SQLi)

**Risk:** Unsanitized input incorporated into SQL queries can alter query logic and potentially bypass authentication or expose data.

**Mitigation:** Parameterized SQL queries.

```python
query = "SELECT * FROM users WHERE username = ? AND password = ?"
user = conn.execute(query, (username, password)).fetchone()
```

User-supplied values are passed separately from the SQL statement, preventing them from being interpreted as SQL syntax.

**Verification:** An automated test attempts to bypass login using SQL injection input and verifies that authentication is not bypassed.

> Note: The lab's simplified authentication implementation is for educational use. Production applications should store passwords using an appropriate password-hashing algorithm such as Argon2id.

### 2. Insecure Direct Object Reference (IDOR)

**Risk:** An authenticated user may access another user's resources by changing an object identifier in a request.

**Mitigation:** Verify resource ownership in the database query itself.

```sql
SELECT * FROM notes WHERE id = ? AND owner_id = ?
```

The application checks both the requested note ID and the authenticated user's ID.

**Verification:** Tests confirm that a user can access their own note, cannot access another user's note, and is redirected to login when unauthenticated.

### 3. Reflected Cross-Site Scripting (XSS)

**Risk:** Untrusted input rendered as executable HTML or JavaScript can lead to cross-site scripting.

**Mitigation:** Use Jinja2's automatic HTML escaping when rendering user-controlled input.

```html
{{ q }}
```

The application renders the search input as text rather than treating it as executable HTML.

**Verification:** A regression test submits a script-shaped payload and checks that the response contains escaped HTML rather than the raw script markup.

### 4. Path Traversal

**Risk:** An attacker may manipulate a file path to access files outside the intended download directory.

**Mitigation:** Resolve the requested path, verify that it remains inside the permitted base directory, and reject paths that escape that directory.

```python
base_dir = FILES.resolve()
target = (base_dir / filename).resolve()

try:
    target.relative_to(base_dir)
except ValueError:
    abort(403)

if not target.is_file():
    abort(404)
```

**Verification:** An automated test confirms that a traversal attempt targeting a file outside the permitted directory is rejected with HTTP 403.

### 5. Broken Access Control

**Risk:** A user may access administrative functionality without the required privileges.

**Mitigation:** Enforce authentication and role checks on the server using the session and the user's stored role. Query parameters alone must not grant administrative privileges.

**Verification:** Tests confirm that an unauthenticated user is redirected to login, an authenticated non-admin user receives HTTP 403, and an administrator can access the protected page.

## Project Structure

```text
vulnlab/
├── .github/
│   └── workflows/
│       └── tests.yml
├── files/
├── tests/
│   ├── conftest.py
│   ├── broken_access_control_test.py
│   ├── idor_test.py
│   ├── path_traversal_test.py
│   ├── sql_injection_test.py
│   └── xss_test.py
├── .gitignore
├── app.py
├── README.md
├── requirements.txt
└── secret.txt
```

- `app.py` — Flask routes, database initialization, authentication, and security mitigations.
- `files/` — files available to the download functionality.
- `secret.txt` — harmless lab data used to demonstrate the path traversal boundary.
- `tests/` — automated regression tests.
- `tests/conftest.py` — shared pytest fixture that creates an isolated temporary SQLite database for tests.
- `.github/workflows/tests.yml` — GitHub Actions workflow.
- `requirements.txt` — Python application dependencies.

## Getting Started

### Prerequisites

- Python 3.14
- Git
- A terminal
- Optional: Burp Suite Community Edition for manual HTTP testing

The project was tested with Python 3.14.8 and pytest 9.1.1.

### 1. Clone the repository

```bash
git clone https://github.com/hypelc/vulnlab
cd vulnlab
```

### 2. Create a virtual environment

Linux and macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Windows PowerShell:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt pytest
```

### 4. Run the application

```bash
python app.py
```

Open the local address printed by Flask, typically:

```text
http://127.0.0.1:5000
```

Keep the application local. Do not expose this educational lab to the public internet.

### 5. Demo accounts

The application seeds demonstration accounts for local testing.

| Username | Password | Role |
|---|---|---|
| `alice` | `alice123` | Regular user |
| `bob` | `bob123` | Regular user |
| `admin` | `admin123` | Administrator |

These credentials are intentionally simple and are for this lab only. Never reuse them for real accounts.

**Database warning:** The `init_db()` function drops and recreates the lab tables when invoked. Use only the disposable lab database; never point this application at a database containing important data.

## Running the Automated Tests

From the project root, with the virtual environment activated, run:

```bash
python -m pytest -v
```

The test suite currently contains **nine tests** covering the five security topics.

| Test module | What it verifies |
|---|---|
| `broken_access_control_test.py` | Unauthenticated, non-admin, and admin access |
| `idor_test.py` | Resource ownership and authentication requirements |
| `path_traversal_test.py` | Rejection of path traversal attempts |
| `sql_injection_test.py` | SQL injection cannot bypass login |
| `xss_test.py` | HTML input is escaped in the response |

The shared fixture in `conftest.py` uses pytest's temporary directory support and redirects the application to an isolated test database. This prevents tests from depending on the local development database.

The tests use Flask's test client, so they do not require a running web server.

### Example expected output

```text
collected 9 items

...
9 passed
```

## Manual Testing with Burp Suite

The vulnerabilities were investigated in a controlled local environment using HTTP requests and Burp Suite.

A simplified manual testing workflow:

1. Start the Flask application locally.
2. Browse the application and intercept requests using Burp Suite.
3. Inspect parameters, cookies, session behavior, and HTTP responses.
4. Test the relevant security boundary using controlled lab inputs.
5. Implement the mitigation in the application.
6. Repeat the request to verify the expected behavior.
7. Add or run regression tests to check that the fix remains effective.

### Behaviors to verify

- **SQL injection:** Login input must not alter SQL query logic or bypass authentication.
- **IDOR:** A user must not retrieve another user's note by changing the note ID.
- **XSS:** Script-shaped search input must be rendered as escaped text.
- **Path traversal:** A download request must not access files outside the permitted directory.
- **Broken access control:** Changing a query parameter must not grant administrative privileges.

The expected behavior is enforced by the application's security checks and the automated tests.

## Continuous Integration with GitHub Actions

VulnLab uses GitHub Actions to run the regression tests automatically when code is pushed or a pull request is opened or updated.

The workflow:

1. Checks out the repository.
2. Sets up Python 3.14.
3. Installs the application dependencies and pytest.
4. Executes `python -m pytest -v`.

This provides repeatable test execution in a clean Linux environment and helps detect regressions when the application changes.

The workflow's result can be inspected in the repository's **Actions** tab.

## Key Learnings

Through this project, I practiced:

- Identifying common web application vulnerabilities.
- Inspecting HTTP requests and responses with Burp Suite.
- Understanding the difference between authentication and authorization.
- Applying parameterized SQL queries and server-side access checks.
- Using safe HTML rendering and filesystem path validation.
- Building isolated automated tests with pytest.
- Using regression tests to validate security fixes.
- Integrating automated testing into a GitHub Actions CI workflow.

An important takeaway was that implementing a fix is only part of the process. Automated regression tests provide repeatable evidence that the specific behavior being tested remains correct.

## Limitations

VulnLab is an educational project, not a production-ready web application or a comprehensive security assessment tool.

- The test suite covers specific expected behaviors, not every possible attack or application state.
- The authentication and password-storage implementation is simplified for learning.
- Passing the tests does not prove that the entire application is secure.
- Additional production controls, including robust password hashing, CSRF protection where applicable, secure session configuration, logging, and broader security testing, would be necessary before using a comparable application in production.

## Scope and Responsible Use

This project is intended for local learning, defensive development, and authorized security testing.

All manual testing was performed against the local VulnLab application. Do not use these techniques against systems without explicit authorization.

## License

No license has been added yet. If you intend to allow others to reuse, modify, or distribute this project, choose and add an appropriate open-source license.
