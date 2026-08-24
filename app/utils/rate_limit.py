from time import time

_login_attempts: dict[str, list[float]] = {}


def check_login_rate_limit(key: str, max_attempts: int, window_seconds: int) -> bool:
    now = time()
    attempts = _login_attempts.get(key, [])

    attempts = [timestamp for timestamp in attempts if now - timestamp < window_seconds]

    return len(attempts) < max_attempts


def record_login_attempt(key: str) -> None:
    now = time()

    if key not in _login_attempts:
        _login_attempts[key] = []

    _login_attempts[key].append(now)


def reset_login_attempts(key: str) -> None:

    _login_attempts.pop(key, None)
