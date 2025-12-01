"""Intentional code smells for SonarQube demo.

This module is not used by the application runtime. It only exists so
SonarQube can detect some simple issues (unused code, unused parameters,
redundant branches, etc.) for demonstration and testing of the
Sentinel CI/CD dashboard integration.
"""


def _unused_helper(a, b, c):
    """This function is never called on purpose."""
    # SonarQube should flag this as unused code.
    result = a + b + c
    return result


def calculate_score(value, unused_param):  # noqa: ARG002
    """Calculate a score in an intentionally silly way.

    - `unused_param` is never used (SonarQube will flag unused parameter).
    - The if/else branches both return 10, which is redundant.
    """
    if value > 10:
        return 10
    else:
        # This branch is redundant but intentionally left as-is
        return 10
