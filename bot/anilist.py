from datetime import datetime

import flag
import humanize
import requests
from aiohttp import ClientSession
from html_telegraph_poster import TelegraphPoster

from . import *

url = "https://graphql.anilist.co"
anime_query = """
query ($id: Int, $idMal:Int, $search: String, $type: MediaType, $asHtml: Boolean) {
  Media (id: $id, idMal: $idMal, search: $search, type: $type) {
    id
    idMal
    title {
      romaji
      english
      native
    }
    format
    status
    description (asHtml: $asHtml)
    startDate {
      year
      month
      day
    }
   endDate {
      year
      month
      day
    }
    season
    episodes
    duration
    countryOfOrigin
    source (version: 2)
    trailer {
      id
      site
      thumbnail
    }
    coverImage {
      extraLarge
    }
    bannerImage
    genres
    averageScore
    nextAiringEpisode {
      airingAt
      timeUntilAiring
      episode
    }
    isAdult
    characters (role: MAIN, page: 1, perPage: 10) {
      nodes {
        id
        name {
          full
          native
        }
        image {
          large
        }
        description (asHtml: $asHtml)
        siteUrl
      }
    }
    studios (isMain: true) {
      nodes {
        name
        siteUrl
      }
    }
    siteUrl
  }
}
"""


async def get_info(name, quality, invite_link, tags):
    try:
        variables = {"search": name, "type": "ANIME"}
        json = (
            requests.post(url, json={"query": anime_query, "variables": variables})
            .json()["data"]
            .get("Media")
        )
        # pylint: disable=possibly-unused-variable
        eng_title = json["title"]["english"]
        eng_title = json["title"]["romaji"] if eng_title is None else eng_title
        jp_title = json["title"]["romaji"]
        id_ = json["id"]
        pic_url = f"https://img.anili.st/media/{id_}"
        con = f"{json['countryOfOrigin']}"
        cflag = flag.flag(con)
        try:
            gen = json["genres"]
        except Exception:
            gen = None
        trailer_link = "N/A"
        episode = json.get("episodes")
        duration = json.get("duration")
        status = json.get("status")
        json["averageScore"]
        startDate = "N/A"
        endDate = None
        if json["startDate"]["year"]:
            startDate = f"{json['startDate']['year']}-{json['startDate']['month']}-{json['startDate']['day']}"
        if json["endDate"]["year"]:
            endDate = f"{json['endDate']['year']}-{json['endDate']['month']}-{json['endDate']['day']}"
        if json["trailer"] and json["trailer"]["site"] == "youtube":
            trailer_link = (
                f"<a href='https://youtu.be/{json['trailer']['id']}'>Trailer</a>"
            )
        json.get("format")
    except Exception:
        eng_title = None
        LOGS.info(traceback.format_exc())
    try:
        if eng_title is None:
            raise Exception("Getting info failed")
        if gen:
            genre = ""
            for x in gen:
                genre += "#" + (x.replace(" ", "_")).replace("-", "_") + " "
        if eng_title == jp_title:
            msg = f"`{jp_title}`"
        else:
            msg = f"**{eng_title}**\n`{jp_title}`"
        msg += f"({cflag})"
        msg += "\n\n"
        if gen and genre:
            msg += f"**‣ Genre** : {genre}\n"
        msg += "\n\n"
        msg += f"**‣ Status : {status}**\n"
        msg += f"**‣ First aired : {startDate}**\n"
        if endDate:
            msg += f"**‣ Last aired : {endDate}**\n"
        if duration:
            msg += f"**‣ Runtime : {duration} minutes**\n"
        if episode:
            msg += f"**‣ No of episodes : {episode}**\n"
        if quality or is_url(invite_link) or tags:
            msg += "\n\n"
        if quality:
            msg += f"**‣ Quality Available :** `{quality}`\n"
        if is_url(invite_link):
            link = reformat_spaces(invite_link)
            msg += f"**‣ Invite link :** **[XXXX XXXX XXXX]({link})**\n"
        if tags:
            if quality or is_url(invite_link):
                msg += "\n"
            msg += f"{tags}"
    except Exception:
        LOGS.info(traceback.format_exc())
        msg, pic_url = None, None

    return msg, pic_url


# Default templates for Query Formatting
# https://github.com/UsergeTeam/Userge-Plugins/blob/dev/plugins/utils/anilist/__main__.py
ANIME_TEMPLATE = """[{c_flag}]**{romaji}**

**ID | MAL ID:** `{idm}` | `{idmal}`
➤ **SOURCE:** `{source}`
➤ **TYPE:** `{formats}`
➤ **GENRES:** `{genre}`
➤ **SEASON:** `{season}`
➤ **EPISODES:** `{episodes}`
➤ **STATUS:** `{status}`
➤ **NEXT AIRING:** `{air_on}`
➤ **SCORE:** `{score}%` 🌟
➤ **ADULT RATED:** `{adult}`
🎬 {trailer_link}
📖 [Synopsis & More]({synopsis_link})"""


