import json
import os
import subprocess
import sys
import threading
from pathlib import Path
import customtkinter as ctk
from tkinter import filedialog, messagebox
from pypdf import PdfReader, PdfWriter

try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
except Exception:
    DND_FILES, TkinterDnD = None, None

# ---------------------------------------------------------------------------
# Dil desteği (5 dil) + tema (açık/koyu) + ayarlar
# ---------------------------------------------------------------------------

LANGS = {
    "tr": "Türkçe",
    "en": "English",
    "de": "Deutsch",
    "fr": "Français",
    "es": "Español",
}
LANG_BY_NAME = {v: k for k, v in LANGS.items()}
MODES = ["all", "chunk", "range"]

STRINGS = {
    "tr": {
        "window_title": "PDF Ayırıcı - Sayfa Sayfa Böl",
        "app_title": "PDF Ayırıcı",
        "subtitle": "PDF'lerinizi tek tıkla sayfa sayfa ayırın",
        "add_pdf": "＋  PDF Ekle",
        "clear": "Temizle",
        "files_selected": "{n} dosya seçili",
        "empty_msg": "Henüz PDF eklenmedi.\n'PDF Ekle' ile başlayın ya da dosyaları buraya sürükleyip bırakın.",
        "out_label": "Çıkış Klasörü:",
        "out_placeholder": "Çıkış klasörü seçin",
        "browse": "Gözat",
        "separate": "Her PDF için ayrı klasör oluştur",
        "example": "Örn: dosya.pdf → dosya_sayfalar/ dosya_sayfa_1.pdf, dosya_sayfa_2.pdf ...",
        "mode_label": "Bölme Modu:",
        "mode_all": "Sayfa sayfa",
        "mode_chunk": "Her N sayfada",
        "mode_range": "Sayfa aralığı",
        "chunk_label": "Her dosyada sayfa sayısı (N):",
        "range_placeholder": "örn. 1-5, 8, 10-12",
        "err_invalid_n": "N için 1 veya daha büyük bir tam sayı girin.",
        "err_invalid_range": "Aralık biçimi geçersiz. Örn: 1-5, 8, 10-12",
        "err_no_outdir": "Çıkış klasörü bulunamadı.",
        "ready": "Hazır",
        "split": "✂   PDF'leri Ayır",
        "splitting": "İşleniyor...",
        "hint": "İpucu: Birden fazla PDF seçip toplu ayırma yapabilirsiniz.",
        "dark_mode": "🌙 Koyu",
        "light_mode": "☀ Açık",
        "dlg_select_pdf": "PDF Seç",
        "filetype": "PDF Dosyaları",
        "dlg_select_out": "Çıkış Klasörü Seç",
        "warn_title": "Uyarı",
        "warn_no_pdf": "Lütfen önce en az bir PDF seçin.",
        "err_title": "Hata",
        "err_create_out": "Çıkış klasörü oluşturulamadı:\n{e}",
        "err_invalid_out": "Geçerli bir çıkış klasörü seçin.",
        "started": "İşlem başlatıldı...",
        "processing": "İşleniyor: {name}",
        "log_processing": "→ {name} işleniyor...",
        "log_encrypted": "✗ {name}: Şifreli PDF, atlandı.",
        "log_no_pages": "⚠ {name}: Sayfa bulunamadı.",
        "log_no_valid": "⚠ {name}: Aralıkta geçerli sayfa yok, atlandı.",
        "log_done": "✓ {name}: {pages} sayfa → {dest}",
        "log_error": "✗ {name}: Hata - {err}",
        "log_dnd": "＋ Sürükle-bırak ile {n} dosya eklendi.",
        "list_cleared": "Liste temizlendi.",
        "pages": "{n} sayfa",
        "unreadable": "okunamadı",
        "done_ok": "Bitti! {n} sayfa oluşturuldu.",
        "done_err": "Bitti ({e} hatalı). {n} sayfa oluşturuldu.",
        "success_title": "Başarılı",
        "success_msg": "{pdf} PDF işlendi.\nToplam {pages} sayfa oluşturuldu.\n\nÇıkış: {out}",
        "finished_title": "Bitti",
        "finished_msg": "İşlem tamamlandı.\nBaşarılı: {pages} sayfa\nHatalı PDF: {err}\n\nÇıkış: {out}",
        "fname_page": "sayfa",
        "fname_pages": "sayfalar",
        "fname_part": "bolum",
        "fname_range": "aralik",
    },
    "en": {
        "window_title": "PDF Splitter - Split Page by Page",
        "app_title": "PDF Splitter",
        "subtitle": "Split your PDFs page by page with one click",
        "add_pdf": "＋  Add PDF",
        "clear": "Clear",
        "files_selected": "{n} file(s) selected",
        "empty_msg": "No PDF added yet.\nStart with 'Add PDF' or drag & drop files here.",
        "out_label": "Output Folder:",
        "out_placeholder": "Choose an output folder",
        "browse": "Browse",
        "separate": "Create a separate folder per PDF",
        "example": "E.g.: file.pdf → file_pages/ file_page_1.pdf, file_page_2.pdf ...",
        "mode_label": "Split Mode:",
        "mode_all": "Page by page",
        "mode_chunk": "Every N pages",
        "mode_range": "Page range",
        "chunk_label": "Pages per file (N):",
        "range_placeholder": "e.g. 1-5, 8, 10-12",
        "err_invalid_n": "Enter an integer of 1 or greater for N.",
        "err_invalid_range": "Invalid range format. E.g.: 1-5, 8, 10-12",
        "err_no_outdir": "Output folder not found.",
        "ready": "Ready",
        "split": "✂   Split PDFs",
        "splitting": "Processing...",
        "hint": "Tip: Select multiple PDFs for batch splitting.",
        "dark_mode": "🌙 Dark",
        "light_mode": "☀ Light",
        "dlg_select_pdf": "Select PDF",
        "filetype": "PDF Files",
        "dlg_select_out": "Select Output Folder",
        "warn_title": "Warning",
        "warn_no_pdf": "Please select at least one PDF first.",
        "err_title": "Error",
        "err_create_out": "Could not create output folder:\n{e}",
        "err_invalid_out": "Please choose a valid output folder.",
        "started": "Processing started...",
        "processing": "Processing: {name}",
        "log_processing": "→ Processing {name}...",
        "log_encrypted": "✗ {name}: Encrypted PDF, skipped.",
        "log_no_pages": "⚠ {name}: No pages found.",
        "log_no_valid": "⚠ {name}: No valid pages in range, skipped.",
        "log_done": "✓ {name}: {pages} pages → {dest}",
        "log_error": "✗ {name}: Error - {err}",
        "log_dnd": "＋ {n} file(s) added via drag & drop.",
        "list_cleared": "List cleared.",
        "pages": "{n} pages",
        "unreadable": "unreadable",
        "done_ok": "Done! {n} pages created.",
        "done_err": "Done ({e} failed). {n} pages created.",
        "success_title": "Success",
        "success_msg": "{pdf} PDF(s) processed.\n{pages} pages created in total.\n\nOutput: {out}",
        "finished_title": "Finished",
        "finished_msg": "Process finished.\nSuccess: {pages} pages\nFailed PDFs: {err}\n\nOutput: {out}",
        "fname_page": "page",
        "fname_pages": "pages",
        "fname_part": "part",
        "fname_range": "range",
    },
    "de": {
        "window_title": "PDF Trenner - Seite für Seite teilen",
        "app_title": "PDF Trenner",
        "subtitle": "Teilen Sie Ihre PDFs mit einem Klick Seite für Seite",
        "add_pdf": "＋  PDF hinzufügen",
        "clear": "Leeren",
        "files_selected": "{n} Datei(en) ausgewählt",
        "empty_msg": "Noch kein PDF hinzugefügt.\nBeginnen Sie mit 'PDF hinzufügen' oder ziehen Sie Dateien hierher.",
        "out_label": "Ausgabeordner:",
        "out_placeholder": "Ausgabeordner wählen",
        "browse": "Durchsuchen",
        "separate": "Pro PDF einen eigenen Ordner erstellen",
        "example": "Z.B.: datei.pdf → datei_seiten/ datei_seite_1.pdf, datei_seite_2.pdf ...",
        "mode_label": "Teilungsmodus:",
        "mode_all": "Seite für Seite",
        "mode_chunk": "Alle N Seiten",
        "mode_range": "Seitenbereich",
        "chunk_label": "Seiten pro Datei (N):",
        "range_placeholder": "z.B. 1-5, 8, 10-12",
        "err_invalid_n": "Geben Sie für N eine ganze Zahl ab 1 ein.",
        "err_invalid_range": "Ungültiges Bereichsformat. Z.B.: 1-5, 8, 10-12",
        "err_no_outdir": "Ausgabeordner nicht gefunden.",
        "ready": "Bereit",
        "split": "✂   PDFs teilen",
        "splitting": "Wird verarbeitet...",
        "hint": "Tipp: Wählen Sie mehrere PDFs für die Stapelverarbeitung.",
        "dark_mode": "🌙 Dunkel",
        "light_mode": "☀ Hell",
        "dlg_select_pdf": "PDF auswählen",
        "filetype": "PDF-Dateien",
        "dlg_select_out": "Ausgabeordner auswählen",
        "warn_title": "Warnung",
        "warn_no_pdf": "Bitte wählen Sie zuerst mindestens ein PDF aus.",
        "err_title": "Fehler",
        "err_create_out": "Ausgabeordner konnte nicht erstellt werden:\n{e}",
        "err_invalid_out": "Bitte wählen Sie einen gültigen Ausgabeordner.",
        "started": "Verarbeitung gestartet...",
        "processing": "Verarbeite: {name}",
        "log_processing": "→ {name} wird verarbeitet...",
        "log_encrypted": "✗ {name}: Verschlüsseltes PDF, übersprungen.",
        "log_no_pages": "⚠ {name}: Keine Seiten gefunden.",
        "log_no_valid": "⚠ {name}: Keine gültigen Seiten im Bereich, übersprungen.",
        "log_done": "✓ {name}: {pages} Seiten → {dest}",
        "log_error": "✗ {name}: Fehler - {err}",
        "log_dnd": "＋ {n} Datei(en) per Drag & Drop hinzugefügt.",
        "list_cleared": "Liste geleert.",
        "pages": "{n} Seiten",
        "unreadable": "unlesbar",
        "done_ok": "Fertig! {n} Seiten erstellt.",
        "done_err": "Fertig ({e} fehlerhaft). {n} Seiten erstellt.",
        "success_title": "Erfolgreich",
        "success_msg": "{pdf} PDF(s) verarbeitet.\nInsgesamt {pages} Seiten erstellt.\n\nAusgabe: {out}",
        "finished_title": "Fertig",
        "finished_msg": "Vorgang abgeschlossen.\nErfolgreich: {pages} Seiten\nFehlerhafte PDFs: {err}\n\nAusgabe: {out}",
        "fname_page": "seite",
        "fname_pages": "seiten",
        "fname_part": "teil",
        "fname_range": "bereich",
    },
    "fr": {
        "window_title": "Diviseur PDF - Page par page",
        "app_title": "Diviseur PDF",
        "subtitle": "Divisez vos PDF page par page en un clic",
        "add_pdf": "＋  Ajouter un PDF",
        "clear": "Effacer",
        "files_selected": "{n} fichier(s) sélectionné(s)",
        "empty_msg": "Aucun PDF ajouté.\nCommencez avec 'Ajouter un PDF' ou glissez-déposez des fichiers ici.",
        "out_label": "Dossier de sortie :",
        "out_placeholder": "Choisir un dossier de sortie",
        "browse": "Parcourir",
        "separate": "Créer un dossier séparé par PDF",
        "example": "Ex. : fichier.pdf → fichier_pages/ fichier_page_1.pdf, fichier_page_2.pdf ...",
        "mode_label": "Mode de division :",
        "mode_all": "Page par page",
        "mode_chunk": "Toutes les N pages",
        "mode_range": "Plage de pages",
        "chunk_label": "Pages par fichier (N) :",
        "range_placeholder": "ex. 1-5, 8, 10-12",
        "err_invalid_n": "Saisissez un entier supérieur ou égal à 1 pour N.",
        "err_invalid_range": "Format de plage invalide. Ex. : 1-5, 8, 10-12",
        "err_no_outdir": "Dossier de sortie introuvable.",
        "ready": "Prêt",
        "split": "✂   Diviser les PDF",
        "splitting": "Traitement...",
        "hint": "Astuce : sélectionnez plusieurs PDF pour un traitement par lot.",
        "dark_mode": "🌙 Sombre",
        "light_mode": "☀ Clair",
        "dlg_select_pdf": "Sélectionner un PDF",
        "filetype": "Fichiers PDF",
        "dlg_select_out": "Choisir le dossier de sortie",
        "warn_title": "Avertissement",
        "warn_no_pdf": "Veuillez d'abord sélectionner au moins un PDF.",
        "err_title": "Erreur",
        "err_create_out": "Impossible de créer le dossier de sortie :\n{e}",
        "err_invalid_out": "Veuillez choisir un dossier de sortie valide.",
        "started": "Traitement démarré...",
        "processing": "Traitement : {name}",
        "log_processing": "→ Traitement de {name}...",
        "log_encrypted": "✗ {name} : PDF chiffré, ignoré.",
        "log_no_pages": "⚠ {name} : Aucune page trouvée.",
        "log_no_valid": "⚠ {name} : Aucune page valide dans la plage, ignoré.",
        "log_done": "✓ {name} : {pages} pages → {dest}",
        "log_error": "✗ {name} : Erreur - {err}",
        "log_dnd": "＋ {n} fichier(s) ajouté(s) par glisser-déposer.",
        "list_cleared": "Liste effacée.",
        "pages": "{n} pages",
        "unreadable": "illisible",
        "done_ok": "Terminé ! {n} pages créées.",
        "done_err": "Terminé ({e} en échec). {n} pages créées.",
        "success_title": "Succès",
        "success_msg": "{pdf} PDF traité(s).\n{pages} pages créées au total.\n\nSortie : {out}",
        "finished_title": "Terminé",
        "finished_msg": "Traitement terminé.\nRéussite : {pages} pages\nPDF en échec : {err}\n\nSortie : {out}",
        "fname_page": "page",
        "fname_pages": "pages",
        "fname_part": "partie",
        "fname_range": "plage",
    },
    "es": {
        "window_title": "Divisor de PDF - Página por página",
        "app_title": "Divisor de PDF",
        "subtitle": "Divide tus PDF página por página con un clic",
        "add_pdf": "＋  Añadir PDF",
        "clear": "Limpiar",
        "files_selected": "{n} archivo(s) seleccionado(s)",
        "empty_msg": "Aún no hay PDF.\nEmpieza con 'Añadir PDF' o arrastra y suelta archivos aquí.",
        "out_label": "Carpeta de salida:",
        "out_placeholder": "Elige una carpeta de salida",
        "browse": "Examinar",
        "separate": "Crear una carpeta separada por PDF",
        "example": "Ej.: archivo.pdf → archivo_paginas/ archivo_pagina_1.pdf, archivo_pagina_2.pdf ...",
        "mode_label": "Modo de división:",
        "mode_all": "Página por página",
        "mode_chunk": "Cada N páginas",
        "mode_range": "Rango de páginas",
        "chunk_label": "Páginas por archivo (N):",
        "range_placeholder": "ej. 1-5, 8, 10-12",
        "err_invalid_n": "Introduce un entero igual o mayor que 1 para N.",
        "err_invalid_range": "Formato de rango no válido. Ej.: 1-5, 8, 10-12",
        "err_no_outdir": "Carpeta de salida no encontrada.",
        "ready": "Listo",
        "split": "✂   Dividir PDF",
        "splitting": "Procesando...",
        "hint": "Consejo: selecciona varios PDF para dividir en lote.",
        "dark_mode": "🌙 Oscuro",
        "light_mode": "☀ Claro",
        "dlg_select_pdf": "Seleccionar PDF",
        "filetype": "Archivos PDF",
        "dlg_select_out": "Seleccionar carpeta de salida",
        "warn_title": "Advertencia",
        "warn_no_pdf": "Selecciona al menos un PDF primero.",
        "err_title": "Error",
        "err_create_out": "No se pudo crear la carpeta de salida:\n{e}",
        "err_invalid_out": "Elige una carpeta de salida válida.",
        "started": "Procesamiento iniciado...",
        "processing": "Procesando: {name}",
        "log_processing": "→ Procesando {name}...",
        "log_encrypted": "✗ {name}: PDF cifrado, omitido.",
        "log_no_pages": "⚠ {name}: No se encontraron páginas.",
        "log_no_valid": "⚠ {name}: Sin páginas válidas en el rango, omitido.",
        "log_done": "✓ {name}: {pages} páginas → {dest}",
        "log_error": "✗ {name}: Error - {err}",
        "log_dnd": "＋ {n} archivo(s) añadido(s) por arrastrar y soltar.",
        "list_cleared": "Lista limpiada.",
        "pages": "{n} páginas",
        "unreadable": "ilegible",
        "done_ok": "¡Listo! {n} páginas creadas.",
        "done_err": "Listo ({e} con errores). {n} páginas creadas.",
        "success_title": "Éxito",
        "success_msg": "{pdf} PDF procesado(s).\n{pages} páginas creadas en total.\n\nSalida: {out}",
        "finished_title": "Terminado",
        "finished_msg": "Proceso terminado.\nÉxito: {pages} páginas\nPDF con errores: {err}\n\nSalida: {out}",
        "fname_page": "pagina",
        "fname_pages": "paginas",
        "fname_part": "parte",
        "fname_range": "rango",
    },
}

