import os
import requests
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from concurrent.futures import ThreadPoolExecutor
import time
import threading
import json
from ttkthemes import ThemedTk
import urllib.parse
import re
import requests.exceptions
import random

class IndiriciUygulama(ThemedTk):
    def __init__(self):
        super().__init__(theme="arc")
        self.title("MultiDownload")
        self.geometry("1000x800")

        # Dil değişkenini tanımla
        self.dil = tk.StringVar(value="en")

        # Diğer değişkenleri tanımla
        self.txt_dosya_adi = tk.StringVar()
        self.indirilecek_klasor = tk.StringVar(value=os.path.join(os.path.expanduser("~"), "Downloads"))
        self.indirme_hizi_limit = tk.IntVar(value=0)
        self.proxy_adresi = tk.StringVar(value="")
        self.es_zamanli_indirme = tk.IntVar(value=4)
        self.otomatik_baslat = tk.BooleanVar(value=False)
        self.tamamlandiginda_bildir = tk.BooleanVar(value=True)

        self.indirme_listesi = []
        self.indirme_yoneticisi = None
        self.duraklatildi = False

        # Dil tabanlı metinleri yükle
        self.diller = {
            "en": {
                "title": "Advanced Bulk File Downloader",
                "txt_dosyasi": "TXT File:",
                "url_ekle": "Add URL",
                "indirme_klasoru": "Download Folder:",
                "dosya_sec": "Choose File",
                "klasor_sec": "Choose Folder",
                "baslat": "Start Download",
                "duraklat": "Pause",
                "devam_et": "Resume",
                "secili_urlleri_kaldir": "Remove Selected URLs",
                "tum_urlleri_temizle": "Clear All URLs",
                "indirme_ayarlari": "Download Settings",
                "tema_ayarlari": "Theme Settings",
                "kullanim_kilavuzu": "User Manual",
                "hakkinda": "About",
                "dosya": "File",
                "duzenle": "Edit",
                "ayarlar": "Settings",
                "yardim": "Help",
                "otomatik_baslat": "Auto Start",
                "tamamlandiginda_bildir": "Notify on Completion",
                "indirme_hizi_limi": "Download Speed Limit (KB/s) [0 FOR UNLIMITED]:",
                "proxy_adresi": "Proxy Address:",
                "es_zamanli_indirme_sayisi": "Number of Simultaneous Downloads:",
                "kaydet": "Save",
                "urlleri_yukle": "{} URL loaded.",
                "urlleri_ekle": "{} URL added.",
                "secili_urlleri_sil": "{} URL removed.",
                "tum_urlleri_temizle": "All URLs cleared.",
                "indirme_basladi": "Download started.",
                "indirme_duraklatildi": "Download paused.",
                "indirme_devam_ediyor": "Download resumed.",
                "dosya_indirildi": "'{}' downloaded.",
                "indirme_basarisiz": "'{}' failed to download: ",
                "indirme_hatasi": "HTTP Error: {}",
                "baglanti_hatasi": "Connection Error",
                "zaman_asimi": "Timeout",
                "tum_indirmeler_tamamlandi": "All downloads completed.",
                "uyari": "Warning",
                "indirme_icin_url_yok": "No URLs to download."
            },
            "de": {
                "title": "Erweiterter Massen-Dateidownloader",
                "txt_dosyasi": "TXT-Datei:",
                "url_ekle": "URL hinzufügen",
                "indirme_klasoru": "Download-Ordner:",
                "dosya_sec": "Datei auswählen",
                "klasor_sec": "Ordner auswählen",
                "baslat": "Download starten",
                "duraklat": "Pause",
                "devam_et": "Fortsetzen",
                "secili_urlleri_kaldir": "Ausgewählte URLs entfernen",
                "tum_urlleri_temizle": "Alle URLs löschen",
                "indirme_ayarlari": "Download-Einstellungen",
                "tema_ayarlari": "Theme-Einstellungen",
                "kullanim_kilavuzu": "Benutzerhandbuch",
                "hakkinda": "Über",
                "dosya": "Datei",
                "duzenle": "Bearbeiten",
                "ayarlar": "Einstellungen",
                "yardim": "Hilfe",
                "otomatik_baslat": "Automatischer Start",
                "tamamlandiginda_bildir": "Bei Abschluss benachrichtigen",
                "indirme_hizi_limi": "Download-Geschwindigkeitslimit (KB/s) [0 FÜR UNBEGRENZT]:",
                "proxy_adresi": "Proxy-Adresse:",
                "es_zamanli_indirme_sayisi": "Anzahl gleichzeitiger Downloads:",
                "kaydet": "Speichern",
                "urlleri_yukle": "{} URL geladen.",
                "urlleri_ekle": "{} URL hinzugefügt.",
                "secili_urlleri_sil": "{} URL entfernt.",
                "tum_urlleri_temizle": "Alle URLs gelöscht.",
                "indirme_basladi": "Download gestartet.",
                "indirme_duraklatildi": "Download pausiert.",
                "indirme_devam_ediyor": "Download fortgesetzt.",
                "dosya_indirildi": "'{}' heruntergeladen.",
                "indirme_basarisiz": "'{}' konnte nicht heruntergeladen werden: ",
                "indirme_hatasi": "HTTP-Fehler: {}",
                "baglanti_hatasi": "Verbindungsfehler",
                "zaman_asimi": "Zeitüberschreitung",
                "tum_indirmeler_tamamlandi": "Alle Downloads abgeschlossen.",
                "uyari": "Warnung",
                "indirme_icin_url_yok": "Keine URLs zum Herunterladen."
            }
        }

        # Ayarları yükle
        self.ayarlari_yukle()

        # Menü oluştur
        self.menu_olustur()

        # Arayüzü oluştur
        self.arayuz_olustur()

        # Temayı uygula
        self.tema_uygula()

        # Dil seçme seçeneklerini oluştur
        self.dil_sec_cerceve = ttk.Frame(self)
        self.dil_sec_cerceve.pack(pady=5)
        self.dil_sec = tk.StringVar(value="en")
        ttk.Radiobutton(self.dil_sec_cerceve, text="English", variable=self.dil, value="en", command=self.dili_degistir).pack(side=tk.LEFT)
        ttk.Radiobutton(self.dil_sec_cerceve, text="Deutsch", variable=self.dil, value="de", command=self.dili_degistir).pack(side=tk.LEFT)

        # Dili değiştir
        self.dili_degistir()

    def ayarlari_yukle(self):
        try:
            with open("ayarlar.json", "r") as f:
                ayarlar = json.load(f)
                self.indirilecek_klasor.set(ayarlar.get("indirilecek_klasor", os.path.join(os.path.expanduser("~"), "Downloads")))
                self.indirme_hizi_limit.set(ayarlar.get("indirme_hizi_limit", 0))
                self.proxy_adresi.set(ayarlar.get("proxy_adresi", ""))
                self.es_zamanli_indirme.set(ayarlar.get("es_zamanli_indirme", 4))
                self.otomatik_baslat.set(ayarlar.get("otomatik_baslat", False))
                self.tamamlandiginda_bildir.set(ayarlar.get("tamamlandiginda_bildir", True))
        except FileNotFoundError:
            pass

    def ayarlari_kaydet(self):
        ayarlar = {
            "indirilecek_klasor": self.indirilecek_klasor.get(),
            "indirme_hizi_limit": self.indirme_hizi_limit.get(),
            "proxy_adresi": self.proxy_adresi.get(),
            "es_zamanli_indirme": self.es_zamanli_indirme.get(),
            "otomatik_baslat": self.otomatik_baslat.get(),
            "tamamlandiginda_bildir": self.tamamlandiginda_bildir.get()
        }
        with open("ayarlar.json", "w") as f:
            json.dump(ayarlar, f)

    def menu_olustur(self):
        menubar = tk.Menu(self)
        self.config(menu=menubar)

        dosya_menu = tk.Menu(menubar, tearoff=0)
        dosya_menu.add_command(label=self.get_dil_metni("dosya", "File"), command=self.dosya_sec)
        dosya_menu.add_command(label=self.get_dil_metni("url_ekle", "Add URL"), command=self.url_ekle_penceresi)
        dosya_menu.add_separator()
        dosya_menu.add_command(label="Çıkış", command=self.quit)
        menubar.add_cascade(label=self.get_dil_metni("dosya", "File"), menu=dosya_menu)

        duzenle_menu = tk.Menu(menubar, tearoff=0)
        duzenle_menu.add_command(label=self.get_dil_metni("secili_urlleri_kaldir", "Remove Selected URLs"), command=self.secili_urlleri_kaldir)
        duzenle_menu.add_command(label=self.get_dil_metni("tum_urlleri_temizle", "Clear All URLs"), command=self.tum_urlleri_temizle)
        menubar.add_cascade(label=self.get_dil_metni("duzenle", "Edit"), menu=duzenle_menu)

        ayarlar_menu = tk.Menu(menubar, tearoff=0)
        ayarlar_menu.add_command(label=self.get_dil_metni("indirme_ayarlari", "Download Settings"), command=self.indirme_ayarlari_penceresi)
        ayarlar_menu.add_command(label=self.get_dil_metni("tema_ayarlari", "Theme Settings"), command=self.tema_ayarlari_penceresi)
        menubar.add_cascade(label=self.get_dil_metni("ayarlar", "Settings"), menu=ayarlar_menu)

        yardim_menu = tk.Menu(menubar, tearoff=0)
        yardim_menu.add_command(label=self.get_dil_metni("kullanim_kilavuzu", "User Manual"), command=self.kullanim_kilavuzu)
        yardim_menu.add_command(label=self.get_dil_metni("hakkinda", "About"), command=self.hakkinda)
        menubar.add_cascade(label=self.get_dil_metni("yardim", "Help"), menu=yardim_menu)

    def arayuz_olustur(self):
        self.ana_cerceve = ttk.Frame(self, padding="10")
        self.ana_cerceve.pack(fill=tk.BOTH, expand=True)
        ust_panel = ttk.Frame(self.ana_cerceve)
        ust_panel.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(ust_panel, text=self.get_dil_metni("txt_dosyasi", "TXT File:")).pack(side=tk.LEFT)
        ttk.Entry(ust_panel, textvariable=self.txt_dosya_adi, width=50).pack(side=tk.LEFT, padx=(5, 10))
        ttk.Button(ust_panel, text=self.get_dil_metni("dosya_sec", "Choose File"), command=self.dosya_sec).pack(side=tk.LEFT)
        ttk.Button(ust_panel, text=self.get_dil_metni("url_ekle", "Add URL"), command=self.url_ekle_penceresi).pack(side=tk.LEFT, padx=(10, 0))

        klasor_panel = ttk.Frame(self.ana_cerceve)
        klasor_panel.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(klasor_panel, text=self.get_dil_metni("indirme_klasoru", "Download Folder:")).pack(side=tk.LEFT)
        ttk.Entry(klasor_panel, textvariable=self.indirilecek_klasor, width=50).pack(side=tk.LEFT, padx=(5, 10))
        ttk.Button(klasor_panel, text=self.get_dil_metni("klasor_sec", "Choose Folder"), command=self.klasor_sec).pack(side=tk.LEFT)

        liste_cerceve = ttk.Frame(self.ana_cerceve)
        liste_cerceve.pack(fill=tk.BOTH, expand=True)

        self.indirme_listesi_gorunumu = ttk.Treeview(liste_cerceve, columns=("Durum", "URL", "Boyut", "Hız", "Kalan"), show="headings")
        self.indirme_listesi_gorunumu.heading("Durum", text="Durum")
        self.indirme_listesi_gorunumu.heading("URL", text="URL")
        self.indirme_listesi_gorunumu.heading("Boyut", text="Boyut")
        self.indirme_listesi_gorunumu.heading("Hız", text="Hız")
        self.indirme_listesi_gorunumu.heading("Kalan", text="Kalan Süre")
        self.indirme_listesi_gorunumu.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(liste_cerceve, orient="vertical", command=self.indirme_listesi_gorunumu.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.indirme_listesi_gorunumu.configure(yscrollcommand=scrollbar.set)

        kontrol_panel = ttk.Frame(self.ana_cerceve)
        kontrol_panel.pack(fill=tk.X, pady=10)

        self.baslat_buton = ttk.Button(kontrol_panel, text=self.get_dil_metni("baslat", "Start Download"), command=self.baslat)
        self.baslat_buton.pack(side=tk.LEFT)

        self.duraklat_buton = ttk.Button(kontrol_panel, text=self.get_dil_metni("duraklat", "Pause"), command=self.duraklat, state=tk.DISABLED)
        self.duraklat_buton.pack(side=tk.LEFT, padx=5)

        self.devam_et_buton = ttk.Button(kontrol_panel, text=self.get_dil_metni("devam_et", "Resume"), command=self.devam_et, state=tk.DISABLED)
        self.devam_et_buton.pack(side=tk.LEFT)

        self.ilerleme_cubugu = ttk.Progressbar(self.ana_cerceve, orient="horizontal", length=300, mode="determinate")
        self.ilerleme_cubugu.pack(fill=tk.X, pady=10)

        self.log = tk.Text(self.ana_cerceve, height=6, state='disabled')
        self.log.pack(fill=tk.X, pady=5)

        self.bildirim_etiketi = ttk.Label(self.ana_cerceve, text="")
        self.bildirim_etiketi.pack(pady=5)

    def tema_uygula(self):
        self.style = ttk.Style()
        self.style.configure("TButton", padding=6, relief="flat", background="#ccc")
        self.style.configure("Accent.TButton", background="#007bff", foreground="white")
        self.style.map("Accent.TButton", background=[('active', '#0056b3')])

    def dosya_sec(self):
        dosya_adi = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if dosya_adi:
            self.txt_dosya_adi.set(dosya_adi)
            self.urlleri_yukle(dosya_adi)

    def klasor_sec(self):
        klasor = filedialog.askdirectory()
        if klasor:
            self.indirilecek_klasor.set(klasor)

    def urlleri_yukle(self, dosya_adi):
        with open(dosya_adi, "r") as dosya:
            url_listesi = dosya.read().splitlines()
        for url in url_listesi:
            item_id = self.indirme_listesi_gorunumu.insert("", tk.END, values=("Bekliyor", url, "-", "-", "-"))
            self.indirme_listesi.append((item_id, url))
        self.log_ekle(self.get_dil_metni("urlleri_yukle", "{} URL loaded.").format(len(url_listesi)))

    def url_ekle_penceresi(self):
        pencere = tk.Toplevel(self)
        pencere.title(self.get_dil_metni("url_ekle", "Add URL"))
        pencere.geometry("400x300")

        ttk.Label(pencere, text=self.get_dil_metni("url_ekle", "Add URL") + " (her satıra bir URL):").pack(pady=5)
        metin_alani = tk.Text(pencere, height=10)
        metin_alani.pack(pady=5, padx=10, fill=tk.BOTH, expand=True)

        def urlleri_ekle():
            urls = metin_alani.get("1.0", tk.END).splitlines()
            for url in urls:
                if url.strip():
                    item_id = self.indirme_listesi_gorunumu.insert("", tk.END, values=("Bekliyor", url.strip(), "-", "-", "-"))
                    self.indirme_listesi.append((item_id, url.strip()))
            self.log_ekle(self.get_dil_metni("urlleri_ekle", "{} URL added.").format(len(urls)))
            pencere.destroy()

        ttk.Button(pencere, text="Ekle", command=urlleri_ekle).pack(pady=10)

    def secili_urlleri_kaldir(self):
        secili_ogeleri = self.indirme_listesi_gorunumu.selection()
        for oge in secili_ogeleri:
            item_id = oge

            for idx, (stored_id, url) in enumerate(self.indirme_listesi):
                if stored_id == item_id:
                    self.indirme_listesi.pop(idx)
                    break
            self.indirme_listesi_gorunumu.delete(item_id)
        self.log_ekle(self.get_dil_metni("secili_urlleri_sil", "{} URL removed.").format(len(secili_ogeleri)))

    def tum_urlleri_temizle(self):
        self.indirme_listesi.clear()
        for i in self.indirme_listesi_gorunumu.get_children():
            self.indirme_listesi_gorunumu.delete(i)
        self.log_ekle(self.get_dil_metni("tum_urlleri_temizle", "All URLs cleared."))

    def indirme_ayarlari_penceresi(self):
        ayarlar_penceresi = tk.Toplevel(self)
        ayarlar_penceresi.title(self.get_dil_metni("indirme_ayarlari", "Download Settings"))
        ayarlar_penceresi.geometry("400x300")

        ttk.Label(ayarlar_penceresi, text=self.get_dil_metni("indirme_hizi_limi", "Download Speed Limit (KB/s) [0 FOR UNLIMITED]:")).pack(pady=5)
        ttk.Entry(ayarlar_penceresi, textvariable=self.indirme_hizi_limit).pack(pady=5)

        ttk.Label(ayarlar_penceresi, text=self.get_dil_metni("proxy_adresi", "Proxy Address:")).pack(pady=5)
        ttk.Entry(ayarlar_penceresi, textvariable=self.proxy_adresi).pack(pady=5)

        ttk.Label(ayarlar_penceresi, text=self.get_dil_metni("es_zamanli_indirme_sayisi", "Number of Simultaneous Downloads:")).pack(pady=5)
        ttk.Entry(ayarlar_penceresi, textvariable=self.es_zamanli_indirme).pack(pady=5)

        ttk.Checkbutton(ayarlar_penceresi, text=self.get_dil_metni("otomatik_baslat", "Auto Start"), variable=self.otomatik_baslat).pack(pady=5)
        ttk.Checkbutton(ayarlar_penceresi, text=self.get_dil_metni("tamamlandiginda_bildir", "Notify on Completion"), variable=self.tamamlandiginda_bildir).pack(pady=5)

        ttk.Button(ayarlar_penceresi, text=self.get_dil_metni("kaydet", "Save"), command=lambda: [self.ayarlari_kaydet(), ayarlar_penceresi.destroy()]).pack(pady=10)

    def tema_ayarlari_penceresi(self):
        tema_penceresi = tk.Toplevel(self)
        tema_penceresi.title(self.get_dil_metni("tema_ayarlari", "Theme Settings"))
        tema_penceresi.geometry("300x400")

        canvas = tk.Canvas(tema_penceresi)
        scrollbar = ttk.Scrollbar(tema_penceresi, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        for tema in self.get_themes():
            ttk.Button(scrollable_frame, text=tema.capitalize(),
                       command=lambda t=tema: [self.set_theme(t), tema_penceresi.destroy()]).pack(pady=5, padx=10, fill=tk.X)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def kullanim_kilavuzu(self):
        messagebox.showinfo(self.get_dil_metni("kullanim_kilavuzu", "User Manual"),
                            "1. TXT dosyası seçin veya URL'leri manuel olarak ekleyin.\n"
                            "2. İndirme klasörünü seçin.\n"
                            "3. İndirme ayarlarını yapılandırın.\n"
                            "4. 'İndirmeyi Başlat' butonuna tıklayın.\n"
                            "5. İndirme durumunu ve ilerlemesini takip edin.\n"
                            "6. Gerekirse indirmeyi duraklatıp devam ettirebilirsiniz.")

    def hakkinda(self):
        messagebox.showinfo(self.get_dil_metni("hakkinda", "About"), "Gelişmiş Toplu Dosya İndirici\nVersiyon 3.0\n\nBu uygulama, toplu dosya indirme işlemlerini kolaylaştırmak için tasarlanmıştır.")

    def log_ekle(self, mesaj):
        self.log.config(state='normal')
        self.log.insert(tk.END, f"{time.strftime('%H:%M:%S')} - {mesaj}\n")
        self.log.config(state='disabled')
        self.log.see(tk.END)

    def bildirim_gonder(self, mesaj):
        self.bildirim_etiketi.config(text=mesaj)

    def dosya_indir(self, url):
        try:
            dosya_adi = self.url_to_filename(url)
            tam_yol = os.path.join(self.indirilecek_klasor.get(), dosya_adi)

            proxy = self.proxy_adresi.get()
            proxy_dict = {"http": proxy, "https": proxy} if proxy else None

            with requests.get(url, stream=True, proxies=proxy_dict, timeout=30) as yanit:
                yanit.raise_for_status()
                toplam_boyut = int(yanit.headers.get('content-length', 0))
                indirilen_boyut = 0
                baslangic_zamani = time.time()

                with open(tam_yol, "wb") as dosya:
                    for parca in yanit.iter_content(chunk_size=8192):
                        if self.duraklatildi:
                            while self.duraklatildi:
                                time.sleep(0.5)
                        if parca:
                            dosya.write(parca)
                            indirilen_boyut += len(parca)

                            if self.indirme_hizi_limit.get() > 0:
                                time.sleep(len(parca) / (self.indirme_hizi_limit.get() * 1024))

                            ilerleme = (indirilen_boyut / toplam_boyut) * 100 if toplam_boyut > 0 else 0
                            gecen_sure = time.time() - baslangic_zamani
                            hiz = indirilen_boyut / gecen_sure / 1024 if gecen_sure > 0 else 0  # KB/s
                            kalan_sure = (toplam_boyut - indirilen_boyut) / (hiz * 1024) if hiz > 0 else 0

                            for index, (stored_id, stored_url) in enumerate(self.indirme_listesi):
                                if stored_url == url:
                                    self.indirme_listesi_gorunumu.item(stored_id,
                                                                    values=("İndiriliyor", url,
                                                                            f"{indirilen_boyut / 1024 / 1024:.2f} MB / {toplam_boyut / 1024 / 1024:.2f} MB",
                                                                            f"{hiz:.2f} KB/s",
                                                                            f"{kalan_sure:.0f} saniye"))
                                    break

            self.log_ekle(self.get_dil_metni("dosya_indirildi", "'{}' downloaded.").format(dosya_adi))
            return "Tamamlandı"
        except requests.exceptions.RequestException as e:
            hata_mesaji = self.get_dil_metni("indirme_basarisiz", "'{}' failed to download: ")
            if isinstance(e, requests.exceptions.HTTPError):
                hata_mesaji += self.get_dil_metni("indirme_hatasi", "HTTP Error: {}").format(e.response.status_code)
            elif isinstance(e, requests.exceptions.ConnectionError):
                hata_mesaji += self.get_dil_metni("baglanti_hatasi", "Connection Error")
            elif isinstance(e, requests.exceptions.Timeout):
                hata_mesaji += self.get_dil_metni("zaman_asimi", "Timeout")
            else:
                hata_mesaji += str(e)
            self.log_ekle(hata_mesaji.format(url))
            return "Başarısız"
        except Exception as e:
            self.log_ekle(self.get_dil_metni("indirme_basarisiz", "'{}' failed to download: ").format(url) + str(e))
            return "Başarısız"

    def url_to_filename(self, url):
        parsed_url = urllib.parse.urlparse(url)
        path = parsed_url.path
        query = parsed_url.query

        filename = os.path.basename(path)

        if not filename:
            filename = f'MultiDownlaod{random.randint(93402394,99999999999)}.mld'

        filename = re.sub(r'[^\w\-_\. ]', '_', filename)

        if query:
            filename += '_' + re.sub(r'[^\w\-_\. ]', '_', query)[:50]

        return filename

    def baslat(self):
        if not self.indirme_listesi:
            messagebox.showwarning(self.get_dil_metni("uyari", "Warning"), self.get_dil_metni("indirme_icin_url_yok", "No URLs to download."))
            return

        self.duraklatildi = False
        self.baslat_buton.config(state=tk.DISABLED)
        self.duraklat_buton.config(state=tk.NORMAL)
        self.devam_et_buton.config(state=tk.DISABLED)

        indirilecek_klasor = self.indirilecek_klasor.get()
        if not os.path.exists(indirilecek_klasor):
            os.makedirs(indirilecek_klasor)

        self.indirme_yoneticisi = ThreadPoolExecutor(max_workers=self.es_zamanli_indirme.get())
        for item_id_and_url in self.indirme_listesi:
            self.indirme_yoneticisi.submit(self.indirme_ve_durum_guncelle, item_id_and_url)
        self.log_ekle(self.get_dil_metni("indirme_basladi", "Download started."))

    def indirme_ve_durum_guncelle(self, item_id_and_url):
        item_id, url = item_id_and_url
        durum = self.dosya_indir(url)

        for index, (stored_id, stored_url) in enumerate(self.indirme_listesi):
            if stored_url == url:
                self.indirme_listesi_gorunumu.item(stored_id, values=(durum, url, "-", "-", "-"))
                break

        if durum == "Tamamlandı" and self.tamamlandiginda_bildir.get():
            self.bildirim_gonder(self.get_dil_metni("dosya_indirildi", "'{}' downloaded.").format(url))

        if all(self.indirme_listesi_gorunumu.item(i)["values"][0] in ["Tamamlandı", "Başarısız"]
               for i in self.indirme_listesi_gorunumu.get_children()):
            self.baslat_buton.config(state=tk.NORMAL)
            self.duraklat_buton.config(state=tk.DISABLED)
            self.devam_et_buton.config(state=tk.DISABLED)
            self.bildirim_gonder(self.get_dil_metni("tum_indirmeler_tamamlandi", "All downloads completed."))

    def duraklat(self):
        self.duraklatildi = True
        self.duraklat_buton.config(state=tk.DISABLED)
        self.devam_et_buton.config(state=tk.NORMAL)
        self.log_ekle(self.get_dil_metni("indirme_duraklatildi", "Download paused."))

    def devam_et(self):
        self.duraklatildi = False
        self.duraklat_buton.config(state=tk.NORMAL)
        self.devam_et_buton.config(state=tk.DISABLED)
        self.log_ekle(self.get_dil_metni("indirme_devam_ediyor", "Download resumed."))

    def dili_degistir(self):
        self.title(self.get_dil_metni("title", "Advanced Bulk File Downloader"))
        # Arayüz elemanlarının metinlerini güncelle
        for widget in self.ana_cerceve.winfo_children():
            if isinstance(widget, ttk.Label):
                if widget.cget("text") in self.diller[self.dil.get()]:
                    widget.config(text=self.get_dil_metni(widget.cget("text")))
            elif isinstance(widget, ttk.Button):
                if widget.cget("text") in self.diller[self.dil.get()]:
                    widget.config(text=self.get_dil_metni(widget.cget("text")))

    def get_dil_metni(self, anahtar, varsayılan_metin=None):
        """Belirtilen dilde metin döndürür. Eğer metin yoksa varsayılan metin döndürülür."""
        return self.diller[self.dil.get()].get(anahtar, varsayılan_metin)


if __name__ == "__main__":
    app = IndiriciUygulama()
    app.mainloop()
