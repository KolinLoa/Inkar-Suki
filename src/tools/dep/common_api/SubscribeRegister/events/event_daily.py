# from src.plugins.jx3.daily import daily_ # 产生循环调用风险
from src.tools.dep.common_api.none_dep_api import *
from ..SubscribeItem import *
import threading
import time
import os
from src.tools.dep.bot import *
from src.tools.dep.data_server import *


class IDailyMessage:
    lock = threading.RLock()
    CACHE_Daily: dict[str, str]  # day -> url_local

    def __init__(self, date: str, group_id: str, cron: SubjectCron, offset: int = 0) -> None:
        server = server_mapping(None, group_id)
        key = f"daily_{date}@{server}"
        self.key = key
        self.date = date
        self.group_id = group_id
        self.server = server
        self.cron = cron
        self.offset = offset

    async def get_message(self):
        with PlainTxtDailyMessage.lock:
            return await self._get_daily_message()

    async def _get_daily_message(self):
        ...


class ImgDailyMessage(IDailyMessage):
    CACHE_Daily: dict[str, str] = filebase_database.Database(
        f'{bot_path.common_data_full}daily-img',
    ).value

    def get_path(self, filename: str) -> str:
        return f'{bot_path.DATA}{os.sep}res{os.sep}daily{filename}'

    async def _get_daily_message(self):
        path_cache_daily = ImgDailyMessage.CACHE_Daily.get(self.key)
        target = None
        has_cache = bool(path_cache_daily)
        if not has_cache:
            # 注意销毁今天以前的缓存
            url = await daily_(self.server, self.group_id, self.offset)  # 向后预测1天的
            img_data = (await send_with_async('get', url)).content
            path_cache_daily = f"{self.key}.png"

        target = Path(self.get_path(path_cache_daily))

        if not has_cache:
            if not os.path.exists(target.parent.as_posix()):
                os.makedirs(target.parent.as_posix())
            with open(target.as_posix(), "wb") as f:
                f.write(img_data)
            ImgDailyMessage.CACHE_Daily[self.key] = path_cache_daily

        message = f"{ms.image(target.as_uri())}{self.cron.notify_content}"
        return message


class PlainTxtDailyMessage(IDailyMessage):

    CACHE_Daily: dict[str, str] = filebase_database.Database(
        f'{bot_path.common_data_full}daily-txt',
    ).value

    async def _get_daily_message(self):
        path_cache_daily = PlainTxtDailyMessage.CACHE_Daily.get(self.key)
        if not path_cache_daily:
            # 注意销毁今天以前的缓存
            content = await daily_txt(self.server, self.group_id, self.offset)  # 向后预测1天的
            txt = content.text if isinstance(content, DailyResponse) else content[0]
            PlainTxtDailyMessage.CACHE_Daily[self.key] = txt

        data_daily = PlainTxtDailyMessage.CACHE_Daily[self.key]
        prefix = self.cron.notify_content
        message = f"{data_daily}\n{'-'*10}{prefix}\n{await saohua()}"
        return message


async def CallbackDaily(group_id: str, sub: SubscribeSubject, cron: SubjectCron):
    now = DateTime()
    offset_hour = 3  # 向后3小时，保证9点以后推的是明日日常
    offset = 1 if now.hour >= (24-offset_hour) else 0  # 每晚24-x点后响应次日的
    now += offset_hour * 3600e3
    message = PlainTxtDailyMessage(now.tostring(DateTime.Format.YMD), group_id, cron, offset=offset)
    return await message.get_message()

CallbackDailyToday = CallbackDaily
CallbackDailyTomorow = CallbackDaily


def run(__subjects: list):
    v = SubscribeSubject(
        name="日常",
        description="每天早上和晚上推送日常任务",
        children_subjects=["今日日常", "明日日常"]
    )
    __subjects.append(v)
    v = SubscribeSubject(
        name="今日日常",
        description="每天一大早推送今天的日常任务",
        cron=[
            SubjectCron("20 7 * * *", "早~今天的日常来啦")
        ],
        callback=CallbackDailyToday
    )
    __subjects.append(v)
    v = SubscribeSubject(
        name="明日日常",
        description="每天晚上10点推送次日的日常任务",
        cron=[
            SubjectCron("55 21 * * *", "这是明天的日常哦~晚安！")
        ],
        callback=CallbackDailyTomorow
    )
    __subjects.append(v)
