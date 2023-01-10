import io
import sys
import traceback

from bot import bot, filters
from . import SUDOS

MAX_MESSAGE_LENGTH = 4096

@bot.on_message(filters=filters.command("eval") & filters.user(SUDOS), group=1)
async def _(client, message):
    status_message = await message.reply_text("Processing ...")
    try:
        cmd = message.text.split(" ", maxsplit=1)[1]
    except:
        return await status_message.edit_text("Give code to evaluate...")

    reply_to_ = message
    if message.reply_to_message:
        reply_to_ = message.reply_to_message

    old_stderr = sys.stderr
    old_stdout = sys.stdout
    redirected_output = sys.stdout = io.StringIO()
    redirected_error = sys.stderr = io.StringIO()
    stdout, stderr, exc = None, None, None

    try:
        await aexec(cmd, client, message)
    except Exception:
        exc = traceback.format_exc()

    stdout = redirected_output.getvalue()
    stderr = redirected_error.getvalue()
    sys.stdout = old_stdout
    sys.stderr = old_stderr

    evaluation = ""
    if exc:
        evaluation = exc
    elif stderr:
        evaluation = stderr
    elif stdout:
        evaluation = stdout
    else:
        evaluation = "Success"

    final_output = "**EVAL**: "
    final_output += f"`{cmd}`\n\n"
    final_output += "**OUTPUT***:\n"
    final_output += f"`{evaluation.strip()}`\n"

    if len(final_output) > MAX_MESSAGE_LENGTH:
        with io.BytesIO(str.encode(final_output)) as out_file:
            out_file.name = "eval.text"
            await reply_to_.reply_document(
                document=out_file,
                caption=f"`{cmd[: MAX_MESSAGE_LENGTH // 4 - 1]}`",
                disable_notification=True,
                parse_mode="markdown",
                quote=True,
            )
    else:
        await reply_to_.reply_text(final_output, parse_mode="markdown", quote=True)
    await status_message.delete()


async def aexec(code, client, message):
    exec(
        "async def __aexec(client, message): "
        + "\n m = message"
        + "\n chat = m.chat.id"
        + "\n reply = m.reply_to_message"
        + "".join(f"\n {l_}" for l_ in code.split("\n"))
    )
    return await locals()["__aexec"](client, message)
