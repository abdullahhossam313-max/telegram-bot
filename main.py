import os, base64, requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("ابعتلي أي صورة فيها كلام عربي أو انجليزي وانا هطلعهولك بذكاء اصطناعي قوي 📸")

async def ocr_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("بقرا الصورة بأقوى AI... ⏳")
    try:
        photo_file = await update.message.photo[-1].get_file()
        photo_bytes = await photo_file.download_as_bytearray()
        b64_image = base64.b64encode(photo_bytes).decode('utf-8')

        headers = {
            "Authorization": f"Bearer {OPENROUTER_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com",
            "X-Title": "Telegram OCR Bot"
        }
        data = {
            "model": "google/gemini-2.0-flash-exp:free",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Extract ALL text from this image exactly as written. Keep Arabic and English as is, preserve line breaks. Return ONLY the extracted text, no explanation."},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64_image}"}}
                    ]
                }
            ]
        }
        res = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data, timeout=60)
        res_json = res.json()
        if 'choices' not in res_json:
            print(res_json)
            await update.message.reply_text(f"حصل مشكلة في الـ API: {res_json}")
            return
            
        text = res_json['choices'][0]['message']['content']

        if len(text) > 4000:
            await update.message.reply_text(text[:4000])
            if len(text) > 4000:
                await update.message.reply_text(text[4000:8000])
        else:
            await update.message.reply_text(f"النص اللي لقيته:\n\n{text}")

    except Exception as e:
        print(f"Error: {e}")
        await update.message.reply_text(f"حصل مشكلة: {e}")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, ocr_photo))
    print("Bot is running 24/7 with Gemini quality...")
    app.run_polling()

if __name__ == "__main__":
    main()
