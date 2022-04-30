import os
import sys
from pathlib import Path

from nonebot import on_command
from nonebot.adapters import Message
from nonebot.adapters.onebot.v11 import Event, Bot
from nonebot.params import CommandArg

from .example import status

import nonebot
TOOLS = nonebot.get_driver().config.tools_path
sys.path.append(str(TOOLS))
from permission import checker, error
from file import read, write
from config import Config

status

helpimg = on_command("helpimg", aliases={"hi"}, priority=5)


@helpimg.handle()
async def _(bot: Bot, event: Event, args: Message = CommandArg()):
    if checker(str(event.user_id), 9) == False:
        await helpimg.finish(error(10))
    size = args.extract_plain_text()
    if size:
        if size.find("x"):
            write(Config.size_path,size)
            await helpimg.finish("好的~图片尺寸已修改为"+size+"。")
        else:
            await helpimg.finish("唔，这尺寸不对哦~")
    else:
        await helpimg.finish("唔，你忘记输入尺寸了啦！")
    
imgsize = on_command("imgsize",aliases={"is"},priority=5)

@imgsize.handle()
async def __(bot: Bot, event: Event, args: Message = CommandArg()):
    if checker(str(event.user_id),9) == False:
        await bot.finish(error(9))
    size = read(Config.size_path)
    await imgsize.finish("查到啦！当前图片尺寸为"+size+"。")
purge = on_command("purge",priority=5)

@purge.handle()
async def ___(bot: Bot, event: Event, args: Message = CommandArg()):
    if checker(str(event.user_id),1) == False:
        await purge.finish(error(1))
    if Config.platform == True:
        os.system(f"rm -rf {Config.help_image_save_to}")
        os.system(f"rm -rf {Config.html_path}")
    else:
        os.system(f"rd /s /q {Config.help_image_save_to}")
        os.system(f"rd /s /q {Config.html_path}")
    await purge.finish("好的，已帮你清除图片缓存~")

shutdown = on_command("shutdown",aliases={"poweroff"},priority=5)

@shutdown.handle()
async def ____(bot: Bot, event: Event, args: Message = CommandArg()):
    if checker(str(event.user_id),10) == False:
        await shutdown.error(10)
    if Config.platform == False:
        await shutdown.finish("唔，主人用了Windows，我没办法关闭哦~")
    await shutdown.send("请稍候，正在关闭中……")
    await shutdown.send("关闭成功！请联系Owner到后台手动开启哦~")
    os.system("killall nb")

restart = on_command("restart",priority=5)
@restart.handle()
async def _(bot: Bot, event: Event, args: Message = CommandArg()):
    with open("./example.py",mode="w") as cache:
        if checker(str(event.user_id),5) == False:
            await restart.finish(error(5))
        await  restart.send("好啦，开始重启，整个过程需要些许时间，还请等我一下哦~")
        cache.write("status=\"OK\"")
