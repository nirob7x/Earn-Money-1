import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes,
)

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN      = os.environ.get("BOT_TOKEN", "")
CHANNEL_ID     = os.environ.get("CHANNEL_ID", "")
BOT_USERNAME   = os.environ.get("BOT_USERNAME", "")
ADMIN_IDS      = [int(x) for x in os.environ.get("ADMIN_IDS", "").split(",") if x.strip()]
FSUB_IDS       = [x.strip() for x in os.environ.get("FSUB_IDS", "").split(",") if x.strip()]
AD_MESSAGE     = os.environ.get("AD_MESSAGE", "")
AD_BUTTON_TEXT = os.environ.get("AD_BUTTON_TEXT", "")
AD_BUTTON_URL  = os.environ.get("AD_BUTTON_URL", "")


def make_start_link(file_id: str) -> str:
    return f"https://t.me/{BOT_USERNAME}?start={file_id}"


async def check_subscription(bot, user_id: int) -> list:
    not_joined = []
    for ch_id in FSUB_IDS:
        try:
            member = await bot.get_chat_member(chat_id=ch_id, user_id=user_id)
            if member.status in ("left", "kicked", "banned"):
                not_joined.append(ch_id)
        except Exception as e:
            logger.warning(f"Subscription check failed for {ch_id}: {e}")
            not_joined.append(ch_id)
    return not_joined


async def build_fsub_keyboard(bot, not_joined: list) -> InlineKeyboardMarkup:
    buttons = []
    for ch_id in not_joined:
        try:
            chat = await bot.get_chat(ch_id)
            invite = chat.invite_link or await bot.export_chat_invite_link(ch_id)
            buttons.append([InlineKeyboardButton(f"✅ Join {chat.title}", url=invite)])
        except Exception:
            buttons.append([InlineKeyboardButton("✅ Join Channel", url="https://t.me/")])
    buttons.append([InlineKeyboardButton("🔄 Try Again", callback_data="check_sub")])
    return InlineKeyboardMarkup(buttons)


async def deliver_file(update: Update, context: ContextTypes.DEFAULT_TYPE, file_id: str):
    if AD_MESSAGE:
        ad_keyboard = None
        if AD_BUTTON_TEXT and AD_BUTTON_URL:
            ad_keyboard = InlineKeyboardMarkup([[InlineKeyboardButton(AD_BUTTON_TEXT, url=AD_BUTTON_URL)]])
        await update.message.reply_text(AD_MESSAGE, reply_markup=ad_keyboard, parse_mode="Markdown", disable_web_page_preview=False)

    try:
        await context.bot.forward_message(chat_id=update.effective_chat.id, from_chat_id=CHANNEL_ID, message_id=int(file_id))
        if AD_BUTTON_TEXT and AD_BUTTON_URL:
            keyboard = InlineKeyboardMarkup([[InlineKeyboardButton(f"🔗 {AD_BUTTON_TEXT}", url=AD_BUTTON_URL)]])
            await update.message.reply_text("✅ আপনার ফাইল পাঠানো হয়েছে!\n\n📢 আমাদের sponsor দেখুন:", reply_markup=keyboard)
        else:
            await update.message.reply_text("✅ আপনার ফাইল পাঠানো হয়েছে!")
    except Exception as e:
        logger.error(f"Forward error: {e}")
        await update.message.reply_text("❌ ফাইলটি পাওয়া যায়নি। লিংকটি সঠিক কিনা দেখুন।")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    args = context.args

    if FSUB_IDS:
        not_joined = await check_subscription(context.bot, user.id)
        if not_joined:
            keyboard = await build_fsub_keyboard(context.bot, not_joined)
            await update.message.reply_text(
                "⚠️ *ফাইল পেতে হলে আগে নিচের channel/group গুলোতে join করুন!*\n\nJoin করার পর 'Try Again' বাটনে চাপুন।",
                reply_markup=keyboard, parse_mode="Markdown"
            )
            if args:
                context.user_data["pending_file"] = args[0]
            return

    if args:
        await deliver_file(update, context, args[0])
    else:
        await update.message.reply_text(
            f"👋 স্বাগতম, {user.first_name}!\n\nএই বটের মাধ্যমে ফাইল ডাউনলোড করতে পারবেন।\nAdmin এর কাছ থেকে একটি লিংক নিন এবং ক্লিক করুন।"
        )


