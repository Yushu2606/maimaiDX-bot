from fractions import Fraction

import aiohttp
import tomlkit


def get_fc_or_fs(fc: int = 0, fs: int = 0, default_value=None):
    fc_enums = {0: default_value, 1: "fc", 2: "fcp", 3: "ap", 4: "app"}

    fs_enums = {0: default_value, 1: "fs", 2: "fsp", 3: "fsd", 4: "fsdp", 5: "sync"}
    return fc_enums.get(fc, default_value), fs_enums.get(fs, default_value)


async def generate_df_update_records(music_data: dict):
    async with aiohttp.ClientSession() as session:
        async with session.get(
            "https://www.diving-fish.com/api/maimaidxprober/music_data"
        ) as resp:
            resp.raise_for_status()
            total_list = await resp.json()

    update_music_data_list = []

    for sig_music_list in music_data["userMusicList"]:
        music_detial = None
        for music in total_list:
            if music["id"] == str(sig_music_list["userMusicDetailList"][0]["musicId"]):
                music_detial = music
                break

        if music_detial is None:
            continue

        for music_score in sig_music_list["userMusicDetailList"]:
            level_index = music_score["level"]
            if len(music_detial["cids"]) <= level_index:
                continue

            fc, fs = get_fc_or_fs(
                music_score["comboStatus"], music_score["syncStatus"], ""
            )
            achievements = Fraction(music_score["achievement"]) / Fraction(10000)
            dx_score = music_score["deluxscoreMax"]
            title = music_detial["title"]
            music_type = music_detial["type"]
            music_data = {
                "achievements": achievements.numerator / achievements.denominator,
                "dxScore": dx_score,
                "fc": fc,
                "fs": fs,
                "level_index": level_index,
                "title": title,
                "type": music_type,
            }
            update_music_data_list.append(music_data)

    return update_music_data_list


async def generate_lx_update_records(music_data: dict):
    async with aiohttp.ClientSession() as session:
        async with session.get(
            "https://maimai.lxns.net/api/v0/maimai/song/list"
        ) as resp:
            resp.raise_for_status()
            total_list = await resp.json()

    update_music_data_list = []

    for sig_music_list in music_data["userMusicList"]:
        for music_score in sig_music_list["userMusicDetailList"]:
            music_id = music_score["musicId"] % 10000
            music_type = "dx" if music_score["musicId"] >= 10000 else "standard"
            level_index = music_score["level"]
            if not [
                None
                for song in total_list["songs"]
                if song["id"] == music_id and len(song[music_type]) > level_index
            ]:
                continue

            fc, fs = get_fc_or_fs(music_score["comboStatus"], music_score["syncStatus"])
            achievements = Fraction(music_score["achievement"]) / Fraction(10000)
            dx_score = music_score["deluxscoreMax"]
            music_data = {
                "id": music_id,
                "type": music_type,
                "level_index": level_index,
                "achievements": achievements.numerator / achievements.denominator,
                "fc": fc,
                "fs": fs,
                "dx_score": dx_score,
            }
            update_music_data_list.append(music_data)

    return update_music_data_list


async def diving_fish_uploading(dfid: str, records: dict):
    try:
        update_music_data_list = await generate_df_update_records(records)
        async with aiohttp.ClientSession() as session:
            headers = {"Import-Token": dfid}
            async with session.post(
                "https://www.diving-fish.com/api/maimaidxprober/player/update_records",
                json=update_music_data_list,
                headers=headers,
            ) as resp:
                resp.raise_for_status()
                resp_obj = await resp.json()
    except:
        return False, "水鱼：API异常"

    if "status" in resp_obj and resp_obj["status"] != "error":
        return False, f"水鱼：{resp_obj["message"]}"

    return True, None


async def lxns_uploading(lxid: str, records: dict):
    try:
        update_music_data_list = await generate_lx_update_records(records)
        async with aiohttp.ClientSession() as session:
            with open("config.toml", "r", encoding="utf-8") as f:
                config = tomlkit.load(f)

            headers = {"Authorization": config["lx_dev_token"]}
            async with session.post(
                f"https://maimai.lxns.net/api/v0/maimai/player/{lxid}/scores",
                json={"scores": update_music_data_list},
                headers=headers,
            ) as resp:
                resp_obj = await resp.json()
    except:
        return False, "落雪：API异常"

    if not resp_obj["success"]:
        return False, f"落雪：{resp_obj["message"]}"

    return True, None
