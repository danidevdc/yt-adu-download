import os
import subprocess
import glob
import shutil
import re
import shlex
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = os.getenv("TOKEN")
DOWNLOAD_DIR = "/app/downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

async def start(update: Update, _: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎵 HOLA Envíame un link de YouTube y te lo devuelvo en MP3 (máx 50 MB).")

async def handle(update: Update, _: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    if not url.startswith(("http://", "https://")):
        await update.message.reply_text("❌ Link inválido.")
        return

    # Limpia parámetros de lista / radio
    url = re.sub(r'&list=.*', '', url)
    url = re.sub(r'&start_radio=.*', '', url)

    await update.message.reply_text("📥 Descargando…")

    cmd = [
        "yt-dlp",
        "-x", "--audio-format", "mp3",
        "-o", os.path.join(DOWNLOAD_DIR, "%(title)s.%(ext)s"),
        "--no-playlist",
        "--no-warnings",
        shlex.quote(url)  # escapa & y espacios
    ]

    try:
        subprocess.run(cmd, check=True, timeout=300)
        mp3_files = glob.glob(os.path.join(DOWNLOAD_DIR, "*.mp3"))
        if not mp3_files:
            await update.message.reply_text("❌ No se pudo encontrar el archivo MP3.")
            return

        file_path = mp3_files[0]
        size = os.path.getsize(file_path) / (1024 * 1024)
        if size > 50:
            await update.message.reply_text(f"⚠️ Archivo demasiado grande ({size:.1f} MB).")
        else:
            with open(file_path, "rb") as audio_file:
                await update.message.reply_audio(audio=audio_file, caption="✅ Listo")
    except subprocess.TimeoutExpired:
        await update.message.reply_text("⏱️ La descarga tardó demasiado.")
    except subprocess.CalledProcessError as e:
        await update.message.reply_text(f"❌ Error en yt-dlp: {e.stderr[:200] if e.stderr else str(e)}")
    finally:
        for f in glob.glob(os.path.join(DOWNLOAD_DIR, "*")): os.remove(f)

def main():
    if not TOKEN: raise RuntimeError("Falta TOKEN")
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))
    app.run_polling()

if __name__ == "__main__":
    main()