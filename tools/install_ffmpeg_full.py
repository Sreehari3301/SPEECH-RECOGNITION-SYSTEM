import os
import sys
import zipfile
import urllib.request
import shutil

def install_ffmpeg_full():
    """Download complete FFmpeg suite including ffprobe"""
    print("Downloading complete FFmpeg suite...")
    
    # URL for complete Windows Build
    url = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
    zip_path = "ffmpeg_full.zip"
    extract_path = "ffmpeg_extract"
    
    try:
        # 1. Download
        print(f"Downloading from {url}...")
        urllib.request.urlretrieve(url, zip_path)
        print("Download complete.")
        
        # 2. Extract
        print("Extracting...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_path)
            
        # 3. Locate bin folder with all executables
        bin_folder = None
        for root, dirs, files in os.walk(extract_path):
            if "bin" in dirs:
                potential_bin = os.path.join(root, "bin")
                # Check if it has ffmpeg.exe
                if os.path.exists(os.path.join(potential_bin, "ffmpeg.exe")):
                    bin_folder = potential_bin
                    break
        
        if not bin_folder:
            print("Could not find bin folder in the downloaded archive.")
            return

        # 4. Copy all executables to ./bin
        target_dir = os.path.join(os.getcwd(), "bin")
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)
        
        # Copy all .exe files from the bin folder
        copied_files = []
        for file in os.listdir(bin_folder):
            if file.endswith('.exe'):
                src = os.path.join(bin_folder, file)
                dst = os.path.join(target_dir, file)
                shutil.copy2(src, dst)
                copied_files.append(file)
                print(f"Copied: {file}")
        
        print(f"\nSUCCESS: Installed {len(copied_files)} files to {target_dir}")
        print(f"Files: {', '.join(copied_files)}")
        
        # Cleanup
        print("\nCleaning up...")
        os.remove(zip_path)
        shutil.rmtree(extract_path)
        
        print("\n✓ FFmpeg suite installed successfully!")

    except Exception as e:
        print(f"Error installing ffmpeg: {e}")

if __name__ == "__main__":
    install_ffmpeg_full()
