import logging
import tomllib
from pathlib import Path

from .schemas import ConfigSchema, InputSchema, OutputSchema

logger = logging.getLogger(__name__)


def parse_config_file(path: Path) -> ConfigSchema:
    logger.info(f"Reading config file '{path}'")
    with path.open("rb") as file:
        data = tomllib.load(file)
    logger.info("Parsing and validating TOML")
    return ConfigSchema.model_validate(data)


def parse_input_file(path: Path) -> InputSchema:
    logger.info(f"Reading input file '{path}'")
    text = path.read_text(encoding="utf-8")
    logger.info("Parsing and validating JSON")
    return InputSchema.model_validate_json(text)


def parse_output_file(path: Path) -> OutputSchema:
    logger.info(f"Reading output file '{path}'")
    text = path.read_text(encoding="utf-8")
    logger.info("Parsing and validating JSON")
    return OutputSchema.model_validate_json(text)
