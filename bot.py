from pyrogram import Client, filters
from pyrogram.types import Message
from dotenv import load_dotenv
import qrcode
from PIL import Image, ImageDraw, ImageFont
import os

load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
UPI_ID = os.getenv("UPI_ID")

app = Client("upi-payment-bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

user_data = {}

# Listen for bot mention to ask for amount
@app.on_message(filters.private | filters.group & filters.regex(r'@\w+'))
def mention_handler(client, message: Message):
    user_data[message.from_user.id] = {}
    message.reply_text("Enter the amount you want to pay:")

# Listen for number input
@app.on_message(filters.text & filters.private | filters.group)
def amount_handler(client, message: Message):
    try:
        amount = float(message.text.strip())
        upi_link = f"upi://pay?pa={UPI_ID}&pn=Payment&am={amount}&cu=INR"

        # Generate QR
        qr = qrcode.make(upi_link)
        qr.save("qr.png")

        # Paste on background
        bg = Image.open("background.jpg").convert("RGB")
        qr_img = Image.open("qr.png").resize((400, 400))
        bg.paste(qr_img, (140, 300))  # Adjust position based on your background

        # Add text
        draw = ImageDraw.Draw(bg)
        font = ImageFont.load_default()
        draw.text((140, 720), f"Payment of ₹{amount}\nMake sure you are paying to {UPI_ID}", fill="black", font=font)

        file_path = f"upi_qr_{message.from_user.id}.jpg"
        bg.save(file_path)

        message.reply_photo(
            photo=file_path,
            caption=f"Scan this QR code to pay ₹{amount}.\nOr click the button below.\n\nConfirm UPI: `{UPI_ID}`",
            reply_markup=None,
            parse_mode="markdown"
        )

        os.remove("qr.png")
        os.remove(file_path)

    except ValueError:
        pass  # Ignore non-numeric messages

app.run()
