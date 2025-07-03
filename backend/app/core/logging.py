import logging
import sys
from loguru import logger

def setup_logging():
    """Setup logging configuration"""
    # Configure loguru
    logger.remove()
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="INFO",
    )
    
    # Intercept standard logging
    class InterceptHandler(logging.Handler):
        def emit(self, record):
            logger_opt = logger.opt(depth=6, exception=record.exc_info)
            logger_opt.log(record.levelno, record.getMessage())
    
    logging.basicConfig(handlers=[InterceptHandler()], level=0)