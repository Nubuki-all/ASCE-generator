from . import *
from .anilist import anime_arch, get_info

LOGS.info("starting…")


@bot.on_message(filters.incoming & filters.command(["start", "help"]))
async def _(bot, message):
    await hello(message)


@bot.on_message(filters.incoming & filters.command(["set_psd"]))
async def _(bot, message):
    await passwd(message)


@bot.on_message(filters.incoming & filters.command(["logs"]))
async def _(bot, message):
    await send_logs(message)


@bot.on_message(filters.incoming & filters.command(["anime"]))
async def _(bot, message):
    if message.from_user:
        if str(message.from_user.id) not in SUDO:
            return await message.delete()
    else:
        if str(message.chat.id) not in ALLOWED_CHANNELS:
            return await message.delete()
    await anime_arch(message)


@bot.on_message(filters.incoming & filters.command(["gen", "create_sub"]))
async def _(bot, message):
    await generate(message)


async def rep_msg_tmp(message, msg):
    rep = await message.reply(msg)
    await message.delete()
    await asyncio.sleep(15)
    await rep.delete()


async def hello(message):
    if not str(message.from_user.id) in SUDO:
        return await message.delete()
    currenttime = get_readable_time(time.time() - uptime)
    reply = f"Hello there I've been up for {currenttime}!"
    reply += "\n\n**Available commands:**"
    reply += "\n /gen - `generate subchannel entries.` Arguments: -p (password) -n (name of anime) , -l (invite link)(optional) , -q (quality)(optional)"
    reply += "\n /set_psd - `change/disable password for bot.`"
    reply += "\n /logs - `Get logs.`"
    reply += "\n /start - `see this message again.`"
    try:
        await message.reply(reply)
    except Exception:
        LOGS.info(traceback.format_exc())


async def passwd(message):
    if not str(message.from_user.id) in SUDO:
        return
    args = message.command[1]
    if str(args) == "0":
        if PASSWD[0] == "0":
            await message.reply("`Password already disabled.`")
        await message.reply("`Password disabled.`")
    elif PASSWD[0] == args:
        return await message.reply("`Kindly enter a 'new' password.`")
    PASSWD.clear()
    PASSWD.append(str(args))
    return await message.reply(f"**Password changed to** `{args}`")


async def generate(message):
    if message.from_user:
        return await message.reply("Coming soon.")
    if ALLOWED_CHANNELS == "0":
        pass
    elif not str(message.chat.id) in ALLOWED_CHANNELS:
        return
    chat = message.chat.id
    arg = (message.text.split(maxsplit=1))[1]
    parser = argparse.ArgumentParser(description="Wip")
    parser.add_argument("-p", type=str, required=False)
    parser.add_argument("-n", type=str, required=False)
    parser.add_argument("-l", type=str, required=False)
    parser.add_argument("-q", type=str, required=False)

    try:
        args, unknown = parser.parse_known_args(shlex.split(arg))
    except SystemExit:
        er = "A drastic error occurred while trying to parse argument."
        LOGS.info(er)
        return await message.reply(er)
    if unknown:
        value = ""
        for v in unknown:
            value += v + ", "
        await rep_msg_tmp(
            message,
            f'**Warning:** The following were not parsed "`{value.strip(", ")}`"\nTo avoid use quotes while passing arguments.',
        )

    # Password check:
    if PASSWD[0] == "0":
        pass
    elif not args.p:
        return await rep_msg_tmp(message, "`Please provide a password.`")
    elif args.p != PASSWD[0]:
        return await rep_msg_tmp(message, "`Incorrect password.`")

    # Anime name check:
    if not args.n:
        return await rep_msg_tmp(message, "`Please provide a name.`")
    if is_url(args.l):
        re_link = reformat_spaces(args.l)
        link = InlineKeyboardButton(text=f"◉  Link", url=re_link)
        link = InlineKeyboardMarkup([[link]])
    else:
        link = None
    try:
        caption, pic_url = await get_info(args.n, args.q)
        await message.delete()
        await bot.send_photo(
            photo=pic_url, caption=caption, chat_id=chat, reply_markup=link
        )
    except Exception:
        LOGS.info(traceback.format_exc())
        return await rep_msg_tmp(message, "`An error occurred.`")
    return


async def send_logs(message):
    if not message.from_user:
        return
    if str(message.from_user.id) not in SUDO:
        return
    try:
        await message.reply_document(
            document="logs.txt",
            quote=True,
            caption=get_readable_time(time.time() - uptime),
        )
        return
    except Exception:
        LOGS.info(traceback.format_exc())
        await message.reply("`An error occurred.`")


########### Start ############

try:
    with bot:
        bot.loop.run_until_complete(startup())
        bot.loop.run_forever()
except Exception:
    LOGS.critical(traceback.format_exc())
    LOGS.critical("Cannot recover from error, exiting…")
    exit()
