import asyncio as aio


def wait_signals(*signals):
    loop = aio.get_running_loop()
    future = loop.create_future()

    def handler():
        future.set_result(None)
        for signal in signals:
            loop.remove_signal_handler(signal)

    for signal in signals:
        loop.add_signal_handler(signal, handler)

    return future
