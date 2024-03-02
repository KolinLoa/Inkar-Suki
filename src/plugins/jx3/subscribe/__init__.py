from src.tools.basic import *

subscribe_options = json.loads(read(PLUGINS + "/jx3/subscribe/options.json"))

subscribe_enable = on_command("jx3_subscribe", aliases={"订阅", "开启"}, priority=5)

@subscribe_enable.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    arg = args.extract_plain_text().split(" ")
    if len(arg) == 0:
        await subscribe_enable.finish("唔……开启失败，您似乎没有告诉我您要订阅的内容？")
    else:
        if not set(arg).issubset(set(list(subscribe_options))):
            await subscribe_enable.finish("唔……开启失败，虽然音卡可以一次开启多个订阅，但是好像您这里包含了不应该存在的订阅内容，请检查后重试！")
        currentData = getGroupData(str(event.group_id), "subscribe")
        for i in arg:
            if i in currentData:
                continue
            currentData.append(i)
        setGroupData(str(event.group_id), "subscribe", currentData)
        await subscribe_enable.finish("订阅成功！\n可使用“关于”查看本群详细信息！")

subscribe_disable = on_command("jx3_unsubscribe", aliases={"退订", "关闭"}, priority=5)

@subscribe_disable.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    arg = args.extract_plain_text().split(" ")
    if len(arg) == 0:
        await subscribe_disable.finish("唔……关闭失败，您似乎没有告诉我您要退订的内容？")
    else:
        if not set(arg).issubset(set(list(subscribe_options))):
            await subscribe_enable.finish("唔……关闭失败，虽然音卡可以一次关闭多个订阅，但是好像您这里包含了不应该存在的退订内容，请检查后重试！")
        currentData = getGroupData(str(event.group_id), "subscribe")
        for i in arg:
            if i not in currentData:
                continue
            currentData.remove(i)
        setGroupData(str(event.group_id), "subscribe", currentData)
        await subscribe_disable.finish("退订成功！\n可使用“关于”查看本群详细信息！")