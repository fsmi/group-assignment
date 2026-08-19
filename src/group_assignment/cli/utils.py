import logging


def configure_logging(verbose: bool = False) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging_format = (
        "[%(levelname)s][%(name)s:%(lineno)d] %(message)s"
        if verbose
        else "[%(levelname)s] %(message)s"
    )
    logging.basicConfig(level=level, format=logging_format)
