import sys
import traceback
import ujson as json
from polog.utils.json_vars import get_item


def get_traceback():
    """
    Получаем последний фрейм трейсбека в виде списка строк и сразу сериализуем этот список в json.
    """
    trace = sys.exc_info()[2]
    trace_list = traceback.format_tb(trace)
    trace_json = json.dumps(trace_list)
    return trace_json

def get_locals_from_traceback():
    """
    Забираем из последнего фрейма трейсбека локальные переменные и упаковываем их в json.
    """
    trace = sys.exc_info()[2]
    try:
        local_variables = {key: get_item(value) for key, value in trace.tb_next.tb_frame.f_locals.items()}
        local_variables_json = json.dumps(local_variables)
        return local_variables_json
    except:
        return ''
