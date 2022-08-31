# %%

import pathlib
import logging

def __get_log_path(filename):
    p = pathlib.Path(__file__).parent.joinpath(filename)
    return str(p)


def setup_logger(log_filename:str, level:int = logging.DEBUG):
    """setups logger.
    Params:
    - log_filename (str): Log filename without extension."""
    ...
    logFormatter = logging.Formatter("'%(asctime)s - %(message)s")
    logger = logging.getLogger(log_filename)
    logger.setLevel(level)

    fileHandler = logging.FileHandler(__get_log_path(f"{log_filename}.log"), mode="w")
    fileHandler.setFormatter(logFormatter)
    logger.addHandler(fileHandler)

    consolerHandler = logging.StreamHandler()
    consolerHandler.setFormatter(logFormatter)
    logger.addHandler(consolerHandler)

    return logger




if __name__ == "__main__":
    logger = setup_logger("Testlogger")
    logger.debug("THIS IS DEBUG")
    logger.info("THIS IS INFO")
    logger.warning("THIS IS WARNING")
    logger.error("THIS IS ERROR")