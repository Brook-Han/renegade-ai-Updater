# logger.py
import logging
import sys

def setup_logging(name="renegade_radar", level=logging.INFO):
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger   # 避免重复添加 handler
    
    logger.setLevel(level)
    
    # 控制台 handler（简洁格式）
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s', datefmt='%H:%M:%S'))
    logger.addHandler(console_handler)
    
    # 文件 handler（详细日志，用于事后排查）
    log_path = Path(__file__).parent / "radar.log"
    file_handler = logging.FileHandler(log_path, encoding='utf-8')
    file_handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(name)s: %(message)s'))
    logger.addHandler(file_handler)
    
    return logger

# 全局 logger 实例
logger = setup_logging()