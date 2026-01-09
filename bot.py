import os, subprocess, glob, shutil
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = os.getenv("TOKEN")
DOWNLOAD_DIR = "/app/downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

async def start(update: Update, _: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎵 Envíame un link de YouTube y te lo devuelvo en MP3 (máx 50 MB).")

async def handle(update: Update, _: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    if not url.startswith(("http://","https://")):
        await update.message.reply_text("❌ Link inválido.")
        return
    await update.message.reply_text("📥 Descargando…")
    cmd = ["yt-dlp","-x","--audio-format","mp3","-o",f"{DOWNLOAD_DIR}/%(title)s.%(ext)s","--no-playlist",url]
    try:
        subprocess.run(cmd, check=True, timeout=300)
        mp3 = glob.glob(f"{DOWNLOAD_DIR}/*.mp3")[0]
        size = os.path.getsize(mp3)/(1024*1024)
        if size > 50:
            await update.message.reply_text(f"⚠️ Archivo demasiado grande ({size:.1f} MB).")
        else:
            with open(mp3,"rb") as f:
                await update.message.reply_audio(audio=f, caption="✅ Listo")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")
    finally:
        for f in glob.glob(f"{DOWNLOAD_DIR}/*"): os.remove(f)

def main():
    if not TOKEN: raise RuntimeError("Falta TOKEN")
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))
    app.run_polling()

if __name__ == "__main__":
    main()