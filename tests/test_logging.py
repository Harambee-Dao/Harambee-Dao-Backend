from app.core.logging import setup_logging
import logging


def test_setup_logging_idempotent():
    # Ensure clean logger so the first call executes full setup path
    root = logging.getLogger()
    for h in list(root.handlers):
        root.removeHandler(h)

    setup_logging()  # sets handler/formatter/level
    # Second call should early-return, covering that branch
    setup_logging()
