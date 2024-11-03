import logging

def configure_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.ERROR)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.ERROR)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(funcName)s - %(message)s')
    console_handler.setFormatter(formatter)

    logger.addHandler(console_handler)

configure_logging()

