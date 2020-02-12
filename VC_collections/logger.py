import logging
from pathlib import Path


# class VC_Logger(logging.LoggerAdapter):

# def __init__(self, branch, collection_id):
def initialize_logger(branch, collection_id):
    """
        Set up logging to file and console.
    :param branch:
    :param collection_id:
    """

    reports_path = (
            Path.cwd().parent.parent / ("VC-" + branch) / collection_id / "Data" / "reports"
    )

    logging.basicConfig(
        level=logging.DEBUG,
        filename=reports_path / (collection_id + ".log"),
        format="%(asctime)s %(name)-12s %(levelname)-8s %(message)s",
        datefmt="%y-%m-%d %H:%M",
    )
    # logging.basicConfig(level=logging.INFO,
    #                     format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
    #                     datefmt='%y-%m-%d %H:%M',
    #                     )

    # setup logging file handler
    dt_fmt = "%y-%m-%d %H:%M"
    file_handler = logging.FileHandler(filename=reports_path / (collection_id + ".log"))
    file_handler.setFormatter(
        logging.Formatter(
            "[{levelname}] {asctime}s {name}  {message}", dt_fmt, style="{"
        )
    )
    logging.getLogger().addHandler(file_handler)

    # setup logging console handler
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)
    stream_handler.setFormatter(
        logging.Formatter("[{levelname}] {name}  {message}", style="{")
    )
    logging.getLogger().addHandler(stream_handler)
