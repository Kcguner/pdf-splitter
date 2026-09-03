import os
import threading
from pathlib import Path
import customtkinter as ctk
from tkinter import filedialog, messagebox
from pypdf import PdfReader, PdfWriter

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

class PdfAyiriciApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("PDF Ayırıcı - Sayfa Sayfa Böl")
        self.geometry("720x620")
        self.minsize(680, 580)
        self.pdf_dosyalari = []
        self.cikti_klasoru = str(Path.home() / "Desktop")

        self._build_ui()

    def _build_ui(self):
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=24, pady=(20, 10))

        title = ctk.CTkLabel(header, text="PDF Ayırıcı", font=ctk.CTkFont(size=24, weight="bold"))
        title.pack(anchor="w")
        subtitle = ctk.CTkLabel(header, text="PDF'lerinizi tek tıkla sayfa sayfa ayırın", text_color="gray50", font=ctk.CTkFont(size=13))
        subtitle.pack(anchor="w", pady=(2,0))

        # Card - Dosya seçimi
        card = ctk.CTkFrame(self, corner_radius=16)
        card.pack(fill="both", expand=True, padx=20, pady=12)

        # Üst butonlar
        top_btn_frame = ctk.CTkFrame(card, fg_color="transparent")
        top_btn_frame.pack(fill="x", padx=18, pady=(18,10))

        self.btn_ekle = ctk.CTkButton(top_btn_frame, text="＋  PDF Ekle", width=140, height=38, corner_radius=10,
                                      font=ctk.CTkFont(size=13, weight="bold"),
                                      command=self.pdf_ekle)
        self.btn_ekle.pack(side="left", padx=(0,10))

        self.btn_temizle = ctk.CTkButton(top_btn_frame, text="Temizle", width=90, height=38, corner_radius=10,
                                         fg_color="#E8E8E8", text_color="#333", hover_color="#D8D8D8",
                                         font=ctk.CTkFont(size=13),
                                         command=self.liste_temizle)
        self.btn_temizle.pack(side="left")

        self.lbl_sayi = ctk.CTkLabel(top_btn_frame, text="0 dosya seçili", text_color="gray50", font=ctk.CTkFont(size=12))
        self.lbl_sayi.pack(side="right", padx=8)

        # Dosya listesi
        self.scroll = ctk.CTkScrollableFrame(card, height=210, corner_radius=10, fg_color="#F5F5F7")
        self.scroll.pack(fill="both", expand=False, padx=18, pady=6)
        self._bos_mesaj = ctk.CTkLabel(self.scroll, text="Henüz PDF eklenmedi.\n'PDF Ekle' ile başlayın veya birden fazla PDF seçebilirsiniz.",
                                       text_color="gray50", font=ctk.CTkFont(size=12), justify="center")
        self._bos_mesaj.pack(pady=40)

        # Çıktı klasörü
        out_frame = ctk.CTkFrame(card, fg_color="transparent")
        out_frame.pack(fill="x", padx=18, pady=(14,6))
        ctk.CTkLabel(out_frame, text="Çıkış Klasörü:", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w")
        row = ctk.CTkFrame(out_frame, fg_color="transparent")
        row.pack(fill="x", pady=(6,0))
        self.entry_out = ctk.CTkEntry(row, placeholder_text="Çıkış klasörü seçin", height=36, corner_radius=10)
        self.entry_out.pack(side="left", fill="x", expand=True, padx=(0,10))
        self.entry_out.insert(0, self.cikti_klasoru)
        ctk.CTkButton(row, text="Gözat", width=90, height=36, corner_radius=10,
                      fg_color="#2B2B2B", hover_color="#1A1A1A",
                      command=self.cikti_sec).pack(side="right")

        # Seçenekler
        opt_frame = ctk.CTkFrame(card, fg_color="transparent")
        opt_frame.pack(fill="x", padx=18, pady=(10, 6))
        self.var_alt_klasor = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(opt_frame, text="Her PDF için ayrı klasör oluştur", variable=self.var_alt_klasor,
                        font=ctk.CTkFont(size=12)).pack(anchor="w")
        ctk.CTkLabel(opt_frame, text="Örn: dosya.pdf → dosya_sayfalar/ dosya_sayfa_1.pdf, dosya_sayfa_2.pdf ...",
                     text_color="gray50", font=ctk.CTkFont(size=11)).pack(anchor="w", pady=(2,0))

        # Progress + Log
        self.progress = ctk.CTkProgressBar(card, height=8, corner_radius=4)
        self.progress.pack(fill="x", padx=18, pady=(14,8))
        self.progress.set(0)

        self.lbl_durum = ctk.CTkLabel(card, text="Hazır", text_color="gray50", font=ctk.CTkFont(size=11))
        self.lbl_durum.pack(anchor="w", padx=18)

        self.log = ctk.CTkTextbox(card, height=90, corner_radius=10, fg_color="#FAFAFA", text_color="#333",
                                  font=ctk.CTkFont(size=11))
        self.log.pack(fill="x", padx=18, pady=(6, 12))
        self.log.configure(state="disabled")

        # Alt buton - Ayır
        bottom = ctk.CTkFrame(self, fg_color="transparent")
        bottom.pack(fill="x", padx=20, pady=(0,18))
        self.btn_ayir = ctk.CTkButton(bottom, text="✂   PDF'leri Ayır", height=46, corner_radius=12,
                                      font=ctk.CTkFont(size=15, weight="bold"),
                                      fg_color="#2563EB", hover_color="#1D4ED8",
                                      command=self.ayir_baslat)
        self.btn_ayir.pack(fill="x")

        hint = ctk.CTkLabel(bottom, text="İpucu: Birden fazla PDF seçip toplu ayırma yapabilirsiniz.",
                            text_color="gray50", font=ctk.CTkFont(size=11))
        hint.pack(pady=(6,0))

    def log_yaz(self, msg):
        self.log.configure(state="normal")
        self.log.insert("end", msg + "\n")
        self.log.see("end")
        self.log.configure(state="disabled")

    def pdf_ekle(self):
        dosyalar = filedialog.askopenfilenames(title="PDF Seç", filetypes=[("PDF Dosyaları", "*.pdf")])
        if not dosyalar:
            return
        for f in dosyalar:
            if f not in self.pdf_dosyalari:
                self.pdf_dosyalari.append(f)
        self.liste_guncelle()

    def liste_temizle(self):
        self.pdf_dosyalari.clear()
        self.liste_guncelle()
        self.log_yaz("Liste temizlendi.")

    def cikti_sec(self):
        klasor = filedialog.askdirectory(title="Çıkış Klasörü Seç")
        if klasor:
            self.cikti_klasoru = klasor
            self.entry_out.delete(0, "end")
            self.entry_out.insert(0, klasor)

    def liste_guncelle(self):
        for w in self.scroll.winfo_children():
            w.destroy()
        n = len(self.pdf_dosyalari)
        self.lbl_sayi.configure(text=f"{n} dosya seçili")
        if n == 0:
            self._bos_mesaj = ctk.CTkLabel(self.scroll, text="Henüz PDF eklenmedi.\n'PDF Ekle' ile başlayın veya birden fazla PDF seçebilirsiniz.",
                                           text_color="gray50", font=ctk.CTkFont(size=12), justify="center")
            self._bos_mesaj.pack(pady=40)
            return
        for idx, yol in enumerate(self.pdf_dosyalari):
            ad = os.path.basename(yol)
            # sayfa sayısı ön izleme
            try:
                reader = PdfReader(yol)
                sayfa_sayisi = len(reader.pages)
                detay = f"{sayfa_sayisi} sayfa"
            except Exception:
                detay = "okunamadı"
            row = ctk.CTkFrame(self.scroll, fg_color="white", corner_radius=8)
            row.pack(fill="x", pady=4, padx=4)
            # renkli ikon
            icon = ctk.CTkLabel(row, text="PDF", width=44, height=32, corner_radius=6,
                                fg_color="#EF4444", text_color="white", font=ctk.CTkFont(size=11, weight="bold"))
            icon.pack(side="left", padx=8, pady=8)
            info = ctk.CTkFrame(row, fg_color="transparent")
            info.pack(side="left", fill="x", expand=True, pady=6)
            ctk.CTkLabel(info, text=ad, font=ctk.CTkFont(size=12, weight="bold"), anchor="w").pack(fill="x")
            ctk.CTkLabel(info, text=f"{detay}  •  {yol}", text_color="gray50", font=ctk.CTkFont(size=10), anchor="w").pack(fill="x")
            ctk.CTkButton(row, text="✕", width=32, height=26, corner_radius=8,
                          fg_color="#F1F1F1", text_color="#666", hover_color="#E5E5E5",
                          font=ctk.CTkFont(size=12, weight="bold"),
                          command=lambda i=idx: self.dosya_sil(i)).pack(side="right", padx=8)

    def dosya_sil(self, idx):
        if 0 <= idx < len(self.pdf_dosyalari):
            self.pdf_dosyalari.pop(idx)
            self.liste_guncelle()

    def ayir_baslat(self):
        if not self.pdf_dosyalari:
            messagebox.showwarning("Uyarı", "Lütfen önce en az bir PDF seçin.")
            return
        cikti = self.entry_out.get().strip()
        if not cikti or not os.path.isdir(cikti):
            try:
                os.makedirs(cikti, exist_ok=True)
            except Exception as e:
                messagebox.showerror("Hata", f"Çıkış klasörü oluşturulamadı:\n{e}")
                return
            if not os.path.isdir(cikti):
                messagebox.showerror("Hata", "Geçerli bir çıkış klasörü seçin.")
                return
        self.cikti_klasoru = cikti
        self.btn_ayir.configure(state="disabled", text="İşleniyor...")
        self.progress.set(0)
        self.lbl_durum.configure(text="İşlem başlatıldı...")
        threading.Thread(target=self._ayir_thread, daemon=True).start()

    def _ayir_thread(self):
        toplam_pdf = len(self.pdf_dosyalari)
        toplam_sayfa = 0
        hata = 0
        for idx, dosya_yolu in enumerate(list(self.pdf_dosyalari)):
            try:
                ad = Path(dosya_yolu).stem
                self.after(0, lambda m=f"İşleniyor: {ad}": self.lbl_durum.configure(text=m))
                self.after(0, lambda m=f"→ {ad} işleniyor...": self.log_yaz(m))

                reader = PdfReader(dosya_yolu)
                if reader.is_encrypted:
                    try:
                        reader.decrypt("")
                    except Exception:
                        self.after(0, lambda a=ad: self.log_yaz(f"✗ {a}: Şifreli PDF, atlandı."))
                        hata += 1
                        continue

                sayfa_sayisi = len(reader.pages)
                if sayfa_sayisi == 0:
                    self.after(0, lambda a=ad: self.log_yaz(f"⚠ {a}: Sayfa bulunamadı."))
                    continue

                # hedef klasör
                if self.var_alt_klasor.get():
                    hedef = Path(self.cikti_klasoru) / f"{ad}_sayfalar"
                    hedef.mkdir(parents=True, exist_ok=True)
                else:
                    hedef = Path(self.cikti_klasoru)

                for i, page in enumerate(reader.pages):
                    writer = PdfWriter()
                    writer.add_page(page)
                    cikti_adi = hedef / f"{ad}_sayfa_{i+1}.pdf"
                    # çakışma varsa üzerine yaz
                    with open(cikti_adi, "wb") as out:
                        writer.write(out)
                    toplam_sayfa += 1

                self.after(0, lambda a=ad, s=sayfa_sayisi, h=str(hedef): self.log_yaz(f"✓ {a}: {s} sayfa → {h}"))

            except Exception as e:
                hata += 1
                self.after(0, lambda a=ad, err=str(e): self.log_yaz(f"✗ {a}: Hata - {err}"))

            prog = (idx + 1) / toplam_pdf
            self.after(0, lambda p=prog: self.progress.set(p))

        def bitir():
            self.btn_ayir.configure(state="normal", text="✂   PDF'leri Ayır")
            self.progress.set(1 if hata == 0 else 0.85)
            if hata == 0:
                self.lbl_durum.configure(text=f"Bitti! {toplam_sayfa} sayfa oluşturuldu.")
                messagebox.showinfo("Başarılı", f"{toplam_pdf} PDF işlendi.\nToplam {toplam_sayfa} sayfa oluşturuldu.\n\nÇıkış: {self.cikti_klasoru}")
            else:
                self.lbl_durum.configure(text=f"Bitti ({hata} hatalı). {toplam_sayfa} sayfa oluşturuldu.")
                messagebox.showwarning("Bitti", f"İşlem tamamlandı.\nBaşarılı: {toplam_sayfa} sayfa\nHatalı PDF: {hata}\n\nÇıkış: {self.cikti_klasoru}")
        self.after(0, bitir)


if __name__ == "__main__":
    app = PdfAyiriciApp()
    app.mainloop()
