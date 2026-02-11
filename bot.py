from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import qrcode

# =========================
# KONFIGURASI
# =========================
TOKEN = "8489070666:AAGOVVMdxc6NieQzFKIOjQ64Q4xekI51GeI"
ADMIN_USERNAME = "mnhfxz"
NAMA_SHEET = "DATA_ABSENSI"

# =========================
# GOOGLE SHEETS
# =========================
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

creds = ServiceAccountCredentials.from_json_keyfile_name(
    "credentials.json", scope
)
client = gspread.authorize(creds)
sheet = client.open(NAMA_SHEET).sheet1

# =========================
# FUNGSI BOT
# =========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎓 SISTEM ABSENSI DIGITAL\n\n"
        "/hadir → Absen\n"
        "/rekap → Rekap (Admin)\n"
        "/qr → QR Bot"
    )

async def hadir(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    today = datetime.now().strftime("%Y-%m-%d")

    data = sheet.get_all_records()

    for row in data:
        if row["Username"] == user.username and row["Tanggal"] == today:
            await update.message.reply_text("❌ Kamu sudah absen hari ini!")
            return

    waktu = datetime.now().strftime("%H:%M:%S")

    sheet.append_row([
        user.full_name,
        user.username,
        today,
        waktu
    ])

    await update.message.reply_text(
        f"✅ Absensi berhasil!\n\n"
        f"Nama: {user.full_name}\n"
        f"Tanggal: {today}\n"
        f"Jam: {waktu}"
    )

async def rekap(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user

    if user.username != ADMIN_USERNAME:
        await update.message.reply_text("⛔ Akses ditolak!")
        return

    today = datetime.now().strftime("%Y-%m-%d")
    data = sheet.get_all_records()

    jumlah = 0
    for row in data:
        if row["Tanggal"] == today:
            jumlah += 1

    await update.message.reply_text(
        f"📊 Rekap Hari Ini\n\nJumlah hadir: {jumlah}"
    )

async def qr(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = "https://t.me/Projectabsensi_bot"
    img = qrcode.make(data)
    img.save("qr_absensi.png")

    await update.message.reply_photo(photo=open("qr_absensi.png", "rb"))

# =========================
# JALANKAN BOT
# =========================
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("hadir", hadir))
app.add_handler(CommandHandler("rekap", rekap))
app.add_handler(CommandHandler("qr", qr))

print("🚀 Bot aktif...")
app.run_polling()
