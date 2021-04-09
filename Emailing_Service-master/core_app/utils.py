from datetime import datetime, timedelta
import logging
import os
import pathlib

from django.utils import timezone


def get_this_week():
    """
    Get the week start, end in format "d-m_d-m"
    :return:
    """
    start_of_week = datetime.now() - timedelta(days=datetime.now().weekday())
    end_of_week = start_of_week + timedelta(days=6)
    return '_'.join(map(lambda x: x.strftime('%d-%m'), (start_of_week, end_of_week)))


def logging_config(submodule):
    """
    Naming pattern of log file: /logs/{submodule}/log_{week_str}.txt
    """
    week_str = get_this_week()
    logfile_path = os.path.join('logs', submodule, f"log_{week_str}.txt")
    if not os.path.isfile(logfile_path):
        dir_path = f"{os.sep}".join(logfile_path.split(os.sep)[:-1])
        pathlib.Path(dir_path).mkdir(parents=True, exist_ok=True)
        with open(logfile_path, 'a') as file_buffer:
            file_buffer.write('')
    return logging.basicConfig(filename=logfile_path, filemode='a', format=f"{timezone.now()} %(message)s", level='DEBUG')
