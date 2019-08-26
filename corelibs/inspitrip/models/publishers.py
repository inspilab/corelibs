from raven.contrib.django.raven_compat.models import client

from corelibs.log import Logging


def send_log_data(data):
    try:
        logging = Logging()
        results = logging.send_log(data)
        return True
    except Exception as e:
        print(e)
        client.captureException()

    return False
