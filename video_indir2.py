import os
import winreg
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from yt_dlp import YoutubeDL

def gercek_masaustu_yolu():
    try:
        reg_path = r"Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders"
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path) as key:
            desktop, _ = winreg.QueryValueEx(key, "Desktop")
            return os.path.expandvars(desktop)
    except Exception:
        desktop = os.path.join(os.path.expanduser("~"), "Desktop")
        if not os.path.exists(desktop):
            desktop = os.path.join(os.path.expanduser("~"), "Masaüstü")
        return desktop

def kaynak_koddan_video_bul(url):
    """yt-dlp'nin patladığı php sayfalarında, HTML içindeki gerçek video linkini arar"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            return None
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 1. Senaryo: <video> veya <source> etiketlerini ara
        for video_tag in soup.find_all(['video', 'source']):
            src = video_tag.get('src') or video_tag.get('data-src')
            if src:
                # Göreceli linkleri (örn: /uploads/video.mp4) tam linke çevirir
                return urljoin(url, src)
                
        # 2. Senaryo: iframe içinde gömülü video var mı kontrol et
        for iframe in soup.find_all('iframe'):
            src = iframe.get('src')
            if src and any(ext in src for ext in ['.mp4', '.m3u8', 'player']):
                return urljoin(url, src)
                
    except Exception as e:
        print(f"[-] Sayfa analizi sırasında hata: {e}")
    return None

def video_indir():
    video_url = input("\n[>] Lütfen php'li video linkini yapıştırın ve ENTER'a basın: ").strip()
    
    if not video_url:
        print("[-] Geçersiz link!")
        return

    desktop_path = gercek_masaustu_yolu()
    
    # İndirme konfigürasyonu
    ydl_opts = {
        'outtmpl': os.path.join(desktop_path, '%(title)s.%(ext)s'),
        'format': 'mp4/best/bestvideo+bestaudio',
        'no_warnings': True,
        'quiet': False
    }

    print("\n[*] Aşama 1: Standart yöntemle video sorgulanıyor...")
    try:
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])
        print("\n[+] BAŞARILI! Video direkt Masaüstüne indirildi.")
        return
    except Exception:
        print("[-] Standart yöntem başarısız oldu. Gelişmiş mod devreye giriyor...")

    print("[*] Aşama 2: PHP sayfasının kaynak kodları taranıyor...")
    gercek_link = kaynak_koddan_video_bul(video_url)
    
    if gercek_link:
        print(f"[+] Gizli video kaynağı başarıyla yakalandı: {gercek_link}")
        print("[*] Video Masaüstüne indiriliyor...")
        try:
            # Yakalanan ham video linkini indirmesi için tekrar yt-dlp'ye paslıyoruz
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([gercek_link])
            print("\n[+] BAŞARILI! Zorlu video doğrudan Masaüstüne indirildi.")
        except Exception as e:
            print(f"[-] Video çekilemedi: {e}")
    else:
        print("\n[-] Maalesef bu sitenin video korumasını otomatik geçemedim.")
        print("[💡 İpucu] Videonun üzerine sağ tıklayıp 'Video adresini kopyala' diyerek çıkan linki buraya yapıştırmayı deneyebilirsin.")

if __name__ == "__main__":
    video_indir()
