import os
import threading
import urllib.request
import urllib.error
import urllib.parse
import zipfile

import customtkinter as ctk

try:
    import rarfile
except ImportError:
    rarfile = None

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")


class InstallerApp:
    def __init__(self, root, download_url=""):
        self.root = root
        self.download_url = download_url.strip()
        self.root.title("Instalator Aplikacji")
        self.root.geometry("760x520")
        self.root.resizable(False, False)

        self.title_font = ctk.CTkFont(size=28, weight="bold")
        self.text_font = ctk.CTkFont(size=16)
        self.button_font = ctk.CTkFont(size=15, weight="bold")

        self.current_step = 0
        self.current_page = None
        self.install_progress = 0.0
        self.install_job = None

        self.steps = [
            self.show_welcome,
            self.show_license,
            self.show_installing,
            self.show_finish,
        ]

        # Main layout
        self.main_frame = ctk.CTkFrame(self.root, corner_radius=0)
        self.main_frame.pack(fill="both", expand=True)

        self.sidebar = ctk.CTkFrame(self.main_frame, width=180, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        self.content_frame = ctk.CTkFrame(self.main_frame, corner_radius=0)
        self.content_frame.pack(side="right", fill="both", expand=True)

        # Sidebar step labels (fixed positions so the indicator never drifts)
        self.step_labels = []
        self.sidebar_targets = []
        self.base_y = 42
        self.spacing = 52
        self.indicator_x = 8
        self.indicator_w = 4
        self.indicator_h = 24

        steps_text = ["Witaj", "Licencja", "Instalacja", "Zakończono"]
        for i, text in enumerate(steps_text):
            y = self.base_y + i * self.spacing
            self.sidebar_targets.append(y)
            lbl = ctk.CTkLabel(self.sidebar, text=text, anchor="w", font=self.text_font)
            lbl.place(x=30, y=y)
            self.step_labels.append(lbl)

        self.indicator = ctk.CTkFrame(
            self.sidebar,
            width=self.indicator_w,
            height=self.indicator_h,
            fg_color="#4cc2ff",
            corner_radius=2,
        )
        self.indicator.place(x=self.indicator_x, y=self.sidebar_targets[0])

        # Page container
        self.frame = ctk.CTkFrame(self.content_frame, corner_radius=20)
        self.frame.pack(padx=20, pady=20, fill="both", expand=True)

        # Bottom buttons
        self.button_frame = ctk.CTkFrame(self.root, corner_radius=0)
        self.button_frame.pack(fill="x")

        self.back_button = ctk.CTkButton(
            self.button_frame,
            text="Wstecz",
            command=self.go_back,
            font=self.button_font,
            width=120,
            height=40,
        )
        self.back_button.pack(side="left", padx=20, pady=10)

        self.cancel_button = ctk.CTkButton(
            self.button_frame,
            text="Anuluj",
            command=self.cancel,
            font=self.button_font,
            width=120,
            height=40,
            fg_color="#8b1a1a",
            hover_color="#a11f1f",
        )
        self.cancel_button.pack(side="right", padx=20, pady=10)

        self.next_button = ctk.CTkButton(
            self.button_frame,
            text="Dalej",
            command=self.go_next,
            font=self.button_font,
            width=120,
            height=40,
        )
        self.next_button.pack(side="right", padx=10, pady=10)

        # Window fade-in
        self.root.attributes("-alpha", 0.0)
        self.fade_in_window()

        self.root.after(80, lambda: self.show_current_step(initial=True))

    # ---------- GLOBAL ANIMATIONS ----------
    def fade_in_window(self, alpha=0.0):
        alpha = min(alpha + 0.06, 1.0)
        self.root.attributes("-alpha", alpha)
        if alpha < 1.0:
            self.root.after(16, lambda: self.fade_in_window(alpha))

    def type_text(self, label, text, index=0, delay=18):
        if index <= len(text):
            label.configure(text=text[:index])
            self.root.after(delay, lambda: self.type_text(label, text, index + 1, delay))

    def pop_in_widget(self, widget, start_y=18, end_y=0, steps=8):
        # Lightweight “slide in + settle” effect for labels and controls.
        def step_anim(i=0):
            if i <= steps:
                y = start_y - (start_y - end_y) * (i / steps)
                widget.place_configure(rely=0.5, anchor="center")
                try:
                    widget.update_idletasks()
                except Exception:
                    pass
                self.root.after(12, lambda: step_anim(i + 1))
        step_anim()

    # ---------- SIDEBAR ----------
    def update_sidebar(self):
        for i, lbl in enumerate(self.step_labels):
            lbl.configure(text_color="#4cc2ff" if i == self.current_step else "gray")

        self.animate_sidebar_indicator()

    def animate_sidebar_indicator(self):
        target_y = self.sidebar_targets[self.current_step]

        # cancel previous animation if exists (prevents duplication)
        if hasattr(self, "sidebar_anim_job") and self.sidebar_anim_job:
            try:
                self.root.after_cancel(self.sidebar_anim_job)
            except Exception:
                pass

        def step_anim():
            current_y = self.indicator.winfo_y()
            diff = target_y - current_y

            if abs(diff) > 0.8:
                self.indicator.place(y=current_y + diff * 0.22)
                self.sidebar_anim_job = self.root.after(16, step_anim)
            else:
                self.indicator.place(y=target_y)
                self.sidebar_anim_job = None

        step_anim()

    # ---------- PAGE SWITCH ----------
    def show_current_step(self, initial=False, direction="left"):
        new_page = ctk.CTkFrame(self.frame, corner_radius=20)
        new_page.place(relwidth=1, relheight=1, x=0, y=0)

        self.steps[self.current_step](new_page)

        width = self.frame.winfo_width() or 600
        start_x = 0 if initial else (width if direction == "left" else -width)
        new_page.place(x=start_x, y=0, relwidth=1, relheight=1)

        if self.current_page is None:
            self.current_page = new_page
            self.update_buttons()
            self.update_sidebar()
            return

        old_page = self.current_page
        old_end_x = -width if direction == "left" else width
        self.animate_page(old_page, new_page, old_end_x)

    def animate_page(self, old_page, new_page, old_end_x):
        step = 34

        def anim():
            old_x = old_page.winfo_x()
            new_x = new_page.winfo_x()

            if old_end_x < 0:
                old_x = max(old_x - step, old_end_x)
            else:
                old_x = min(old_x + step, old_end_x)

            if new_x > 0:
                new_x = max(new_x - step, 0)
            else:
                new_x = min(new_x + step, 0)

            old_page.place(x=old_x, y=0)
            new_page.place(x=new_x, y=0)

            if old_x != old_end_x or new_x != 0:
                self.root.after(16, anim)
            else:
                old_page.destroy()
                self.current_page = new_page
                self.update_buttons()
                self.update_sidebar()

        anim()

    # ---------- BUTTONS ----------
    def update_buttons(self):
        self.back_button.configure(state=ctk.NORMAL if self.current_step > 0 else ctk.DISABLED)

        if self.current_step == len(self.steps) - 1:
            self.next_button.configure(text="Zakończ", command=self.finish)
        else:
            self.next_button.configure(text="Dalej", command=self.go_next)

        if self.current_step == 1:
            self.next_button.configure(state=ctk.NORMAL if getattr(self, "agree_var", ctk.BooleanVar(value=False)).get() else ctk.DISABLED)
            return

        self.next_button.configure(state=ctk.NORMAL)

    def start_download(self):
        if not hasattr(self, "download_url") or not self.download_url:
            self.root.after(0, lambda: self.install_status.configure(text="Brak adresu URL do pobrania."))
            return

        try:
            request = urllib.request.Request(
                self.download_url,
                headers={"User-Agent": "Mozilla/5.0"},
            )
            with urllib.request.urlopen(request, timeout=20) as response:
                total_length = response.getheader("Content-Length")
                total_size = int(total_length) if total_length else None
                url_path = urllib.parse.urlsplit(self.download_url).path
                file_name = os.path.basename(url_path) or "pobrany_plik"
                self.download_path = os.path.join(os.getcwd(), file_name)
                downloaded = 0

                with open(self.download_path, "wb") as out_file:
                    while True:
                        chunk = response.read(8192)
                        if not chunk:
                            break
                        out_file.write(chunk)
                        downloaded += len(chunk)
                        if total_size:
                            progress = downloaded / total_size
                        else:
                            progress = min(downloaded / (1024 * 1024 * 10), 1.0)

                        self.root.after(0, lambda p=progress: self.progress.set(p))
                        self.root.after(
                            0,
                            lambda d=downloaded, t=total_size: self.install_status.configure(
                                text=(
                                    f"Pobrano {d // 1024} KB / {t // 1024} KB"
                                    if t
                                    else f"Pobrano {d // 1024} KB"
                                )
                            ),
                        )

            self.root.after(0, lambda: self.install_status.configure(text="Pobieranie zakończone."))
            self.extract_downloaded_file()
        except urllib.error.URLError as error:
            self.root.after(0, lambda e=error: self.install_status.configure(text=f"Błąd pobierania: {e.reason}"))
        except Exception as error:
            self.root.after(0, lambda e=error: self.install_status.configure(text=f"Błąd: {e}"))

    def extract_downloaded_file(self):
        file_path = getattr(self, "download_path", None)
        if not file_path or not os.path.exists(file_path):
            self.root.after(0, lambda: self.install_status.configure(text="Plik nie został znaleziony po pobraniu."))
            return

        extension = os.path.splitext(file_path)[1].lower()
        extract_path = os.path.dirname(file_path)

        if extension == ".zip":
            try:
                with zipfile.ZipFile(file_path, "r") as archive:
                    archive.extractall(extract_path)
                self.root.after(0, lambda: self.install_status.configure(text="Plik rozpakowany."))
            except Exception as error:
                self.root.after(0, lambda: self.install_status.configure(text=f"Błąd rozpakowywania ZIP: {error}"))
                return
        elif extension == ".rar":
            if rarfile is None:
                self.root.after(0, lambda: self.install_status.configure(text="Brak wsparcia dla RAR. Zainstaluj moduł rarfile."))
                return
            try:
                with rarfile.RarFile(file_path) as archive:
                    archive.extractall(extract_path)
                self.root.after(0, lambda: self.install_status.configure(text="Plik rozpakowany."))
            except Exception as error:
                self.root.after(0, lambda: self.install_status.configure(text=f"Błąd rozpakowywania RAR: {error}"))
                return
        else:
            self.root.after(0, lambda: self.install_status.configure(text="Plik pobrany."))

        self.root.after(
            500,
            lambda: (
                self.progress.set(1.0),
                self.install_status.configure(text="Gotowe."),
                self.update_sidebar(),
                self.go_next(),
            ),
        )

    def go_next(self):
        if self.current_step < len(self.steps) - 1:
            self.current_step += 1
            self.update_sidebar()  # update immediately
            self.show_current_step(direction="left")

    def go_back(self):
        if self.current_step > 0:
            self.current_step -= 1
            self.update_sidebar()  # update immediately
            self.show_current_step(direction="right")

    def cancel(self):
        self.root.quit()

    def finish(self):
        self.root.quit()

    # ---------- PAGES ----------
    def show_welcome(self, parent):
        title = ctk.CTkLabel(parent, text="", font=self.title_font)
        title.pack(pady=(32, 10))
        self.type_text(title, "Witaj w Instalatorze")

        subtitle = ctk.CTkLabel(parent, text="", font=self.text_font, wraplength=520, justify="center")
        subtitle.pack(pady=(0, 18))
        self.type_text(subtitle, "Adres pobierania został wprowadzony w konsoli.")

        hint = ctk.CTkLabel(parent, text="", font=self.text_font, text_color="gray")
        hint.pack(pady=(8, 10))
        self.type_text(hint, f"Pobrany URL: {self.download_url}")

    def show_license(self, parent):
        title = ctk.CTkLabel(parent, text="", font=self.title_font)
        title.pack(pady=(24, 12))
        self.type_text(title, "Umowa Licencyjna")

        box = ctk.CTkTextbox(parent, height=185)
        box.pack(padx=22, pady=(6, 12), fill="x")
        box.insert("0.0", "Tutaj treść licencji...\n\nMożesz wkleić prawdziwą umowę licencyjną.")
        box.configure(state="disabled")

        self.agree_var = ctk.BooleanVar(value=False)
        checkbox = ctk.CTkCheckBox(
            parent,
            text="Akceptuję warunki",
            variable=self.agree_var,
            command=self.update_buttons,
            font=self.text_font,
        )
        checkbox.pack(pady=12)

    def show_installing(self, parent):
        title = ctk.CTkLabel(parent, text="", font=self.title_font)
        title.pack(pady=(34, 12))
        self.type_text(title, "Instalowanie...")

        self.install_status = ctk.CTkLabel(parent, text="", font=self.text_font, text_color="gray")
        self.install_status.pack(pady=(0, 18))
        self.install_status.configure(text="Pobieranie...")

        self.progress = ctk.CTkProgressBar(parent)
        self.progress.pack(padx=40, pady=10, fill="x")
        self.progress.set(0)

        threading.Thread(target=self.start_download, daemon=True).start()

    def start_install_animation(self):
        if self.current_step != 2:
            return

        self.install_progress = min(self.install_progress + 0.01, 1.0)
        if hasattr(self, "progress"):
            self.progress.set(self.install_progress)

        if self.install_progress < 1.0:
            self.install_job = self.root.after(25, self.start_install_animation)
        else:
            self.install_status.configure(text="Zakończono pomyślnie.")
            self.root.after(350, lambda: (self.update_sidebar(), self.go_next()))

    def show_finish(self, parent):
        title = ctk.CTkLabel(parent, text="", font=self.title_font)
        title.pack(pady=(48, 10))
        self.type_text(title, "Instalacja zakończona!")

        subtitle = ctk.CTkLabel(parent, text="", font=self.text_font, wraplength=520, justify="center")
        subtitle.pack(pady=(0, 14))
        self.type_text(subtitle, "Aplikacja została zainstalowana poprawnie.")

        finish_hint = ctk.CTkLabel(parent, text="", font=self.text_font, text_color="gray")
        finish_hint.pack(pady=8)
        self.type_text(finish_hint, "Kliknij Zakończ, aby zamknąć instalator.")

    def destroy_current_page(self):
        if self.current_page is not None:
            self.current_page.destroy()
            self.current_page = None


if __name__ == "__main__":
    download_url = ""
    while not download_url.strip():
        try:
            download_url = input("Podaj link do pobrania pliku ZIP/RAR: ").strip()
        except EOFError:
            download_url = ""

    root = ctk.CTk()
    app = InstallerApp(root, download_url=download_url)
    root.mainloop()