async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "check_sub":
        not_joined = await check_subscription(context.bot, query.from_user.id) if FSUB_IDS else []
        if not_joined:
            keyboard = await build_fsub_keyboard(context.bot, not_joined)
            await query.edit_message_text("❌ এখনো সব channel join করেননি! Join করুন তারপর আবার চেষ্টা করুন।", reply_markup=keyboard, parse_mode="Markdown")
        else:
            await query.edit_message_text("✅ সব channel join করা হয়েছে! এখন আবার লিংকে ক্লিক করুন।")
            pending = context.user_data.pop("pending_file", None)
            if pending:
                await deliver_file(update, context, pending)


async def genlink(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        await update.message.reply_text("⛔ Permission নেই।")
        return
    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text("ব্যবহার: /genlink <message_id>\nউদাহরণ: /genlink 25")
        return
    link = make_start_link(context.args[0])
    await update.message.reply_text(f"✅ *লিংক তৈরি হয়েছে!*\n\n🔗 `{link}`\n\nএই লিংক শেয়ার করুন।", parse_mode="Markdown")


async def batch(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        return
    if len(context.args) < 2:
        await update.message.reply_text("ব্যবহার: /batch 10 15")
        return
    try:
        s, e = int(context.args[0]), int(context.args[1])
        if s > e or (e - s) > 50:
            await update.message.reply_text("❌ Range সঠিক নয় (সর্বোচ্চ ৫০টি)।")
            return
        links = "\n".join([f"• `{make_start_link(str(i))}`" for i in range(s, e + 1)])
        await update.message.reply_text(f"✅ *{e-s+1}টি লিংক:*\n\n{links}", parse_mode="Markdown")
    except ValueError:
        await update.message.reply_text("❌ সংখ্যা দিন।")


async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        return
    msg = update.message
    if not (msg.document or msg.video or msg.audio or msg.photo):
        return
    try:
        forwarded = await msg.forward(chat_id=CHANNEL_ID)
        link = make_start_link(str(forwarded.message_id))
        await msg.reply_text(f"✅ *Channel এ আপলোড হয়েছে!*\n\n🔗 `{link}`\n\n📌 Message ID: `{forwarded.message_id}`", parse_mode="Markdown")
    except Exception as e:
        await msg.reply_text(f"❌ Error: {e}")


async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        return
    bot_info = await context.bot.get_me()
    fsub_text = "\n".join(FSUB_IDS) if FSUB_IDS else "সেট করা নেই"
    await update.message.reply_text(
        f"🤖 *Bot Info:*\nName: {bot_info.full_name}\nUsername: @{bot_info.username}\n\n"
        f"📦 Storage Channel: `{CHANNEL_ID}`\n"
        f"👥 Force Subscribe:\n{fsub_text}\n\n"
        f"📢 Ad Message: {'✅ সেট আছে' if AD_MESSAGE else '❌ নেই'}\n"
        f"🔘 Ad Button: {'✅ সেট আছে' if AD_BUTTON_URL else '❌ নেই'}",
        parse_mode="Markdown"
    )


def main():
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN সেট করা নেই!")
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("genlink", genlink))
    app.add_handler(CommandHandler("batch", batch))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CallbackQueryHandler(callback_handler))
    app.add_handler(MessageHandler(filters.Document.ALL | filters.VIDEO | filters.AUDIO | filters.PHOTO, handle_file))
    logger.info("✅ Bot চালু হয়েছে!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
