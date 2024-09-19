import asyncio
import json
import re
from datetime import datetime, timedelta

from botpy import BotAPI
from botpy.ext.command_util import Commands
from botpy.message import GroupMessage

import maimai.Api
from Utils.Database import Database
from Utils.ScoreProcess import diving_fish_uploading, lxns_uploading
from httpcore import ConnectTimeout

@Commands("bind", "绑定", "绑")
async def bind(api: BotAPI, message: GroupMessage, params: list[str] | None = None):
    if params is None:
        await message.reply(
            content="请在命令后附带有效登入二维码内容\r\n例：/bind SGWCMAID000..."
        )
        return True

    if len(params) != 1 or len(params[0]) != 84 or not params[0].startswith("SGWCMAID") or re.match(
            "^[0-9A-F]+$",
            params[0][
            20:]) is None:
        await message.reply(content="无效的登入二维码")
        return True

    try:
        if datetime.now() - datetime.strptime(params[0][8:20], "%y%m%d%H%M%S") > timedelta(
                minutes=10):
            await message.reply(content="过期的登入二维码")
            return True
    except ValueError:
        await message.reply(content="无效的登入二维码")
        return True

    try:
        result = await maimai.Api.A(params[0])
    except ConnectTimeout:
        await message.reply(content="远端访问异常")
        return True

    if result["errorID"] != 0 or result["userID"] == -1:
        await message.reply(content="API异常")
        return True

    with Database("uid") as db:
        db.set(message.author.member_openid, result["userID"])
    await message.reply(content="舞萌中二账号绑定成功")
    return True


@Commands("binddf", "绑定水鱼", "绑水鱼")
async def binddf(api: BotAPI, message: GroupMessage, params: list[str] | None = None):
    if params is None:
        await message.reply(content="请在命令后附带水鱼上传Token\r\n例：/binddf 000...")
        return True

    if len(params) != 1 or len(params[0]) != 128 or re.match("^[0-9A-Za-z]+$", params[0]) is None:
        await message.reply(content="无效的水鱼上传Token")
        return True

    with Database("dfid") as db:
        db.set(message.author.member_openid, params[0])
    await message.reply(content="水鱼上传Token绑定成功")
    return True


@Commands("bindlx", "绑定落雪", "绑落雪")
async def bindlx(api: BotAPI, message: GroupMessage, params: list[str] | None = None):
    if params is None:
        await message.reply(content="请在命令后附带好友码\r\n例：/bindlx 000...")
        return True

    if len(params) != 1 or len(params[0]) != 15 or not params[0].isdigit():
        await message.reply(content="无效的好友码")
        return True

    with Database("lxid") as db:
        db.set(message.author.member_openid, params[0])
    await message.reply(content="好友码绑定成功")
    return True


@Commands("pull", "爬取", "拉取", "推送", "推")
async def pull(api: BotAPI, message: GroupMessage, params: None = None):
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
    except ConnectTimeout:
        await message.reply(content="远端访问异常")
        return True

    tasks = []
    if dfid:
        tasks.append(diving_fish_uploading(dfid, result))

    if lxid:
        tasks.append(lxns_uploading(lxid, result))

    results = await asyncio.gather(*tasks)
    msgs = []
    for _, result in enumerate(results):
        if result[0] or result[1] is None:
            continue

        msgs.append(result[1])

    if len(msgs) <= 0:
        await message.reply(content="成绩推送成功")
        return True

    await message.reply(content=f"成绩推送失败：\r\n{"\r\n".join(msgs)}")
    return True


@Commands("埋", "下埋")
async def mai(api: BotAPI, message: GroupMessage, params: list[str] | None = None):
    with Database("uid") as db:
        uid = db.get(message.author.member_openid)
    if not uid:
        await message.reply(content="尚未绑定舞萌中二账号")
        return True

    if params is None:
        await message.reply(content="请在命令后附带需要下埋的牌子\r\n例：/埋 真极")
        return True

    if len(params) != 1 or len(params[0]) > 3 or len(params[0]) < 2:
        await message.reply(content="无效的牌子")
        return True

    with open("./data/map/mai_ver.json", "r", encoding="utf-8") as f:
        mai_ver: dict[str, list[str]] = json.load(f)

    ver_name = params[0][0]
    act_type = params[0][1:]
    if params[0] == "霸者":
        ver_name = "舞"
        act_type = "清"
    elif ver_name not in mai_ver or act_type not in ["极", "将", "神", "舞舞"] or params[0] == "真将":
        await message.reply(content="无效的牌子")
        return True

    try:
        succeed, msg = await maimai.Api.C(uid, mai_ver[ver_name], act_type)
    except ConnectTimeout:
        await message.reply(content="远端访问异常")
        return True

    if not succeed:
        await message.reply(content=f"下埋失败：{msg}")
        return True

    if msg <= 0:
        await message.reply(content="不需要下埋")
        return True

    await message.reply(content=f"下埋完成，已埋{msg}个谱面")
    return True
