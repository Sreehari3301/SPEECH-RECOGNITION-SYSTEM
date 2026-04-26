# SPEECH-RECOGNITION-SYSTEM

## 🎉 What's New

Your speech-to-text system has been successfully upgraded with **multilingual translation capabilities**!

## ✨ New Features

### 1. **Multi-Language Transcription**
The system now supports transcription in **6 languages**:
- 🇬🇧 **English**
- 🇮🇳 **Malayalam** (മലയാളം)
- 🇮🇳 **Hindi** (हिन्दी)
- 🇮🇳 **Tamil** (தமிழ்)
- 🇮🇳 **Kannada** (ಕನ್ನಡ)
- 🇮🇳 **Telugu** (తెలుగు)

### 2. **Translation Between Languages**
After transcribing audio, you can now translate the text between any of the supported languages:
- **Auto-detect** source language
- Translate from any language to any other language
- Real-time translation with visual feedback

### 3. **Enhanced User Interface**
- New **Translation Panel** with language selection dropdowns
- Visual language indicators with flag emojis
- Smooth animations and transitions
- Loading states for translation process
- Error handling with user-friendly messages

## 🔧 Technical Changes

### Backend (`main.py`)
- ✅ Added `googletrans` library for translation
- ✅ New `/translate` endpoint for text translation
- ✅ Enhanced `/transcribe` endpoint with language parameter
- ✅ Language code mapping for all supported languages
- ✅ Auto-detection support for source language

### Frontend (`index.html`)
- ✅ New translation section with language selectors
- ✅ "From" and "To" language dropdowns
- ✅ Translate button with loading states
- ✅ Translation output display area
- ✅ Updated tagline to mention translation

### JavaScript (`script.js`)
- ✅ Translation button event handler
- ✅ `translateText()` async function
- ✅ Language parameter in transcription requests
- ✅ Enhanced clear button to reset both transcription and translation
- ✅ Detected language display in transcription results

### Styling (`style.css`)
- ✅ Translation panel styles with glassmorphism
- ✅ Language selector styling with hover effects
- ✅ Translate button with gradient background
- ✅ Translation output area with fade-in animation
- ✅ Responsive design for mobile devices

### Dependencies (`requirements.txt`)
- ✅ Added `googletrans==4.0.0rc1`

## 📖 How to Use

### Step 1: Transcribe Audio
1. **Record** audio by clicking "Start Recording" 
                 OR
 **File Upload**: Upload existing audio files in multiple formats:
  - **WAV** (native support, no FFmpeg needed)
  - **MP3** (requires FFmpeg)
  - **M4A** (requires FFmpeg)
  - **OPUS** (requires FFmpeg)
  - **OGG** (requires FFmpeg)
2. **Select** the language of your audio (or use Auto-detect)
3. Wait for the transcription to appear

### Step 2: Translate (Optional)
1. After transcription appears, scroll to the **Translation** section
2. Select the **source language** (or use Auto-detect)
3. Select the **target language** you want to translate to
4. Click the **"Translate"** button
5. View the translated text below

## 🎨 UI Features

### Language Selection
- **Auto-detect**: Automatically identifies the language
- **Flag Emojis**: Visual indicators for each language
- **Native Scripts**: Language names shown in their native scripts

### Visual Feedback
- **Loading States**: Spinner animation during translation
- **Language Path**: Shows "Source → Target" language path
- **Error Messages**: Clear error messages if something goes wrong
- **Fade-in Animation**: Smooth appearance of translated text

## 🚀 Running the Application

1. **Installation**:

1. Create a virtual environment:
   ```bash
   python -m venv venv
   ```
2. Activate it:
   - Windows: `.\venv\Scripts\Activate`
   - Linux/Mac: `source venv/bin/activate`
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. **Start the server**:
   ```bash
   uvicorn main:app --reload
   ```
   Or double-click `run.bat`

3. **Open your browser**:
   Navigate to [http://127.0.0.1:8000](http://127.0.0.1:8000)

## 🌟 Example Use Cases

1. **Malayalam to English**: Transcribe Malayalam audio and translate to English
2. **Hindi to Tamil**: Transcribe Hindi audio and translate to Tamil
3. **Auto-detect**: Upload audio in any language, auto-detect it, and translate to your preferred language
4. **Multi-step Translation**: Transcribe in one language, translate to another, then copy the result

## 🔒 Privacy & API Usage

- **Speech Recognition**: Uses Google's Speech Recognition API (free tier)
- **Translation**: Uses Google Translate API via `googletrans` library (free)
- **No API Keys Required**: Both services work without authentication for basic usage

## 📝 Notes

- Translation works on the transcribed text, so ensure accurate transcription first
- For best results, speak clearly when recording
- Auto-detect works best with longer text samples
- Internet connection required for both transcription and translation

## 🎯 Future Enhancements (Ideas)

- Download translated text as file
- Translation history
- Batch translation of multiple files
- Voice output of translated text (Text-to-Speech)
- Support for more languages

---
## Output
<img width="1896" height="912" alt="Image" src="https://github.com/user-attachments/assets/2efc5edc-dc46-437c-989c-5c81bdf342d0" />
<img width="1886" height="989" alt="Image" src="https://github.com/user-attachments/assets/75412698-e8bd-4d40-9899-5f616151143e" />

**Enjoy your upgraded multilingual speech-to-text and translation system! 🎊**