SETTINGS_PATH = Path.home() / ".pdf_ayirici_settings.json"


def load_settings():
    lang, theme, outdir = "tr", "light", None
    try:
        data = json.loads(SETTINGS_PATH.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            lang = data.get("lang", lang)
            theme = data.get("theme", theme)
            outdir = data.get("outdir")
    except Exception:
        pass
    if lang not in STRINGS:
        lang = "tr"
    if theme not in ("light", "dark"):
        theme = "light"
    if outdir and not os.path.isdir(outdir):
        outdir = None
    return lang, theme, outdir


def save_settings(lang, theme, outdir=None):
    try:
        SETTINGS_PATH.write_text(
            json.dumps({"lang": lang, "theme": theme, "outdir": outdir}, ensure_ascii=False),
            encoding="utf-8",
        )
    except Exception:
        pass


def parse_range(text):
    """'1-5, 8, 10-12' -> [(1,5),(8,8),(10,12)] (1-indexed, dahil). Hatalıysa ValueError."""
    groups = []
    for part in str(text).split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            bits = part.split("-", 1)
            a, b = int(bits[0].strip()), int(bits[1].strip())
            if a < 1 or b < 1 or a > b:
                raise ValueError(part)
        else:
            a = b = int(part)
            if a < 1:
                raise ValueError(part)
        groups.append((a, b))
    if not groups:
        raise ValueError(text)
    return groups


THEME_COLORS = {
    "light": {
        "scroll_bg": "#F5F5F7",
        "row_bg": "white",
        "log_bg": "#FAFAFA",
        "log_text": "#333",
        "clear_fg": "#E8E8E8",
        "clear_text": "#333",
        "clear_hover": "#D8D8D8",
        "del_fg": "#F1F1F1",
        "del_text": "#666",
        "del_hover": "#E5E5E5",
    },
    "dark": {
        "scroll_bg": "#242424",
        "row_bg": "#2E2E2E",
        "log_bg": "#242424",
        "log_text": "#E8E8E8",
        "clear_fg": "#3A3A3A",
        "clear_text": "#EDEDED",
        "clear_hover": "#4A4A4A",
        "del_fg": "#3A3A3A",
        "del_text": "#CCCCCC",
        "del_hover": "#4A4A4A",
    },
}


class PdfAyiriciApp(ctk.CTk, TkinterDnD.DnDWrapper if TkinterDnD else object):
    def __init__(self):
        self.lang, self.theme, saved_out = load_settings()
        ctk.set_appearance_mode(self.theme)
        ctk.set_default_color_theme("blue")
        super().__init__()
        self.geometry("720x760")
        self.minsize(680, 680)
        self.pdf_dosyalari = []
        desktop = str(Path.home() / "Desktop")
        self.cikti_klasoru = saved_out if saved_out else desktop
        self.mode = "all"
        self._n = 10
        self._range_groups = None
        self._islem_sirada = False

        self._build_ui()
        self.apply_language()
        self.apply_theme()
        self._init_dnd()

    def t(self, key, **kwargs):
        s = STRINGS[self.lang].get(key, STRINGS["tr"].get(key, key))
        try:
            return s.format(**kwargs)
        except Exception:
            return s

    def _current_outdir(self):
        return self.entry_out.get().strip() or self.cikti_klasoru

    # ------------------------------------------------------------------ UI --
    def _build_ui(self):
        # Header (sol: başlık, sağ: dil + tema)
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(side="top", fill="x", padx=24, pady=(16, 8))

        left = ctk.CTkFrame(header, fg_color="transparent")
        left.pack(side="left", fill="x", expand=True)
        self.lbl_title = ctk.CTkLabel(left, text="", font=ctk.CTkFont(size=24, weight="bold"))
        self.lbl_title.pack(anchor="w")
        self.lbl_subtitle = ctk.CTkLabel(left, text="", text_color="gray50", font=ctk.CTkFont(size=13))
        self.lbl_subtitle.pack(anchor="w", pady=(2, 0))

        right = ctk.CTkFrame(header, fg_color="transparent")
        right.pack(side="right", anchor="n")
        self.var_dark = ctk.BooleanVar(value=(self.theme == "dark"))
        self.switch_theme = ctk.CTkSwitch(
            right, text="", font=ctk.CTkFont(size=12),
            variable=self.var_dark, command=self.toggle_theme,
        )
        self.switch_theme.pack(anchor="e", pady=(2, 6))
        self.menu_lang = ctk.CTkOptionMenu(
            right, width=130, height=30, corner_radius=8,
            values=list(LANGS.values()), command=self.change_language,
        )
        self.menu_lang.pack(anchor="e")
        self.menu_lang.set(LANGS[self.lang])

        # Alt buton - Ayır (ÖNCE pack'lenir ki her zaman görünür kalsın,
        # pencere küçük / ekran ölçeği büyük olsa bile alttan taşmasın)
        bottom = ctk.CTkFrame(self, fg_color="transparent")
        bottom.pack(side="bottom", fill="x", padx=20, pady=(8, 14))
        self.btn_ayir = ctk.CTkButton(bottom, text="", height=46, corner_radius=12,
                                      font=ctk.CTkFont(size=15, weight="bold"),
                                      fg_color="#2563EB", hover_color="#1D4ED8",
                                      command=self.ayir_baslat)
        self.btn_ayir.pack(fill="x")

        self.lbl_hint = ctk.CTkLabel(bottom, text="",
                                     text_color="gray50", font=ctk.CTkFont(size=11))
        self.lbl_hint.pack(pady=(6, 0))

        # Card - Dosya seçimi (kalan alanı doldurur, küçülürse iç liste küçülür)
        card = ctk.CTkFrame(self, corner_radius=16)
        card.pack(side="top", fill="both", expand=True, padx=20, pady=(4, 4))

        # Üst butonlar
        top_btn_frame = ctk.CTkFrame(card, fg_color="transparent")
        top_btn_frame.pack(fill="x", padx=18, pady=(18, 10))

        self.btn_ekle = ctk.CTkButton(top_btn_frame, text="", width=140, height=38, corner_radius=10,
                                      font=ctk.CTkFont(size=13, weight="bold"),
                                      command=self.pdf_ekle)
        self.btn_ekle.pack(side="left", padx=(0, 10))

        self.btn_temizle = ctk.CTkButton(top_btn_frame, text="", width=90, height=38, corner_radius=10,
                                         font=ctk.CTkFont(size=13),
                                         command=self.liste_temizle)
        self.btn_temizle.pack(side="left")

        self.lbl_sayi = ctk.CTkLabel(top_btn_frame, text="", text_color="gray50", font=ctk.CTkFont(size=12))
        self.lbl_sayi.pack(side="right", padx=8)

        # Dosya listesi (esnek yükseklik: pencere küçülünce önce bu daralır)
        self.scroll = ctk.CTkScrollableFrame(card, height=140, corner_radius=10)
        self.scroll.pack(fill="both", expand=True, padx=18, pady=6)

        # Çıktı klasörü
        out_frame = ctk.CTkFrame(card, fg_color="transparent")
        out_frame.pack(fill="x", padx=18, pady=(14, 6))
        self.lbl_out = ctk.CTkLabel(out_frame, text="", font=ctk.CTkFont(size=12, weight="bold"))
        self.lbl_out.pack(anchor="w")
        row = ctk.CTkFrame(out_frame, fg_color="transparent")
        row.pack(fill="x", pady=(6, 0))
        self.entry_out = ctk.CTkEntry(row, placeholder_text="", height=36, corner_radius=10)
        self.entry_out.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.entry_out.insert(0, self.cikti_klasoru)
        self.btn_folder = ctk.CTkButton(row, text="📂", width=44, height=36, corner_radius=10,
                                        font=ctk.CTkFont(size=16),
                                        command=self.klasor_ac)
        self.btn_folder.pack(side="left", padx=(0, 8))
        self.btn_gozat = ctk.CTkButton(row, text="", width=90, height=36, corner_radius=10,
                                       fg_color="#2B2B2B", hover_color="#1A1A1A",
                                       command=self.cikti_sec)
        self.btn_gozat.pack(side="right")

        # Seçenekler
        opt_frame = ctk.CTkFrame(card, fg_color="transparent")
        opt_frame.pack(fill="x", padx=18, pady=(10, 6))
        self.var_alt_klasor = ctk.BooleanVar(value=True)
        self.chk_alt = ctk.CTkCheckBox(opt_frame, text="", variable=self.var_alt_klasor,
                                       font=ctk.CTkFont(size=12))
        self.chk_alt.pack(anchor="w")
        self.lbl_ornek = ctk.CTkLabel(opt_frame, text="",
                                      text_color="gray50", font=ctk.CTkFont(size=11))
        self.lbl_ornek.pack(anchor="w", pady=(2, 0))

        # Bölme modu
        mode_frame = ctk.CTkFrame(card, fg_color="transparent")
        mode_frame.pack(fill="x", padx=18, pady=(4, 2))
        self.lbl_mode = ctk.CTkLabel(mode_frame, text="", font=ctk.CTkFont(size=12, weight="bold"))
        self.lbl_mode.pack(anchor="w")
        self.seg = ctk.CTkSegmentedButton(mode_frame, command=self.on_mode_change)
        self.seg.pack(fill="x", pady=(6, 0))

        self.dynamic = ctk.CTkFrame(card, fg_color="transparent")
        self.dynamic.pack(fill="x", padx=18, pady=(2, 4))
        self.chunk_row = ctk.CTkFrame(self.dynamic, fg_color="transparent")
        self.lbl_chunk = ctk.CTkLabel(self.chunk_row, text="", font=ctk.CTkFont(size=12))
        self.lbl_chunk.pack(side="left", padx=(0, 8))
        self.entry_n = ctk.CTkEntry(self.chunk_row, width=80, height=32, corner_radius=8)
        self.entry_n.pack(side="left")
        self.entry_n.insert(0, "10")
        self.range_row = ctk.CTkFrame(self.dynamic, fg_color="transparent")
        self.entry_range = ctk.CTkEntry(self.range_row, placeholder_text="", height=32, corner_radius=8)
        self.entry_range.pack(fill="x")

        # Progress + Log
        self.progress = ctk.CTkProgressBar(card, height=8, corner_radius=4)
        self.progress.pack(fill="x", padx=18, pady=(8, 6))
        self.progress.set(0)

        self.lbl_durum = ctk.CTkLabel(card, text="", text_color="gray50", font=ctk.CTkFont(size=11))
        self.lbl_durum.pack(anchor="w", padx=18)

        self.log = ctk.CTkTextbox(card, height=60, corner_radius=10,
                                  font=ctk.CTkFont(size=11))
        self.log.pack(fill="x", padx=18, pady=(6, 12))
        self.log.configure(state="disabled")

    def _init_dnd(self):
        """Sürükle-bırak desteği (yoksa sessizce devre dışı)."""
        self._dnd_ok = False
        if TkinterDnD is None:
            return
        try:
            self.TkdndVersion = TkinterDnD._require(self)
            self.drop_target_register(DND_FILES)
            self.dnd_bind("<<Drop>>", self.on_drop)
            self._dnd_ok = True
        except Exception:
            pass

    # ---------------------------------------------------------- dil + tema --
    def change_language(self, display_name):
        code = LANG_BY_NAME.get(display_name, "tr")
        self.lang = code
        save_settings(self.lang, self.theme, self._current_outdir())
        self.apply_language()

    def apply_language(self):
        self.title(self.t("window_title"))
        self.lbl_title.configure(text=self.t("app_title"))
        self.lbl_subtitle.configure(text=self.t("subtitle"))
        self.btn_ekle.configure(text=self.t("add_pdf"))
        self.btn_temizle.configure(text=self.t("clear"))
        self.lbl_out.configure(text=self.t("out_label"))
        self.entry_out.configure(placeholder_text=self.t("out_placeholder"))
        self.btn_gozat.configure(text=self.t("browse"))
        self.chk_alt.configure(text=self.t("separate"))
        self.lbl_ornek.configure(text=self.t("example"))
        self.lbl_hint.configure(text=self.t("hint"))
        self.lbl_mode.configure(text=self.t("mode_label"))
        vals = [self.t("mode_all"), self.t("mode_chunk"), self.t("mode_range")]
        self.seg.configure(values=vals)
        self.seg.set(vals[MODES.index(self.mode)])
        self.lbl_chunk.configure(text=self.t("chunk_label"))
        self.entry_range.configure(placeholder_text=self.t("range_placeholder"))
        self.switch_theme.configure(
            text=self.t("dark_mode") if self.theme == "dark" else self.t("light_mode")
        )
        if not self._islem_sirada:
            self.btn_ayir.configure(text=self.t("split"))
            self.lbl_durum.configure(text=self.t("ready"))
        self.menu_lang.set(LANGS[self.lang])
        self._update_mode_rows()
        self.liste_guncelle()

    def on_mode_change(self, value):
        vals = [self.t("mode_all"), self.t("mode_chunk"), self.t("mode_range")]
        try:
            self.mode = MODES[vals.index(value)]
        except ValueError:
            self.mode = "all"
        self._update_mode_rows()

    def _update_mode_rows(self):
        if self.mode == "chunk":
            self.range_row.pack_forget()
            self.chunk_row.pack(fill="x", pady=(4, 0))
        elif self.mode == "range":
            self.chunk_row.pack_forget()
            self.range_row.pack(fill="x", pady=(4, 0))
        else:
            self.chunk_row.pack_forget()
            self.range_row.pack_forget()

    def toggle_theme(self):
        self.theme = "dark" if self.var_dark.get() else "light"
        save_settings(self.lang, self.theme, self._current_outdir())
        self.apply_theme()

    def apply_theme(self):
        ctk.set_appearance_mode(self.theme)
        c = THEME_COLORS[self.theme]
        self.var_dark.set(self.theme == "dark")
        self.switch_theme.configure(
            text=self.t("dark_mode") if self.theme == "dark" else self.t("light_mode")
        )
        self.scroll.configure(fg_color=c["scroll_bg"])
        self.log.configure(fg_color=c["log_bg"], text_color=c["log_text"])
        self.btn_temizle.configure(
            fg_color=c["clear_fg"], text_color=c["clear_text"], hover_color=c["clear_hover"]
        )
        self.btn_folder.configure(
            fg_color=c["clear_fg"], text_color=c["clear_text"], hover_color=c["clear_hover"]
        )
        self.liste_guncelle()

    # ---------------------------------------------------------------- mantık --
    def log_yaz(self, msg):
        self.log.configure(state="normal")
        self.log.insert("end", msg + "\n")
        self.log.see("end")
        self.log.configure(state="disabled")

    def pdf_ekle(self):
        dosyalar = filedialog.askopenfilenames(
            title=self.t("dlg_select_pdf"),
            filetypes=[(self.t("filetype"), "*.pdf")],
        )
        if not dosyalar:
            return
        for f in dosyalar:
            if f not in self.pdf_dosyalari:
                self.pdf_dosyalari.append(f)
        self.liste_guncelle()

    def on_drop(self, event):
        try:
            paths = self.tk.splitlist(event.data)
        except Exception:
            return
        eklenen = 0
        for p in paths:
            if isinstance(p, bytes):
                try:
                    p = p.decode("utf-8")
                except Exception:
                    continue
            if os.path.isfile(p) and p.lower().endswith(".pdf") and p not in self.pdf_dosyalari:
                self.pdf_dosyalari.append(p)
                eklenen += 1
        if eklenen:
            self.liste_guncelle()
            self.log_yaz(self.t("log_dnd", n=eklenen))

    def liste_temizle(self):
        self.pdf_dosyalari.clear()
        self.liste_guncelle()
        self.log_yaz(self.t("list_cleared"))

    def cikti_sec(self):
        klasor = filedialog.askdirectory(title=self.t("dlg_select_out"))
        if klasor:
            self.cikti_klasoru = klasor
            self.entry_out.delete(0, "end")
            self.entry_out.insert(0, klasor)
            save_settings(self.lang, self.theme, klasor)

    def klasor_ac(self):
        yol = self._current_outdir()
        if not os.path.isdir(yol):
            messagebox.showwarning(self.t("warn_title"), self.t("err_no_outdir"))
            return
        try:
            if os.name == "nt":
                os.startfile(yol)
            elif sys.platform == "darwin":
                subprocess.run(["open", yol])
            else:
                subprocess.run(["xdg-open", yol])
        except Exception as e:
            messagebox.showerror(self.t("err_title"), str(e))

    def liste_guncelle(self):
        c = THEME_COLORS[self.theme]
        for w in self.scroll.winfo_children():
            w.destroy()
        n = len(self.pdf_dosyalari)
        self.lbl_sayi.configure(text=self.t("files_selected", n=n))
        if n == 0:
            self._bos_mesaj = ctk.CTkLabel(self.scroll, text=self.t("empty_msg"),
                                           text_color="gray50", font=ctk.CTkFont(size=12),
                                           justify="center")
            self._bos_mesaj.pack(pady=40)
            return
        for idx, yol in enumerate(self.pdf_dosyalari):
            ad = os.path.basename(yol)
            # sayfa sayısı ön izleme
            try:
                reader = PdfReader(yol)
                sayfa_sayisi = len(reader.pages)
                detay = self.t("pages", n=sayfa_sayisi)
            except Exception:
                detay = self.t("unreadable")
            row = ctk.CTkFrame(self.scroll, fg_color=c["row_bg"], corner_radius=8)
            row.pack(fill="x", pady=4, padx=4)
            # renkli ikon
            icon = ctk.CTkLabel(row, text="PDF", width=44, height=32, corner_radius=6,
                                fg_color="#EF4444", text_color="white",
                                font=ctk.CTkFont(size=11, weight="bold"))
            icon.pack(side="left", padx=8, pady=8)
            info = ctk.CTkFrame(row, fg_color="transparent")
            info.pack(side="left", fill="x", expand=True, pady=6)
            ctk.CTkLabel(info, text=ad, font=ctk.CTkFont(size=12, weight="bold"), anchor="w").pack(fill="x")
            ctk.CTkLabel(info, text=f"{detay}  •  {yol}", text_color="gray50",
                         font=ctk.CTkFont(size=10), anchor="w").pack(fill="x")
            ctk.CTkButton(row, text="✕", width=32, height=26, corner_radius=8,
                          fg_color=c["del_fg"], text_color=c["del_text"], hover_color=c["del_hover"],
                          font=ctk.CTkFont(size=12, weight="bold"),
                          command=lambda i=idx: self.dosya_sil(i)).pack(side="right", padx=8)

    def dosya_sil(self, idx):
        if 0 <= idx < len(self.pdf_dosyalari):
            self.pdf_dosyalari.pop(idx)
            self.liste_guncelle()

    def ayir_baslat(self):
        if not self.pdf_dosyalari:
            messagebox.showwarning(self.t("warn_title"), self.t("warn_no_pdf"))
            return
        # mod girdilerini önden doğrula
        if self.mode == "chunk":
            try:
                n = int(self.entry_n.get().strip())
                if n < 1:
                    raise ValueError
            except (ValueError, AttributeError):
                messagebox.showerror(self.t("err_title"), self.t("err_invalid_n"))
                return
            self._n = n
        elif self.mode == "range":
            try:
                self._range_groups = parse_range(self.entry_range.get())
            except ValueError:
                messagebox.showerror(self.t("err_title"), self.t("err_invalid_range"))
                return
        cikti = self.entry_out.get().strip()
        if not cikti or not os.path.isdir(cikti):
            try:
                os.makedirs(cikti, exist_ok=True)
            except Exception as e:
                messagebox.showerror(self.t("err_title"), self.t("err_create_out", e=e))
                return
            if not os.path.isdir(cikti):
                messagebox.showerror(self.t("err_title"), self.t("err_invalid_out"))
                return
        self.cikti_klasoru = cikti
        save_settings(self.lang, self.theme, cikti)
        self._islem_sirada = True
        self.btn_ayir.configure(state="disabled", text=self.t("splitting"))
        self.progress.set(0)
        self.lbl_durum.configure(text=self.t("started"))
        threading.Thread(target=self._ayir_thread, daemon=True).start()

    def _plan_jobs(self, mode, n, groups, pagecount, stem):
        """Çıktı işlerini planla: [(dosya_önadı, [sayfa_indexleri])]."""
        if mode == "chunk":
            jobs = []
            for k in range(0, pagecount, n):
                part = list(range(k, min(k + n, pagecount)))
                jobs.append((f"{stem}_{self.t('fname_part')}_{k // n + 1}", part))
            return jobs
        if mode == "range":
            jobs = []
            for (a, b) in groups:
                a = max(1, a)
                b = min(pagecount, b)
                if a > b:
                    continue
                jobs.append((f"{stem}_{self.t('fname_range')}_{a}-{b}", list(range(a - 1, b))))
            return jobs
        return [(f"{stem}_{self.t('fname_page')}_{i + 1}", [i]) for i in range(pagecount)]

    def _ayir_thread(self):
        toplam_pdf = len(self.pdf_dosyalari)
        toplam_sayfa = 0
        hata = 0
        mode, n, groups = self.mode, self._n, self._range_groups
        for idx, dosya_yolu in enumerate(list(self.pdf_dosyalari)):
            try:
                ad = Path(dosya_yolu).stem
                self.after(0, lambda m=self.t("processing", name=ad): self.lbl_durum.configure(text=m))
                self.after(0, lambda m=self.t("log_processing", name=ad): self.log_yaz(m))

                reader = PdfReader(dosya_yolu)
                if reader.is_encrypted:
                    try:
                        reader.decrypt("")
                    except Exception:
                        self.after(0, lambda a=ad: self.log_yaz(self.t("log_encrypted", name=a)))
                        hata += 1
                        continue

                sayfa_sayisi = len(reader.pages)
                if sayfa_sayisi == 0:
                    self.after(0, lambda a=ad: self.log_yaz(self.t("log_no_pages", name=a)))
                    continue

                jobs = self._plan_jobs(mode, n, groups, sayfa_sayisi, ad)
                if not jobs:
                    self.after(0, lambda a=ad: self.log_yaz(self.t("log_no_valid", name=a)))
                    continue

                # hedef klasör
                if self.var_alt_klasor.get():
                    hedef = Path(self.cikti_klasoru) / f"{ad}_{self.t('fname_pages')}"
                    hedef.mkdir(parents=True, exist_ok=True)
                else:
                    hedef = Path(self.cikti_klasoru)

                uretilen = 0
                for on_ad, sayfalar in jobs:
                    writer = PdfWriter()
                    for pi in sayfalar:
                        writer.add_page(reader.pages[pi])
                    with open(hedef / f"{on_ad}.pdf", "wb") as out:
                        writer.write(out)
                    uretilen += len(sayfalar)

                toplam_sayfa += uretilen
                self.after(0, lambda a=ad, s=uretilen, h=str(hedef):
                           self.log_yaz(self.t("log_done", name=a, pages=s, dest=h)))

            except Exception as e:
                hata += 1
                self.after(0, lambda a=ad, err=str(e):
                           self.log_yaz(self.t("log_error", name=a, err=err)))

            prog = (idx + 1) / toplam_pdf
            self.after(0, lambda p=prog: self.progress.set(p))

        def bitir():
            self._islem_sirada = False
            self.btn_ayir.configure(state="normal", text=self.t("split"))
            self.progress.set(1 if hata == 0 else 0.85)
            if hata == 0:
                self.lbl_durum.configure(text=self.t("done_ok", n=toplam_sayfa))
                messagebox.showinfo(
                    self.t("success_title"),
                    self.t("success_msg", pdf=toplam_pdf, pages=toplam_sayfa, out=self.cikti_klasoru),
                )
            else:
                self.lbl_durum.configure(text=self.t("done_err", e=hata, n=toplam_sayfa))
                messagebox.showwarning(
                    self.t("finished_title"),
                    self.t("finished_msg", pages=toplam_sayfa, err=hata, out=self.cikti_klasoru),
                )
        self.after(0, bitir)


if __name__ == "__main__":
    app = PdfAyiriciApp()
    app.mainloop()
