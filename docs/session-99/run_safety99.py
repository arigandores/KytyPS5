"""Shared failure markers for the session-99 launcher and offline scorer; no side effects."""
FAILURE_TOKENS = (
    b'gpuhangabort', b'gpuwaitslow', b'gpumarkerhung', b'gpucheckpointhang',
    b'errordevicelost', b'std::terminate', b'abort()', b'fatal', b'unhandled exception',
)

def failure_marker(line: bytes) -> bool:
    lower = line.lower()
    return any(token in lower for token in FAILURE_TOKENS)
