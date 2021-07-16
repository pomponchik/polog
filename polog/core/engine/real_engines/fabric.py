from polog.core.engine.real_engines.multithreaded.writer import MultiThreadedRealEngine
from polog.core.engine.real_engines.singlethreaded.writer import SingleThreadedRealEngine


def real_engine_fabric(settings):
    if settings['pool_size'] == 0:
        return SingleThreadedRealEngine(settings)
    return MultiThreadedRealEngine(settings)
