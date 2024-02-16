from .api import *

item_price = on_command("jx3_price", aliases={"物价"}, priority=5)


@item_price.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    """
    获取外观物价：

    Example：-物价 山神盒子
    Example：-物价 大橙武券
    """
    arg = args.extract_plain_text()
    if arg == "":
        return await item_price.finish("缺少物品名称，没办法找哦~")
    data = await item_(arg)
    if isinstance(data, list):
        async with httpx.AsyncClient() as client:
            r: httpx.Response = await client.get(data[0])
            final_image = r.content
            await item_price.finish(ms.image(final_image))
    await item_price.finish(ms.image(data))

