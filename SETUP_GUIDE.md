# 📖 Telegram File Sharing Bot — সম্পূর্ণ Setup গাইড

## প্রয়োজনীয় জিনিস
- Telegram Account
- GitHub Account (ফ্রি) → github.com
- Render Account (ফ্রি) → render.com

---

## ধাপ ১: Bot Token নিন

1. Telegram এ @BotFather খুলুন
2. `/newbot` লিখুন
3. Bot এর নাম দিন (যেকোনো নাম)
4. Username দিন (শেষে `_bot` থাকতে হবে, যেমন: `myfiles_bot`)
5. BotFather আপনাকে একটি **Token** দেবে — এটা সেভ করুন
   - উদাহরণ: `7123456789:AAFxxxxxxxxxxxxxxxxxxxxxxxx`

---

## ধাপ ২: Channel তৈরি ও Bot কে Admin করুন

1. Telegram এ একটি **নতুন Channel** তৈরি করুন (Private বা Public যেকোনো)
2. Channel Settings → Administrators → আপনার bot কে Admin করুন
3. Channel এর ID নিন:
   - Channel এ যেকোনো message forward করুন @userinfobot এ
   - সে আপনাকে Channel ID দেবে (যেমন: `-1001234567890`)

---

## ধাপ ৩: আপনার Telegram User ID নিন

1. @userinfobot এ `/start` দিন
2. সে আপনার **ID** দেবে (যেমন: `987654321`)
3. এটা ADMIN_IDS এ ব্যবহার হবে

---

## ধাপ ৪: GitHub এ Code Upload করুন

1. github.com এ Login করুন
2. **New Repository** তৈরি করুন
   - Name: `telegram-file-bot`
   - Public বা Private যেকোনো
3. নিচের ৩টি ফাইল upload করুন:
   - `bot.py`
   - `requirements.txt`
   - `render.yaml`

---

## ধাপ ৫: Render এ Deploy করুন

1. render.com এ যান → GitHub দিয়ে Login করুন
2. **New** → **Background Worker** ক্লিক করুন
3. আপনার GitHub repo সিলেক্ট করুন
4. নিচের **Environment Variables** গুলো সেট করুন:

| Key | Value (উদাহরণ) |
|-----|----------------|
| `BOT_TOKEN` | `7123456789:AAFxxx...` |
| `CHANNEL_ID` | `-1001234567890` |
| `ADMIN_IDS` | `987654321` |
| `BOT_USERNAME` | `myfiles_bot` |

5. **Deploy** বাটন চাপুন
6. কিছুক্ষণ অপেক্ষা করুন — Bot চালু হয়ে যাবে!

---

## ✅ Bot ব্যবহার করার নিয়ম

### ফাইল আপলোড ও Link তৈরি করার ২টি পদ্ধতি:

#### পদ্ধতি ১ — Bot এ সরাসরি ফাইল পাঠান (সহজ)
1. Bot এ যান
2. যেকোনো ফাইল/ভিডিও/ছবি পাঠান
3. Bot নিজেই Channel এ আপলোড করবে এবং link দেবে

#### পদ্ধতি ২ — Channel থেকে Message ID দিয়ে link তৈরি
1. Channel এ ফাইল আপলোড করুন
2. সেই Message এর ID নিন (Channel URL এ দেখা যায়)
3. Bot এ `/genlink 25` লিখুন (25 = message ID)
4. Bot আপনাকে shareable link দেবে

### User দের জন্য:
- Link এ ক্লিক করলে Bot এ যাবে
- Bot স্বয়ংক্রিয়ভাবে ফাইলটি পাঠিয়ে দেবে

---

## 📋 সব Command

| Command | কাজ |
|---------|-----|
| `/start` | Bot শুরু করুন |
| `/genlink 25` | Message ID দিয়ে link তৈরি |
| `/batch 10 20` | ১০ থেকে ২০ পর্যন্ত সব link একসাথে |
| `/stats` | Bot এর তথ্য দেখুন |

---

## ❓ সমস্যা হলে

- **Bot respond করছে না** → Render dashboard এ Logs চেক করুন
- **Channel এ forward হচ্ছে না** → Bot কে Channel এ Admin করুন কিনা দেখুন
- **Link কাজ করছে না** → BOT_USERNAME সঠিক আছে কিনা দেখুন
