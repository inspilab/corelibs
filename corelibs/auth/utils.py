import re
import time

from datetime import datetime


def is_match_with_pattern(list_pattern, path):
    for pattern in list_pattern:
        result = re.search(pattern, path)
        if result:
            return True
    return False
