import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import yt_dlp  # type: ignore
import threading
import json
import re

DEFAULT_FFMPEG_PATH = r"G:\Youtube Video Download\ffmpeg\bin"

class SettingsManager:
    """Handles saving and loading application settings."""
    def __init__(self, filename="settings.json"):
        self.filename = filename
        self.settings = self.load_settings()

    def load_settings(self):
        try:
            with open(self.filename, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def save_settings(self, new_settings):
        self.settings.update(new_settings)
        with open(self.filename, "w") as f:
            json.dump(self.settings, f, indent=4)


class YouTubeDownloader:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube Vintage Downloader")
        self.root.geometry("800x600")
        self.root.resizable(False, False)

        self.settings_manager = SettingsManager()
        self.settings = self.settings_manager.settings
        self.ffmpeg_path = self.settings.get("ffmpeg_path", DEFAULT_FFMPEG_PATH)
        self.save_path = self.settings.get("save_path")
        self.stop_event = threading.Event()

        self.current_theme = tk.StringVar(value=self.settings.get("theme", "light"))
        self.themes = {
            "light": {"bg": "#C0C0C0", "fg": "black", "entry_bg": "#E0E0E0", "button_bg": "#D0D0D0", "relief": "raised"},
            "dark": {"bg": "#333333", "fg": "white", "entry_bg": "#555555", "button_bg": "#666666", "relief": "flat"}
        }
        
        style = ttk.Style()
        style.theme_use('default')

        self.queue_data = []

        self._create_widgets()
        self.set_theme(self.current_theme.get())

    def _create_widgets(self):
        """Initializes and packs all the main GUI components."""
        self._create_input_frame()
        self._create_options_frame()
        self._create_control_buttons()
        self._create_queue_display()
        self._create_status_bar()
        self._create_menu_bar()

        if self.save_path:
            self.status_label.config(text=f"Save Path: {self.save_path}")

    def _create_input_frame(self):
        """Creates the frame for URL input."""
        input_frame = tk.Frame(self.root)
        input_frame.pack(pady=10)
        tk.Label(input_frame, text="YouTube URL:", font=("MS Sans Serif", 10, "bold")).grid(row=0, column=0, pady=5, padx=5, sticky="w")
        self.url_entry = tk.Entry(input_frame, width=70, font=("MS Sans Serif", 10), relief="sunken", bd=2)
        self.url_entry.grid(row=0, column=1, columnspan=3, pady=5, padx=5)

    def _create_options_frame(self):
        """Creates the frame for download options."""
        options_frame = tk.LabelFrame(self.root, text="Download Options", font=("MS Sans Serif", 10, "bold"), bd=2, relief="groove")
        options_frame.pack(padx=20, pady=10, fill="x")

        # Quality & File Type
        tk.Label(options_frame, text="Select Quality:", font=("MS Sans Serif", 10)).grid(row=0, column=0, pady=5, padx=5, sticky="w")
        self.quality_var = tk.StringVar(self.root)
        self.quality_var.set("720p")
        qualities = ["144p", "240p", "360p", "480p", "720p", "1080p", "best"]
        self.quality_menu = ttk.Combobox(options_frame, textvariable=self.quality_var, values=qualities, state="readonly")
        self.quality_menu.grid(row=0, column=1, pady=5, padx=5, sticky="w")

        tk.Label(options_frame, text="File Type:", font=("MS Sans Serif", 10)).grid(row=0, column=2, pady=5, padx=5, sticky="w")
        self.file_type_var = tk.StringVar(value="Video")
        file_types = ["Video", "Audio (MP3)"]
        self.file_type_menu = ttk.Combobox(options_frame, textvariable=self.file_type_var, values=file_types, state="readonly")
        self.file_type_menu.grid(row=0, column=3, pady=5, padx=5, sticky="w")

        # Playlist Checkbox
        self.is_playlist = tk.BooleanVar()
        ttk.Checkbutton(options_frame, text="Download Playlist", variable=self.is_playlist).grid(row=1, column=0, pady=5, padx=5, sticky="w")

    def _create_control_buttons(self):
        """Creates the buttons for queue management and download control."""
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=10)
        ttk.Button(button_frame, text="Add to Queue", command=self.add_to_queue).grid(row=0, column=0, padx=5, pady=5)
        ttk.Button(button_frame, text="Clear Queue", command=self.clear_queue).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(button_frame, text="Start Download", command=self.start_download_thread).grid(row=0, column=2, padx=5, pady=5)
        ttk.Button(button_frame, text="Cancel Download", command=self.cancel_download).grid(row=0, column=3, padx=5, pady=5)

    def _create_queue_display(self):
        """Creates the Treeview for the download queue."""
        queue_frame = tk.LabelFrame(self.root, text="Download Queue", font=("MS Sans Serif", 10, "bold"), bd=2, relief="groove")
        queue_frame.pack(padx=20, pady=10, fill="both", expand=True)
        self.queue_tree = ttk.Treeview(queue_frame, columns=("URL", "Type", "Quality"), show="headings")
        self.queue_tree.heading("URL", text="URL")
        self.queue_tree.heading("Type", text="Type")
        self.queue_tree.heading("Quality", text="Quality")
        self.queue_tree.column("Type", width=100)
        self.queue_tree.column("Quality", width=100)
        self.queue_tree.pack(side="left", fill="both", expand=True)
        scrollbar = ttk.Scrollbar(queue_frame, orient="vertical", command=self.queue_tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.queue_tree.configure(yscrollcommand=scrollbar.set)

    def _create_status_bar(self):
        """Creates the progress bar and status label."""
        tk.Label(self.root, text="Download Progress:", font=("MS Sans Serif", 9, "bold")).pack(pady=5)
        self.progress = ttk.Progressbar(self.root, length=400, mode="determinate")
        self.progress.pack(pady=5)
        self.status_label = tk.Label(self.root, text="Ready", bd=1, relief="sunken", anchor="w", font=("MS Sans Serif", 9))
        self.status_label.pack(side="bottom", fill="x")

    def _create_menu_bar(self):
        """Creates the application menu bar."""
        menu_bar = tk.Menu(self.root)
        self.root.config(menu=menu_bar)
        file_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Settings", command=self.open_settings_dialog)
        theme_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Theme", menu=theme_menu)
        theme_menu.add_radiobutton(label="Light Mode", value="light", variable=self.current_theme, command=lambda: self.set_theme("light"))
        theme_menu.add_radiobutton(label="Dark Mode", value="dark", variable=self.current_theme, command=lambda: self.set_theme("dark"))

    def set_theme(self, theme_name):
        """Applies the selected theme to the entire application."""
        theme = self.themes[theme_name]
        self.root.configure(bg=theme["bg"])
        self.settings_manager.save_settings({"theme": theme_name})
        for widget in self.root.winfo_children():
            self.apply_theme_to_widget(widget, theme)
        self.root.option_add('*tearOff', 'False')
        self.root.configure(menu=self.root['menu'])
        
    def apply_theme_to_widget(self, widget, theme):
        """Recursively applies theme styles to widgets."""
        if isinstance(widget, (ttk.Frame, ttk.Label, ttk.Button, ttk.Checkbutton, ttk.Combobox, ttk.Progressbar, ttk.Scrollbar, ttk.Treeview)):
            style = ttk.Style()
            style_name = widget.winfo_class()
            style.configure(style_name, background=theme["bg"], foreground=theme["fg"])
            try:
                widget.configure(style=style_name)
            except tk.TclError:
                pass
        elif isinstance(widget, (tk.Label, tk.LabelFrame, tk.Frame, tk.Toplevel, tk.Menu)):
            try:
                widget.configure(bg=theme["bg"], fg=theme["fg"])
            except tk.TclError:
                pass
        elif isinstance(widget, tk.Entry):
            try:
                widget.configure(bg=theme["entry_bg"], fg=theme["fg"], insertbackground=theme["fg"])
            except tk.TclError:
                pass
        for child in widget.winfo_children():
            self.apply_theme_to_widget(child, theme)

    def open_settings_dialog(self):
        """Creates and displays the settings dialog box."""
        settings_dialog = tk.Toplevel(self.root)
        settings_dialog.title("Settings")
        settings_dialog.geometry("400x200")
        settings_dialog.configure(bg="#C0C0C0")
        tk.Label(settings_dialog, text="FFmpeg Path:", bg="#C0C0C0").pack(pady=5)
        ffmpeg_entry = tk.Entry(settings_dialog, width=40)
        ffmpeg_entry.insert(0, self.ffmpeg_path)
        ffmpeg_entry.pack(pady=5)
        tk.Label(settings_dialog, text="Default Save Path:", bg="#C0C0C0").pack(pady=5)
        save_path_entry = tk.Entry(settings_dialog, width=40)
        save_path_entry.insert(0, self.save_path or "")
        save_path_entry.pack(pady=5)
        def browse_save_path():
            folder = filedialog.askdirectory()
            if folder:
                save_path_entry.delete(0, tk.END)
                save_path_entry.insert(0, folder)
        ttk.Button(settings_dialog, text="Browse", command=browse_save_path).pack(pady=5)
        def save_and_close():
            self.ffmpeg_path = ffmpeg_entry.get()
            self.save_path = save_path_entry.get()
            self.settings_manager.save_settings({"ffmpeg_path": self.ffmpeg_path, "save_path": self.save_path})
            self.status_label.config(text=f"Save Path: {self.save_path}")
            messagebox.showinfo("Settings Saved", "Settings have been saved successfully!")
            settings_dialog.destroy()
        ttk.Button(settings_dialog, text="Save", command=save_and_close).pack(pady=10)
        self.apply_theme_to_widget(settings_dialog, self.themes[self.current_theme.get()])

    def add_to_queue(self):
        """Adds the current URL and options to the download queue."""
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showerror("Error", "Please enter a YouTube URL!")
            return
        quality = self.quality_var.get()
        file_type = self.file_type_var.get()
        is_playlist = self.is_playlist.get()
        self.queue_data.append({"url": url, "quality": quality, "file_type": file_type, "is_playlist": is_playlist})
        self.queue_tree.insert("", "end", values=(url, file_type, quality))
        self.url_entry.delete(0, tk.END)
        self.status_label.config(text=f"Added '{url}' to queue. {len(self.queue_data)} items in queue.")

    def clear_queue(self):
        """Clears all items from the download queue."""
        self.queue_data = []
        for item in self.queue_tree.get_children():
            self.queue_tree.delete(item)
        self.status_label.config(text="Download queue cleared.")

    def start_download_thread(self):
        """Starts the download process in a separate thread."""
        if not self.queue_data:
            messagebox.showerror("Error", "The download queue is empty!")
            return
        if not self.save_path:
            messagebox.showerror("Error", "Please set a default save folder in Settings!")
            return
        self.stop_event.clear()
        download_thread = threading.Thread(target=self.process_queue)
        download_thread.start()

    def cancel_download(self):
        """Cancels the current download process."""
        self.stop_event.set()
        self.status_label.config(text="Cancellation requested. Waiting for current process to finish.")

    def process_queue(self):
        """Iterates through the queue and downloads each item."""
        while self.queue_data and not self.stop_event.is_set():
            item = self.queue_data.pop(0)
            if self.queue_tree.get_children():
                self.queue_tree.delete(self.queue_tree.get_children()[0])
            self.download_item(item)
            if self.stop_event.is_set():
                break
        self.status_label.config(text="Download queue finished!")
        self.progress["value"] = 0

    def download_item(self, item):
        """Handles the actual download of a single video or playlist item."""
        url = item["url"]
        quality = item["quality"]
        file_type = item["file_type"]
        is_playlist = item["is_playlist"]
        ydl_opts = {"progress_hooks": [self.progress_hook]}
        if file_type == "Audio (MP3)":
            ydl_opts["format"] = "bestaudio/best"
            ydl_opts["postprocessors"] = [{"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "192"}]
        else:
            quality_map = {
                "144p": "bestvideo[height<=144][ext=mp4][vcodec^=avc1]+bestaudio[ext=m4a]/best[height<=144][ext=mp4]",
                "240p": "bestvideo[height<=240][ext=mp4][vcodec^=avc1]+bestaudio[ext=m4a]/best[height<=240][ext=mp4]",
                "360p": "bestvideo[height<=360][ext=mp4][vcodec^=avc1]+bestaudio[ext=m4a]/best[height<=360][ext=mp4]",
                "480p": "bestvideo[height<=480][ext=mp4][vcodec^=avc1]+bestaudio[ext=m4a]/best[height<=480][ext=mp4]",
                "720p": "bestvideo[height<=720][ext=mp4][vcodec^=avc1]+bestaudio[ext=m4a]/best[height<=720][ext=mp4]",
                "1080p": "bestvideo[height<=1080][ext=mp4][vcodec^=avc1]+bestaudio[ext=m4a]/best[height<=1080][ext=mp4]",
                "best": "bestvideo[ext=mp4][vcodec^=avc1]+bestaudio[ext=m4a]/best[ext=mp4]"
            }
            ydl_opts["format"] = quality_map.get(quality, "best")
            ydl_opts["merge_output_format"] = "mp4"
            ydl_opts["postprocessors"] = [{"key": "FFmpegVideoConvertor", "preferedformat": "mp4"}]
        if self.ffmpeg_path:
            ydl_opts["ffmpeg_location"] = self.ffmpeg_path
        if is_playlist:
            ydl_opts["outtmpl"] = os.path.join(self.save_path, "%(playlist)s/%(playlist_index)s - %(title)s.%(ext)s")
        else:
            ydl_opts["outtmpl"] = os.path.join(self.save_path, "%(title)s.%(ext)s")
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
        except Exception as e:
            self.status_label.config(text=f"Error downloading {url}")
            messagebox.showerror("Download Error", f"Failed to download {url}\n\n{str(e)}")

    def progress_hook(self, d):
        """Updates the progress bar and status label during download."""
        if self.stop_event.is_set():
            raise yt_dlp.utils.DownloadCancelled()
        if d['status'] == 'downloading':
            total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate')
            downloaded_bytes = d.get('downloaded_bytes')
            speed = d.get('_speed_str', 'N/A')
            eta = d.get('_eta_str', 'N/A')
            if total_bytes and downloaded_bytes:
                percent = (downloaded_bytes / total_bytes) * 100
                self.progress["value"] = percent
                self.status_label.config(text=f"Downloading... {percent:.1f}% at {speed} | ETA: {eta}")
            else:
                self.status_label.config(text=f"Downloading... {d.get('_percent_str', 'N/A')}")
        elif d['status'] == 'finished':
            self.progress["value"] = 100
            self.status_label.config(text="Finalizing download...")
        self.root.update_idletasks()


if __name__ == "__main__":
    root = tk.Tk()
    app = YouTubeDownloader(root)
    root.mainloop()