import asyncio

from botpy import BotAPI
from botpy.ext.command_util import Commands
from botpy.message import GroupMessage

import maimai.Api
from Utils.Database import Database
from Utils.ScoreProcess import diving_fish_uploading, lxns_uploading


@Commands("bind", "绑定", "绑")
async def bind(api: BotAPI, message: GroupMessage, params=None):
    if params is None:
        await message.reply(
            content="请在命令后附带有效登入二维码内容\r\n例：/bind SGWCMAID000..."
        )
        return True

    try:
        result = await maimai.Api.A(params)
    except:
        await message.reply(content="远端访问异常")
        raise

    if result["errorID"] != 0 or result["userID"] == -1:
        await message.reply(content="API异常")
        return True

    with Database("uid") as db:
        db.set(message.author.member_openid, result["userID"])
    await message.reply(content="舞萌中二账号绑定成功")
    return True


@Commands("binddf", "绑定水鱼", "绑水鱼")
async def binddf(api: BotAPI, message: GroupMessage, params=None):
    if params is None:
        await message.reply(content="请在命令后附带水鱼上传Token\r\n例：/binddf 000...")
        return True

    with Database("dfid") as db:
        db.set(message.author.member_openid, params)
    await message.reply(content="水鱼上传Token绑定成功")
    return True


@Commands("bindlx", "绑定落雪", "绑落雪")
async def bindlx(api: BotAPI, message: GroupMessage, params=None):
    if params is None:
        await message.reply(content="请在命令后附带好友码\r\n例：/bindlx 000...")
        return True

    with Database("lxid") as db:
        db.set(message.author.member_openid, params)
    await message.reply(content="好友码绑定成功")
    return True


@Commands("pull", "爬取", "拉取", "推送", "推")
async def pull(api: BotAPI, message: GroupMessage, params=None):
    with Database("uid") as db:
        uid = db.get(message.author.member_openid)
    if not uid:
        await message.reply(content="尚未绑定舞萌中二账号")
        return True

    with Database("dfid") as db:
        dfid = db.get(message.author.member_openid)
    with Database("lxid") as db:
        lxid = db.get(message.author.member_openid)
    if not dfid and not lxid:
        await message.reply(content="尚未绑定任一查分器")
        return True

    try:
        result = await maimai.Api.B(uid)
    except:
        await message.reply(content="远端访问异常")
        raise

    tasks = []
    if dfid:
        tasks.append(diving_fish_uploading(dfid, result))

    if lxid:
        tasks.append(lxns_uploading(lxid, result))

    results = await asyncio.gather(*tasks)
    msgs = []
    for _, result in enumerate(results):
        if result[0]:
            await message.reply(content="成绩推送完成")
            return True
        if result[1] is not None:
            msgs.append(result[1])

    await message.reply(content=f"成绩推送失败：\r\n{"\r\n".join(msgs)}")
    return True
