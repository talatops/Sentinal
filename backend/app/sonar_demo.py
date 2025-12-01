"""Intentional SonarQube demo issues.

This module is NOT used by the application at runtime.
It only exists so SonarQube has a few easy findings to
show in dashboards and so we can verify the Sentinel
integration end‑to‑end.
"""


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
