import sys
import traceback

from polog.core.stores.settings.settings_store import SettingsStore
from polog.utils.json_vars import json_vars


store = SettingsStore()

def get_traceback(cut_string_at_begin=0):
    """
    Получаем последний фрейм трейсбека в виде списка строк и сразу сериализуем этот список в json.
    """
    try:
        json = store['json_module']
        trace = sys.exc_info()[2]
        trace_list = traceback.format_tb(trace)
        trace_list = trace_list[cut_string_at_begin:]
        trace_json = json.dumps(trace_list)
        return trace_json
    except Exception:
        return json.dumps([])

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
