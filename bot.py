import discord
from discord.ext import commands
import os
import cv2
import numpy as np
from PIL import Image
import sqlite3


# Bot ayarları
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Klasör ayarları
SAVE_FOLDER = "saved_images"
MASK_PATH = os.path.join(SAVE_FOLDER, "mask.png")
PHOTO_INPUT_PATH = os.path.join(SAVE_FOLDER, "photo_input.jpg")
PHOTO_OUTPUT_PATH = os.path.join(SAVE_FOLDER, "filtered_face.png")
os.makedirs(SAVE_FOLDER, exist_ok=True)

@bot.event
async def on_ready():
    print(f'{bot.user} olarak giriş yapıldı.')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    await bot.process_commands(message)

@bot.command()
async def kaydet(ctx):
    if not ctx.message.attachments:
        await ctx.send("Lütfen bir resim dosyası ekleyin.")
        return

    attachment = ctx.message.attachments[0]
    temp_path = os.path.join(SAVE_FOLDER, "temp_image")
    await attachment.save(temp_path)
    try:
        with Image.open(temp_path) as img:
            img.save(MASK_PATH, format="PNG")
        await ctx.send(f"Maske başarıyla PNG olarak kaydedildi: {MASK_PATH}")
    except Exception as e:
        await ctx.send(f"Maske kaydedilirken hata oluştu: {e}")
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

@bot.command()
async def foto(ctx):
    if not os.path.exists(MASK_PATH):
        await ctx.send("Önce !kaydet ile bir maske resmi yükleyin.")
        return

    if not ctx.message.attachments:
        await ctx.send("Lütfen filtrelenecek bir fotoğraf ekleyin.")
        return

    await ctx.message.attachments[0].save(PHOTO_INPUT_PATH)

    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    mask = cv2.imread(MASK_PATH, cv2.IMREAD_UNCHANGED)
    img = cv2.imread(PHOTO_INPUT_PATH)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    for (x, y, w, h) in faces:
        resized_mask = cv2.resize(mask, (w, h))
        for i in range(h):
            for j in range(w):
                if y + i >= img.shape[0] or x + j >= img.shape[1]:
                    continue
                if resized_mask[i, j, 3] > 0:
                    img[y + i, x + j] = resized_mask[i, j][:3]

    cv2.imwrite(PHOTO_OUTPUT_PATH, img)
    await ctx.send(file=discord.File(PHOTO_OUTPUT_PATH))

@bot.command()
async def video(ctx):
    if not os.path.exists(MASK_PATH):
        await ctx.send("Önce bir PNG maske resmi gönderin ya da !kaydet komutunu kullanın.")
        return

    await ctx.send("Video başlatıldı. 'q' ile çıkabilirsiniz.")

    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    mask = cv2.imread(MASK_PATH, cv2.IMREAD_UNCHANGED)
    video_capture = cv2.VideoCapture(0)

    while True:
        ret, frame = video_capture.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        for (x, y, w, h) in faces:
            resized_mask = cv2.resize(mask, (w, h))
            for i in range(h):
                for j in range(w):
                    if y + i >= frame.shape[0] or x + j >= frame.shape[1]:
                        continue
                    if resized_mask[i, j, 3] > 0:
                        frame[y + i, x + j] = resized_mask[i, j][:3]

        cv2.imshow("Maskelenmis Video", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    video_capture.release()
    cv2.destroyAllWindows()
@bot.command()
async def info(ctx):
    await ctx.send("Merhaba! Benim adım MaskeBot. Benimle çoğu yüz maskeleme işlemlerini halledebirirsin.\n Botu çalıştırmadan önce şunu bilmelisin ki !kaydet komutuna herhangi bir resim koymalısın. Bu resimler png olsa çok daha güzel filtreler. Png resim olmasa da resmi png'ye dönüştürebiliyorum ama kalite biraz daha azalıyor.\n !video komutunu kullanırsanız kameranız açılır ve !kaydet'e kaydettiğiniz png resim otomatik olarak yüzünüze maskelenir.\n Ve eğer !foto komutunu kullanırsanız ise !foto komutu ile gönderdiğiniz resimi !kaydet'teki resim ile maskelerim.\n Daha projeye birçok şey eklenebilir. Eğer öneri veya şikayetiniz olursa !önveşik komutunu kullandıktan sonra mesajınızı bırakıp bize iletebilirsiniz.\n Anlayışınız için çok teşekkürler. Şimdilik Görüşürüz!")
# Token'i config.py dosyasından al

@bot.command()
async def önveşik(ctx, *, mesaj=None):
    kullanici = str(ctx.author)

    if not mesaj :
        await ctx.send("Lütfen koddan sonraki alana öneri ve şikayetlerinizi yazın.")
        return

    # Veritabanına kaydet
    conn = sqlite3.connect('oneri_ve_sikayetler.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO oneriler (kullanici, mesaj) VALUES (?, ?)", (kullanici, mesaj))
    conn.commit()
    conn.close()

    await ctx.send("Geri bildiriminiz kaydedildi. Teşekkürler!")
    

from config import token
bot.run(token)
