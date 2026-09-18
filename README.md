
# Telegram -> Discord Bridge Bot

Bot simpel: apapun yang lu kirim ke bot Telegram, bakal di-forward ke channel Discord via Webhook.

### Fitur
- Support teks, foto, video, file, dokumen, voice note, audio, sticker, gif
- Ada filter user (optional)
- Keep-alive web server biar bisa deploy di Render / Koyeb gratis

### Cara Deploy Gratis (2 Menit)

#### 1. Siapin Bot & Webhook
- Chat @BotFather di Telegram > `/newbot` > dapet `BOT_TOKEN`
- Discord > Channel > Edit Channel > Integrations > Webhooks > Create Webhook > Copy URL

#### 2. Upload ke Github
Upload semua file di folder ini ke repo Github baru lu.

#### 3. Deploy

**Pilihan A: Koyeb (Rekomendasi, gak tidur)**
1. Daftar di koyeb.com pake Github
2. Create App > From Github > Pilih repo ini
3. Builder: Buildpack
4. Run command: `python main.py`
5. Add Env Variables:
   - `BOT_TOKEN`
   - `DISCORD_WEBHOOK`
   - `ALLOWED_USER_IDS` (optional, isi ID Telegram lu, pisah koma. Contoh: `123456,789012`)
6. Deploy

**Pilihan B: Render (Gratis tanpa kartu kredit)**
1. Daftar di render.com
2. New + > Web Service > Connect repo ini
3. Build Command: `pip install -r requirements.txt`
4. Start Command: `python main.py`
5. Add Env Variables sama kayak di atas
6. Deploy
7. Biar gak tidur: daftar di uptimerobot.com, suruh ping URL Render lu tiap 5 menit.

### Cara dapet Telegram User ID
Chat @userinfobot di Telegram, nanti dia kasih ID lu.

### Variabel Env
| Nama | Wajib | Deskripsi |
|---|---|---|
| BOT_TOKEN | Ya | Token dari @BotFather |
| DISCORD_WEBHOOK | Ya | URL Webhook Discord |
| ALLOWED_USER_IDS | Tidak | Kalo diisi, cuma ID itu yang bisa pake bot |

Enjoy!
