# Torrent Downloader to Google Drive

Script Python untuk mengunduh file torrent (.torrent atau hash torrent) dan mengunggah hasilnya langsung ke Google Drive menggunakan Google Service Account.

Proyek ini dibuat agar proses download torrent menjadi lebih mudah, cepat, dan aman tanpa perlu membuka torrent client secara manual.

---

## ✨ Fitur Utama

- Download torrent melalui:
  - URL `.torrent`
  - Hash/Code torrent (contoh: `25D21CF1F2732C2CCBD7261A7D5FCC95FAE1BBB2`)
  - File `.torrent` lokal
- Menu interaktif saat program dijalankan.
- Setup Google Drive otomatis.
- Upload hasil download ke folder khusus di Google Drive.
- Struktur kode bersih dan mudah dikembangkan.

---

## 📦 Persyaratan

Pastikan sudah menginstal dependensi berikut:

```bash
pip install libtorrent
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
