from threading import Thread
import asyncio

class MyThread(Thread):
    def __init__(self, func, args):
        super(MyThread, self).__init__()
        self.func = func
        self.args = args

    def run(self):
        try:
            self.result = self.func(*self.args)
        except Exception as e:
            raise e

    def get_result(self):
        try:
            return self.result
        except Exception:
            return None

async def run_withaio(func, args):
    try:
        t1 = MyThread(func, args)
        t1.start()
        while t1.is_alive():
            await asyncio.sleep(0.05)
        return t1.get_result()
    except Exception as e:
        raise e