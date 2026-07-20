"""
Logging Configuration
"""

import logging

from .config import LOG_DIR

LOG_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(

    filename=LOG_DIR / "processing_log.txt",

    level=logging.INFO,

    format="%(asctime)s | %(levelname)s | %(message)s"

)

logger = logging.getLogger("EnterprisePipeline")