from nonebot import get_driver
from nonebot.log import logger

from src.tools.config import Config
from src.tools.utils.path import ASSETS
from src.tools.generate import generate

from .jx3 import *

from .parse import get_registered_actions, parse_data, JX3APIOutputMsg
from .weibo import poll_weibo_api

import re
import shutil
import asyncio
import websockets
import json

driver = get_driver()

async def websocket_client(ws_url: str, headers: dict):
    while True:
        try:
            async with websockets.connect(ws_url, extra_headers=headers) as websocket:
                logger.info("WebSocket connection established")
                while True:
                    response = await websocket.recv()
                    raw_response = response
                    response = json.loads(response)
                    if response["action"] not in get_registered_actions():
                        logger.warning("未知JX3API 消息: " + str(raw_response))
                        continue
                    logger.info("JX3API 解析成功: " + str(raw_response))
                    parsed = parse_data(response)
                    msg: JX3APIOutputMsg = parsed.msg()
                    name = msg.name
                    if name == "公告":
                        url, title = parsed.provide_data()
                        if re.match(r'(\d+)月(\d+)日(.*?)版本更新公告', title):
                            try:    
                                shutil.rmtree(ASSETS + "/jx3/update.png")
                            except FileNotFoundError:
                                pass
                            await generate(
                                url, 
                                True, 
                                ".allnews_list_container", 
                                viewport={"height": 3840, "width": 2000}, 
                                hide_classes=["detail_bot", "bdshare-slide-button"], 
                                device_scale_factor=2.0,
                                output=ASSETS + "/jx3/update.png"
                            )
                    await send_subscribe(name, msg.msg, msg.server)
                    logger.info(msg.msg)
        except websockets.exceptions.ConnectionClosed:
            logger.warning("WebSocket connection closed, retrying...")
        except Exception as e:
            logger.error(f"WebSocket connection error: {e}")
        await asyncio.sleep(3)

@driver.on_startup
async def on_startup():
    ws_url = Config.jx3.ws.url
    headers = {
        "token": Config.jx3.ws.token
    }
    asyncio.create_task(websocket_client(ws_url, headers))
    asyncio.create_task(poll_weibo_api("2046281757", interval=600))