async def return_json_senpai(query, vars_):
    """Makes a Post to https://graphql.anilist.co."""
    url_ = "https://graphql.anilist.co"
    async with ClientSession() as api_:
        post_con = await api_.post(url_, json={"query": query, "variables": vars_})
        json_data = await post_con.json()
        return json_data


def post_to_tp(a_title, content):
    """Create a Telegram Post using HTML Content"""
    post_client = TelegraphPoster(use_api=True)
    auth_name = "@Ani_mirror"
    post_client.create_api_token(auth_name)
    post_page = post_client.post(
        title=a_title,
        author=auth_name,
        author_url="https://t.me/Ani_mirror",
        text=content,
    )
    return post_page["url"]


def make_it_rw(time_stamp, as_countdown=False):
    """Converting Time Stamp to Readable Format"""
    if as_countdown:
        now = datetime.now()
        air_time = datetime.fromtimestamp(time_stamp)
        return str(humanize.naturaltime(now - air_time))
    return str(humanize.naturaldate(datetime.fromtimestamp(time_stamp)))


async def anime_arch(message):
    """Search Anime Info"""
    query = message.text.split(maxsplit=1)[1]
    if not query:
        await message.reply("NameError: 'query' not defined")
        return
    vars_ = {"search": query, "asHtml": True, "type": "ANIME"}
    if query.isdigit():
        vars_ = {"id": int(query), "asHtml": True, "type": "ANIME"}
    result = await return_json_senpai(anime_query, vars_)
    error = result.get("errors")
    if error:
        LOG.info(f"**ANILIST RETURNED FOLLOWING ERROR:**\n\n`{error}`")
        error_sts = error[0].get("message")
        await message.reply(f"[{error_sts}]")
        return

    data = result["data"]["Media"]
    # Data of all fields in returned json
    # pylint: disable=possibly-unused-variable
    idm = data.get("id")
    idmal = data.get("idMal")
    romaji = data["title"]["romaji"]
    english = data["title"]["english"]
    native = data["title"]["native"]
    formats = data.get("format")
    status = data.get("status")
    synopsis = data.get("description")
    season = data.get("season")
    episodes = data.get("episodes")
    duration = data.get("duration")
    country = data.get("countryOfOrigin")
    c_flag = flag.flag(country)
    source = data.get("source")
    coverImg = data.get("coverImage")["extraLarge"]
    bannerImg = data.get("bannerImage")
    genres = data.get("genres")
    genre = genres[0]
    if len(genres) != 1:
        genre = ", ".join(genres)
    score = data.get("averageScore")
    air_on = None
    if data["nextAiringEpisode"]:
        nextAir = data["nextAiringEpisode"]["airingAt"]
        air_on = make_it_rw(nextAir)
    s_date = data.get("startDate")
    adult = data.get("isAdult")
    trailer_link = "N/A"

    if data["trailer"] and data["trailer"]["site"] == "youtube":
        trailer_link = f"[Trailer](https://youtu.be/{data['trailer']['id']})"
    html_char = ""
    for character in data["characters"]["nodes"]:
        html_ = ""
        html_ += "<br>"
        html_ += f"""<a href="{character['siteUrl']}">"""
        html_ += f"""<img src="{character['image']['large']}"/></a>"""
        html_ += "<br>"
        html_ += f"<h3>{character['name']['full']}</h3>"
        html_ += f"<em>{c_flag} {character['name']['native']}</em><br>"
        html_ += f"<b>Character ID</b>: {character['id']}<br>"
        html_ += (
            f"<h4>About Character and Role:</h4>{character.get('description', 'N/A')}"
        )
        html_char += f"{html_}<br><br>"

    studios = ""
    for studio in data["studios"]["nodes"]:
        studios += "<a href='{}'>• {}</a> ".format(studio["siteUrl"], studio["name"])
    url = data.get("siteUrl")

    title_img = coverImg or bannerImg
    html_pc = ""
    html_pc += f"<img src='{title_img}' title={romaji}/>"
    html_pc += f"<h1>[{c_flag}] {native}</h1>"
    html_pc += "<h3>Synopsis:</h3>"
    html_pc += synopsis
    html_pc += "<br>"
    if html_char:
        html_pc += "<h2>Main Characters:</h2>"
        html_pc += html_char
        html_pc += "<br><br>"
    html_pc += "<h3>More Info:</h3>"
    html_pc += f"<b>Started On:</b> {s_date['day']}/{s_date['month']}/{s_date['year']}"
    html_pc += f"<br><b>Studios:</b> {studios}<br>"
    html_pc += f"<a href='https://myanimelist.net/anime/{idmal}'>View on MAL</a>"
    html_pc += f"<a href='{url}'> View on anilist.co</a>"
    html_pc += f"<img src='{bannerImg}'/>"

    title_h = english or romaji
    synopsis_link = post_to_tp(title_h, html_pc)
    try:
        finals_ = ANIME_TEMPLATE.format(**locals())
    except KeyError as kys:
        LOGS.info(traceback.format_exc())
        await message.reply(kys)
        return
    await message.reply_photo(title_img, caption=finals_)
    await message.delete()
    return
