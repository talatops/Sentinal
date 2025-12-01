"""Intentional SonarQube demo issues.

This module is NOT used by the application at runtime.
It only exists so SonarQube has a few easy findings to
show in dashboards and so we can verify the Sentinel
integration end‑to‑end.

WARNING: This file contains intentional security vulnerabilities
and code smells for demonstration purposes only.
"""

import os
import subprocess
import random
import pickle
import hashlib
import base64


def _dead_code_example(x, y):
    """Completely unused function (dead code)."""
    # SonarQube should flag this as unused code / dead code
    total = x + y
    total += 1  # pointless operation
    return total


def format_user_v1(name, email):
    """First version of a formatter."""
    return f"User: {name} <{email}>"


def format_user_v2(name, email):
    """Intentional duplicate of v1 so SonarQube detects duplication."""
    # The body is intentionally identical to format_user_v1
    return f"User: {name} <{email}>"


def noisy_score(value, unused_flag=False):  # noqa: ARG002
    """Overly complex and noisy logic just for SonarQube.

    - `unused_flag` is never used (unused parameter)
    - the branching is redundant and could be simplified
    """
    score = 0
    if value > 0:
        if value > 10:
            score = 10
        else:
            score = 5
    else:
        if value == 0:
            score = 0
        else:
            score = -1

    # Redundant re-mapping of score (code smell)
    if score == 10:
        return 10
    elif score == 5:
        return 5
    elif score == 0:
        return 0
    else:
        return -1


# ============================================================================
# INTENTIONAL SECURITY VULNERABILITIES (for SonarQube detection)
# ============================================================================

def hardcoded_secret_example():
    """INTENTIONAL: Hardcoded password/secret - SonarQube should flag this."""
    password = "admin123"  # noqa: S105
    api_key = "sk_live_51H3r3_1s_4_h4rdc0d3d_k3y"  # noqa: S105
    db_password = "postgres:password123"  # noqa: S105
    return {"password": password, "api_key": api_key, "db_password": db_password}


def sql_injection_vulnerability(user_input):
    """INTENTIONAL: SQL injection vulnerability - never use string formatting for SQL."""
    # SonarQube should flag this as a security hotspot
    query = f"SELECT * FROM users WHERE username = '{user_input}'"  # noqa: S608
    # This is vulnerable to SQL injection attacks
    return query


def command_injection_vulnerability(user_input):
    """INTENTIONAL: Command injection vulnerability."""
    # SonarQube should flag this as a security vulnerability
    os.system(f"echo {user_input}")  # noqa: S605
    subprocess.call(f"ls -la {user_input}", shell=True)  # noqa: S602, S604
    return "Command executed"


def path_traversal_vulnerability(filename):
    """INTENTIONAL: Path traversal vulnerability."""
    # SonarQube should flag this as a security vulnerability
    file_path = f"/var/www/uploads/{filename}"  # noqa: S108
    with open(file_path, "r") as f:  # noqa: S108
        return f.read()


def insecure_random_example():
    """INTENTIONAL: Insecure random number generation."""
    # SonarQube should flag this - use secrets module instead
    insecure_token = random.randint(1000, 9999)  # noqa: S311
    insecure_id = random.choice(["a", "b", "c"])  # noqa: S311
    return {"token": insecure_token, "id": insecure_id}


def weak_cryptography_example(password):
    """INTENTIONAL: Weak cryptography - MD5 is insecure."""
    # SonarQube should flag MD5 as weak hashing algorithm
    hash_value = hashlib.md5(password.encode()).hexdigest()  # noqa: S324
    return hash_value


def insecure_deserialization_example(data):
    """INTENTIONAL: Insecure deserialization vulnerability."""
    # SonarQube should flag pickle.loads as insecure
    decoded = base64.b64decode(data)
    obj = pickle.loads(decoded)  # noqa: S301
    return obj


def xss_vulnerability_example(user_input):
    """INTENTIONAL: XSS vulnerability - unescaped user input."""
    # SonarQube should flag this as a security hotspot
    html = f"<div>{user_input}</div>"  # noqa: S703
    return html


def missing_input_validation(user_input):
    """INTENTIONAL: Missing input validation."""
    # SonarQube should flag missing validation
    result = user_input.upper()  # No validation before processing
    return result


def hardcoded_ip_address():
    """INTENTIONAL: Hardcoded IP address."""
    # SonarQube may flag this as a code smell
    server_ip = "192.168.1.100"  # noqa: S104
    return server_ip


def empty_except_block():
    """INTENTIONAL: Empty except block - bad practice."""
    try:
        result = 1 / 0
    except:  # noqa: E722, S110
        pass  # SonarQube should flag empty except blocks
    return result


def use_of_eval(user_input):
    """INTENTIONAL: Use of eval() - security risk."""
    # SonarQube should flag this as a critical security vulnerability
    result = eval(user_input)  # noqa: S307
    return result


def weak_ssl_tls_example():
    """INTENTIONAL: Weak SSL/TLS configuration."""
    # SonarQube should flag this as a security hotspot
    import ssl
    context = ssl.create_default_context()
    context.check_hostname = False  # noqa: S501
    context.verify_mode = ssl.CERT_NONE  # noqa: S501
    return context


def information_disclosure_example():
    """INTENTIONAL: Information disclosure - exposing sensitive data."""
    # SonarQube should flag this as a security hotspot
    error_message = f"Database error: Connection failed to {hardcoded_secret_example()['db_password']}"  # noqa: S105
    return error_message
