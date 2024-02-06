from src.tools.dep import *
from src.tools.file import read, write
import random
import json
import os
import datetime

from nonebot.adapters.onebot.v11 import MessageSegment as ms


class SignInRecord:
    def init_lucky(self, luck: int = None):
        if not luck:
            luck = random.randint(0, 10000)
        if luck < 1000:
            return 0
        elif luck < 7500:
            return 1
        elif luck < 9000:
            return 2
        return 3

    def __init__(self) -> None:
        self.user_id: str = None
        self.continuous: int = 0
        self.coin: int = 0
        self.luck: int = self.init_lucky()
        self.msg: str = None


class Sign:

    def generate_everyday_reward(qq: str):
        signed_list = json.loads(read(bot_path.CLOCK + "/signed.json")) or []
        rank = len(signed_list)
        s = SignInRecord()
        continious = Sign.get_continuity(qq)
        s.coin = random.randint(1, 100) * (s.luck + 1)
        lottery = random.randint(0, 100)
        wlottery = False
        if lottery % 10 == 0:
            s.coin += 100
            wlottery = True
            s.wlottery = 1
        luck_desc = ["末吉签", "中吉签", "上吉签", "上上签"][s.luck]
        luck_desc = f"{luck_desc}(x{s.luck+1})"
        msg = f"\n签到成功！\n金币：+{s.coin}\n今日运势：{luck_desc}"
        if wlottery:
            msg = f"{msg}\n触发额外奖励！已帮你额外添加了100枚金币！"
        msg = f"{msg}\n已连续签到{continious + 1}天！"
        msg = f"{msg}\n您是第{rank + 1}位签到的哦~"
        s.msg = ms.at(qq) + msg
        return s

    def wsigned(qq: int):
        signed = json.loads(read(bot_path.CLOCK + "/signed.json")) or []
        if str(qq) in signed:
            return True
        return False

    def save_data(data: SignInRecord, qq):
        qq = str(qq)
        signed_list = json.loads(read(bot_path.CLOCK + "/signed.json")) or []
        signed_list.append(qq)
        write(bot_path.CLOCK + "/signed.json", json.dumps(signed_list, ensure_ascii=False))
        user = Sign.get_user_record(qq)

        user["coin"] = user.get("coin") + data.coin
        last = user.get("last")
        now = datetime.datetime.now()
        dateformat = "%Y-%m-%d %H:%M:%S"
        is_continued = not last  # 如无记录，则延续用户数据
        if not is_continued:
            last_date = datetime.datetime.strptime(last, dateformat).date()
            judge_date = last_date + datetime.timedelta(days=1)
            is_continued = judge_date == now.date()
        if is_continued:
            user["continuity"] += 1
        user["coin"] += data.coin
        user["last"] = datetime.datetime.strftime(now, dateformat)
        Sign._flush_accounts()
        return

    def get_user_record(qq: str) -> dict:
        """
        获取用户签到信息
        """
        qq = str(qq)
        accounts = json.loads(read(f"{bot_path.CLOCK}{os.sep}account.json")) or {}
        need_convert = isinstance(accounts, list)
        if need_convert:
            accounts = dict([[x["id"], x] for x in accounts])
            for x in accounts:
                del accounts[x]["id"]

        user = accounts.get(qq)
        if not user:
            user = {"coin": 0, "continuity": 0, "last": None}
            accounts[qq] = user

        Sign.accounts = accounts
        if need_convert:
            Sign._flush_accounts()
        return user

    def _flush_accounts():
        x = getattr(Sign, "accounts")
        if x is None:
            return
        path = f"{bot_path.CLOCK}{os.sep}account.json"
        write(path, json.dumps(Sign.accounts, ensure_ascii=False))

    def get_continuity(qq):
        """
        获取用户连续登录天数
        """
        return Sign.get_user_record(qq).get("continuity") or 0

    def get_coin(qq):
        """
        获取用户当前金币数
        """
        return Sign.get_user_record(qq).get("coin") or 0
    
    def reduce(qq, value):
        current = int(Sign.get_coin(qq))
        if current < value:
            return False
        final_value = current - value
        now = json.loads(read(bot_path.CLOCK + "/account.json"))
        now[qq]["coin"] = final_value
        write(bot_path.CLOCK + "/account.json", json.dumps(now))
    
    def add(qq, value):
        now = json.loads(read(bot_path.CLOCK + "/account.json"))
        if qq not in list(now):
            now[qq] = {"coin": int(value)}
        else:
            now[qq]["coin"] = int(Sign.get_coin(qq)) + value
        write(bot_path.CLOCK + "/account.json", json.dumps(now))