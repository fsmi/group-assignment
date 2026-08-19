import logging
from pathlib import Path

from .schemas import InputSchema, OutputSchema

logger = logging.getLogger(__name__)


def write_output_file(path: Path, output: OutputSchema) -> None:
    logger.info(f"Writing output file '{path}'")
    path.write_text(output.model_dump_json(indent=4), encoding="utf-8")


def write_input_file(path: Path, input_data: InputSchema) -> None:
    logger.info(f"Writing input file '{path}'")
    path.write_text(input_data.model_dump_json(indent=4), encoding="utf-8")
