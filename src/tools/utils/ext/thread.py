import asyncio
import threading
from sgtpyutils.logger import logger


class SyncRunner(threading.Thread):

    def __init__(self, async_task) -> None:
        self.tasks = async_task
        self.semaphore = threading.Semaphore(0)
        super().__init__(daemon=True)

    def run(self):
        # 创建一个新任务方式
        # loop = asyncio.new_event_loop()
        # self.result = loop.run_until_complete(loop.create_task(self.tasks))
        # self.result = asyncio.run()
        # loop.close()

        try:
            self.result = asyncio.run(self.tasks)
        except Exception as ex:
            self.result = None
            logger.warning(f'fail in running{self.tasks}.Exception:{ex}')
        self.semaphore.release()
        return super().run()

    @staticmethod
    def as_sync_method(async_method):
        x = SyncRunner(async_method)
        x.start()
        x.semaphore.acquire()
        result = x.result
        return result


if __name__ == '__main__':
    async def async_method():
        await asyncio.sleep(10)
        return 1

    print(SyncRunner.as_sync_method(async_method))
