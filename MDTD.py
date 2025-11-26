#!/usr/bin/env python3
import os
import time
import requests
import libtorrent as lt
from pathlib import Path
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# =============================
#  GOOGLE DRIVE SETUP
# =============================
def setup_drive(sa_path):
    if not os.path.exists(sa_path):
        print(f"[ERROR] File Service Account tidak ditemukan: {sa_path}")
        exit()

    scopes = ["https://www.googleapis.com/auth/drive"]
    creds = service_account.Credentials.from_service_account_file(sa_path, scopes=scopes)
    service = build("drive", "v3", credentials=creds, cache_discovery=False)
    print("[OK] Terhubung ke Google Drive.")
    return service


def ensure_drive_folder(service, name):
    query = f"name='{name}' and mimeType='application/vnd.google-apps.folder'"
    results = service.files().list(q=query).execute().get("files", [])
    
    if results:
        print(f"[OK] Folder ditemukan: {results[0]['id']}")
        return results[0]["id"]

    print("[INFO] Folder tidak ditemukan, membuat baru...")
    meta = {"name": name, "mimeType": "application/vnd.google-apps.folder"}
    folder = service.files().create(body=meta, fields="id").execute()
    print(f"[OK] Folder baru dibuat: {folder['id']}")
    return folder["id"]


def upload_to_drive(service, file_path, folder_id):
    file_metadata = {"name": os.path.basename(file_path), "parents": [folder_id]}
    media = MediaFileUpload(file_path, resumable=True)

    request = service.files().create(body=file_metadata, media_body=media)
    print(f"[UPLOAD] Mengunggah {file_path} ...")

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"Progress: {int(status.progress() * 100)}%")

    print("[OK] Upload selesai:", response.get("id"))


# =============================
#  TORRENT HANDLING
# =============================
def download_torrent(torrent_path, save_dir):
    print("[TORRENT] Memulai download...")

    ses = lt.session()
    ses.listen_on(6881, 6891)

    info = lt.torrent_info(torrent_path)
    params = {"ti": info, "save_path": save_dir}
    h = ses.add_torrent(params)

    print("[INFO] Nama torrent:", info.name())
    print("[INFO] Menghubungkan ke peers...")

    while not h.is_seed():
        s = h.status()
        print(f"{s.progress * 100:.2f}%  | Down: {s.download_rate / 1000:.1f} kB/s | Peers: {s.num_peers}")
        time.sleep(2)

    print("[DONE] Download selesai.")
    return os.path.join(save_dir, info.name())


def download_torrent_url(url, tmp):
    print("[INFO] Mengunduh file .torrent...")
    r = requests.get(url, timeout=30)

    if r.status_code != 200:
        print("[ERROR] Gagal mengunduh file torrent.")
        exit()

    path = os.path.join(tmp, "mdtd_temp.torrent")
    with open(path, "wb") as f:
        f.write(r.content)

    print("[OK] File torrent tersimpan.")
    return path


def download_from_hash(hash_code, tmp):
    url = f"https://torrage.info/torrent.php?h={hash_code}"
    print("[INFO] Mendownload torrent menggunakan hash...")
    return download_torrent_url(url, tmp)


# =============================
#  MENU
# =============================
def menu():
    print("\n===== MDTD — Magnet Download Transfer Drive =====")
    print("1. URL .torrent")
    print("2. Hash / Code torrent")
    print("3. File .torrent lokal")
    print("=================================================")
    return input("Pilih (1/2/3): ").strip()


# =============================
#  MAIN
# =============================
def main():
    save_dir = "./downloads"
    tmp_dir = "./tmp"
    Path(save_dir).mkdir(exist_ok=True)
    Path(tmp_dir).mkdir(exist_ok=True)

    sa_json = input("Lokasi file service_account.json: ").strip()
    drive_folder = input("Nama folder Google Drive: ").strip()

    drive = setup_drive(sa_json)
    folder_id = ensure_drive_folder(drive, drive_folder)

    choice = menu()

    if choice == "1":
        url = input("Masukkan URL .torrent: ").strip()
        torrent = download_torrent_url(url, tmp_dir)

    elif choice == "2":
        code = input("Masukkan hash/code torrent: ").strip()
        torrent = download_from_hash(code, tmp_dir)

    elif choice == "3":
        torrent = input("Lokasi file .torrent: ").strip()
        if not os.path.exists(torrent):
            print("[ERROR] File tidak ditemukan.")
            exit()

    else:
        print("[ERROR] Pilihan tidak valid.")
        exit()

    result = download_torrent(torrent, save_dir)

    if os.path.isdir(result):
        for root, dirs, files in os.walk(result):
            for f in files:
                upload_to_drive(drive, os.path.join(root, f), folder_id)
    else:
        upload_to_drive(drive, result, folder_id)

    print("\n[SELESAI] Semua tugas berhasil dilakukan.")


if __name__ == "__main__":
    main()
