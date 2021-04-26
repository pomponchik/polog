import sys
import traceback
import ujson as json
from polog.utils.json_vars import get_item
from polog.utils.json_vars import json_vars


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
        try:
            local_variables = trace.tb_next.tb_frame.f_locals
        except:
            local_variables = trace.tb_frame.f_locals
        local_variables_json = json_vars(**local_variables)
        return local_variables_json
    except Exception as e:
        return ''
