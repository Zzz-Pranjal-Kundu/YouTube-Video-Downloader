# YouTube Vintage Downloader

A simple yet powerful desktop application for downloading videos and audio from YouTube and other supported sites. Built with Python and `tkinter`, this tool provides a user-friendly graphical interface for `yt-dlp`, the feature-rich command-line video downloader.

## ✨ Features

* **GUI Interface:** A clean, easy-to-use graphical interface.

* **Video & Audio Downloads:** Download videos in various qualities (up to 1080p) or extract audio and save it as an MP3 file.

* **Batch Downloads:** Add multiple URLs to a download queue to download them one after another.

* **Real-time Progress:** Track the download progress with a progress bar and status updates.

* **Configurable Settings:** Set your default save directory and the path to your FFmpeg executable.

* **Light & Dark Themes:** Switch between different themes to match your preference.

* **Playlist Support:** Download entire playlists with a single click.

## 🛠️ Prerequisites

Before you can use this application, you need to have the following software installed on your system:

* **Python 3.x:** This application is built with Python 3.

* **FFmpeg:** A crucial dependency for processing video and audio files. This application will not work correctly without it.

* **`yt-dlp` library:** The core library used for fetching and downloading content.

## 📥 Installation

1. **Clone the repository:**

     git clone https://github.com/Zzz-Pranjal-Kundu/YouTube-Video-Downloader.git
     cd YouTube-Video-Downloader

2. **Install the required Python libraries:**

    pip install yt-dlp
    pip install pyinstaller # Required for building the executable


3. **Download FFmpeg:**

    * Go to the official [FFmpeg website](https://ffmpeg.org/download.html).
    
    * Download the build for your operating system (Windows, macOS, or Linux).
    
    * Unzip the file and note the path to the `bin` folder, which contains `ffmpeg.exe`, `ffplay.exe`, and `ffprobe.exe`.

4. **Configure the FFmpeg Path:**

    * Run the application once and open the **Settings** dialog from the **File** menu.
    
    * In the FFmpeg path field, enter the full path to your FFmpeg `bin` folder (e.g., `C:\ffmpeg\bin`).

## 🚀 How to Use

1. **Run the application:**

    python DownloaderFile.py


2. **Enter the URL:** Paste a YouTube video or playlist URL into the "YouTube URL" field.

3. **Select Options:**

    * Choose your desired video quality from the "Select Quality" dropdown.
    
    * Select "Audio (MP3)" from the "File Type" dropdown if you only want to download the audio.
    
    * Check the "Download Playlist" box if you have entered a playlist URL.

4. **Add to Queue:** Click the **Add to Queue** button. The URL and its settings will appear in the download queue. You can add as many items as you want.

5. **Start Download:** Click **Start Download** to begin processing the queue. The progress bar and status label will show the progress of the current download.

6. **Cancel:** Click **Cancel Download** at any time to stop the current download and exit the queue.

## 🏗️ Building an Executable

If you want to distribute a single, standalone executable that others can use without installing Python, you can use PyInstaller.

1. **Open your terminal** in the project directory.

2. **Run the following command:**

   ```bash
   pyinstaller --onefile --noconsole --add-data "path\to\your\ffmpeg\bin;ffmpeg\bin" DownloaderFile.py
   ```

    Replace `path\to\your\ffmpeg\bin` with the actual path to your FFmpeg bin folder.

3. The executable file will be created in the `dist/` folder.

## NOTE
In Case the exe file does not work or download, run the following command and then try the above steps once again,
     
   ```bash
     pip install --upgrade yt-dlp
   ```

## 📄 License

This project is licensed under the MIT License
