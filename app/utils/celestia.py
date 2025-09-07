import logging
from app.core.config import settings

logger = logging.getLogger(__name__)


def anchor_hash(root_hash: str) -> bool:
    logger.info("Anchoring hash %s to Celestia at %s", root_hash, settings.CELESTIA_ENDPOINT)
    return True
