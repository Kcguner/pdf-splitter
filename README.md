# PDF Ayırıcı ✂️

<p align="center">
  <b>PDF'lerinizi tek tıkla sayfa sayfa ayırın.</b><br>
  Modern, hızlı ve ücretsiz masaüstü uygulaması.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/CustomTkinter-UI-2563EB?style=for-the-badge" alt="CustomTkinter">
  <img src="https://img.shields.io/badge/pypdf-powered-red?style=for-the-badge" alt="pypdf">
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="MIT">
</p>

---

## ✨ Özellikler

- 📄 **Sayfa sayfa bölme** — `rapor.pdf` → `rapor_sayfa_1.pdf`, `rapor_sayfa_2.pdf`, ...
- 📦 **Toplu işlem** — Birden fazla PDF seçip tek seferde ayırın
- 📁 **Akıllı çıktı** — Her PDF için otomatik `ad_sayfalar/` klasörü (isteğe bağlı)
- 👀 **Sayfa önizleme** — Listeye ekler eklemez sayfa sayısını görün
- 📊 **Canlı ilerleme** — Progress bar + durum logu
- 🧵 **Donmayan arayüz** — Ayırma işlemi arka planda (threading) çalışır
- 🔒 **Şifreli PDF koruması** — Şifreli dosyalar atlanır, program çökmez
- 🎨 **Modern UI** — CustomTkinter ile temiz, açık tema arayüz (Türkçe)

## 🖼️ Ekran Görüntüsü

> Uygulamayı çalıştırıp ekran görüntüsü alıp buraya ekleyebilirsiniz:
> `assets/screenshot.png`

```
PDF Ayırıcı
├── ＋ PDF Ekle  |  Temizle
├── 📋 PDF listesi (sayfa sayısı ile)
├── 📁 Çıkış klasörü seçimi
├── ☑ Her PDF için ayrı klasör oluştur
└── ✂ PDF'leri Ayır
```

Örnek çıktı yapısı:

```
Masaüstü/
└── rapor_sayfalar/
    ├── rapor_sayfa_1.pdf
    ├── rapor_sayfa_2.pdf
    └── rapor_sayfa_3.pdf
```

## 🚀 Kurulum

### 1. Kaynaktan çalıştırma

```bash
git clone https://github.com/Kcguner/pdf-ayirici.git
cd pdf-ayirici

# (önerilir) sanal ortam
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt
python pdf_ayirici.py
```

### 2. Gereksinimler

```
pypdf>=5.0
customtkinter>=5.2.0
```

Python **3.10+** önerilir. Tkinter çoğu Python kurulumuyla birlikte gelir.

### 3. EXE olarak kullanma (Windows)

Repo'da `PDF_Ayirici.spec` hazır gelir. Tek komutla exe üretin:

```bash
pip install pyinstaller
pyinstaller PDF_Ayirici.spec
# Çıktı: dist/PDF_Ayirici.exe
```

> Not: `build/` ve `dist/` klasörleri repoya dahil değildir (`.gitignore` ile dışlanır). EXE'yi kendiniz üretin veya [Releases](../../releases) sayfasından indirin.

## 📖 Kullanım

1. **PDF Ekle** butonuna basın, bir veya birden fazla PDF seçin
2. **Çıkış klasörü** seçin (varsayılan: Masaüstü)
3. Dilerseniz **"Her PDF için ayrı klasör oluştur"** seçeneğini açık bırakın
4. **PDF'leri Ayır** butonuna basın — bitti! 🎉

## 🛠️ Proje Yapısı

```
pdf-ayirici/
├── pdf_ayirici.py      # Ana uygulama (CustomTkinter + pypdf)
├── requirements.txt    # Bağımlılıklar
├── PDF_Ayirici.spec    # PyInstaller yapılandırması
├── .gitignore
├── LICENSE
└── README.md
```

## 🤝 Katkıda Bulunma

Katkılara açık! 🧡

1. Fork'layın
2. Yeni branch açın (`git checkout -b feature/harika-ozellik`)
3. Commit'leyin (`git commit -m "Harika özellik eklendi"`)
4. Push'layın (`git push origin feature/harika-ozellik`)
5. Pull Request açın

Öneri / hata bildirimi için [Issues](../../issues) sekmesini kullanın.

Fikirler:
- [ ] Sürükle-bırak ile PDF ekleme
- [ ] Sayfa aralığı seçme (örn. 1-5, 10-12)
- [ ] Karanlık mod geçişi
- [ ] İngilizce dil desteği

## 📝 Lisans

Bu proje [MIT](LICENSE) lisansı ile lisanslanmıştır.

## ⭐ Destek

İşinize yaradıysa yıldız vermeyi unutmayın — motivasyon oluyor! ⭐

---

<p align="center">Python + CustomTkinter + pypdf ile ❤️ ile geliştirildi</p>
