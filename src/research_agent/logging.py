"""
Hệ thống con ghi nhật ký có cấu trúc (ADR-0001, RC-18)
"""

import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional
from research_agent.config import WorkspaceConfig, get_default_config


class JsonFormatter(logging.Formatter):
    """Định dạng bản ghi nhật ký dưới dạng dòng JSON có cấu trúc."""

    def format(self, record: logging.LogRecord) -> str:
        log_data: Dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "component": record.name,
            "message": record.getMessage(),
        }
        if hasattr(record, "artifact_id"):
            log_data["artifact_id"] = record.artifact_id
        if hasattr(record, "operation"):
            log_data["operation"] = record.operation
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_data)


def configure_logging(
    config: Optional[WorkspaceConfig] = None,
    log_level: int = logging.INFO,
    log_to_file: bool = True
) -> logging.Logger:
    """Khởi tạo logger có cấu trúc cho hệ thống nghiên cứu."""
    cfg = config or get_default_config()
    logger = logging.getLogger("research_agent")
    logger.setLevel(log_level)
    logger.handlers.clear()

    # Trình xử lý bảng điều khiển (Con người có thể đọc được với sự hỗ trợ UTF-8)
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")
        except Exception:
            pass
    console_handler = logging.StreamHandler(sys.stdout)
    console_fmt = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    console_handler.setFormatter(console_fmt)
    logger.addHandler(console_handler)

    # Trình xử lý tệp (Dòng JSON có cấu trúc)
    if log_to_file:
        cfg.ensure_directories()
        log_file = cfg.logs_dir / "research_system.jsonl"
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(JsonFormatter())
        logger.addHandler(file_handler)

    return logger


def get_logger(name: str = "research_agent") -> logging.Logger:
    """Truy xuất phiên bản logger."""
    return logging.getLogger(name)
