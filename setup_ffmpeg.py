import os
import urllib.request
import zipfile
import shutil

def setup_ffmpeg():
    bin_dir = "bin"
    if not os.path.exists(bin_dir):
        os.makedirs(bin_dir)
    
    # URL for a reliable FFmpeg build
    ffmpeg_url = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
    
    zip_path = "ffmpeg.zip"
    
    print("Downloading FFmpeg (this may take a minute)...")
    try:
        urllib.request.urlretrieve(ffmpeg_url, zip_path)
            
        print("Extracting...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # Find the ffmpeg.exe and ffprobe.exe inside the zip
            for member in zip_ref.namelist():
                if member.endswith("ffmpeg.exe"):
                    with zip_ref.open(member) as source, open(os.path.join(bin_dir, "ffmpeg.exe"), "wb") as target:
                        shutil.copyfileobj(source, target)
                if member.endswith("ffprobe.exe"):
                    with zip_ref.open(member) as source, open(os.path.join(bin_dir, "ffprobe.exe"), "wb") as target:
                        shutil.copyfileobj(source, target)
        
        print("FFmpeg setup complete! Binaries are in the 'bin' folder.")
    except Exception as e:
        print(f"Error during setup: {e}")
    finally:
        if os.path.exists(zip_path):
            os.remove(zip_path)

if __name__ == "__main__":
    setup_ffmpeg()
