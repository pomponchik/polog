import sys
import traceback
import ujson as json


def get_traceback_string():
    trace = sys.exc_info()[2]
    trace_list = traceback.format_tb(trace)
    trace_json = json.dumps(trace_list)
    return trace_json
