"""
Process utilities: centralized subprocess helpers with consistent timeouts and logging.
Migration target: replace scattered subprocess.run calls with run_cmd for uniform behavior.
"""

import subprocess


def run_cmd(argv: list[str], timeout: int = 10, text: bool = True) -> tuple[int, str, str]:
    """Run a command safely; return (code, stdout, stderr).

    - No shell=True usage.
    - Enforces timeout.
    """
    try:
        result = subprocess.run(argv, check=False, capture_output=True, timeout=timeout, text=text)
        return result.returncode, result.stdout or "", result.stderr or ""
    except subprocess.TimeoutExpired:
        return 124, "", f"Timeout after {timeout}s: {' '.join(argv)}"
    except FileNotFoundError:
        return 127, "", f"Not found: {argv[0]}"
    except Exception as e:
        return 1, "", str(e)
