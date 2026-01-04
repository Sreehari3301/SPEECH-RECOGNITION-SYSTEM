from fastapi import FastAPI, UploadFile, File, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import speech_recognition as sr
import io
import shutil
import os
from pydub import AudioSegment
from pydub.utils import make_chunks
from googletrans import Translator
import time

# Configure FFmpeg path
BIN_DIR = os.path.join(os.path.dirname(__file__), "bin")
FFMPEG_PATH = os.path.join(BIN_DIR, "ffmpeg.exe")
FFPROBE_PATH = os.path.join(BIN_DIR, "ffprobe.exe")

if os.path.exists(FFMPEG_PATH) and os.path.exists(FFPROBE_PATH):
    # Add bin directory to PATH so pydub can find FFmpeg
    os.environ["PATH"] = BIN_DIR + os.pathsep + os.environ.get("PATH", "")
    
    # Also set pydub's internal references (backup method)
    from pydub.utils import which
    AudioSegment.converter = FFMPEG_PATH
    AudioSegment.ffmpeg = FFMPEG_PATH
    AudioSegment.ffprobe = FFPROBE_PATH
    
    print(f"FFmpeg configured at: {FFMPEG_PATH}")
    print(f"FFprobe configured at: {FFPROBE_PATH}")
else:
    print("Warning: Local FFmpeg not found. Falling back to system FFmpeg.")

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...), language: str = "auto", duration: int = 600):
    """
    Transcribe audio file with language support.
    Supported languages: en-IN (English), ml-IN (Malayalam), hi-IN (Hindi), 
                        ta-IN (Tamil), kn-IN (Kannada), te-IN (Telugu), auto (Auto-detect)
    """
    # Language code mapping
    LANGUAGE_CODES = {
        "auto": None,  # Will try multiple languages
        "english": "en-IN",
        "malayalam": "ml-IN",
        "hindi": "hi-IN",
        "tamil": "ta-IN",
        "kannada": "kn-IN",
        "telugu": "te-IN"
    }
    
    # Get language code
    lang_code = LANGUAGE_CODES.get(language.lower(), "en-IN")
    
    temp_filename = f"temp_{int(time.time())}_{file.filename}"
    try:
        # Save temp file
        with open(temp_filename, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        recognizer = sr.Recognizer()
        
        # Load audio using Pydub
        try:
            file_ext = temp_filename.lower().split('.')[-1]
            if temp_filename.lower().endswith(".wav"):
                sound = AudioSegment.from_wav(temp_filename)
            elif file_ext in ['mp3', 'mpeg']:
                sound = AudioSegment.from_mp3(temp_filename)
            elif file_ext in ['m4a', 'mp4']:
                sound = AudioSegment.from_file(temp_filename, format='m4a')
            elif file_ext == 'opus':
                sound = AudioSegment.from_file(temp_filename, format='opus')
            elif file_ext == 'ogg':
                sound = AudioSegment.from_ogg(temp_filename)
            else:
                sound = AudioSegment.from_file(temp_filename)
        except Exception as e:
            error_msg = str(e)
            if "ffmpeg" in error_msg.lower() or "file not found" in error_msg.lower():
                return JSONResponse(
                    content={"error": f"FFmpeg error: {error_msg}. Please ensure FFmpeg is properly installed."}, 
                    status_code=400
                )
            return JSONResponse(content={"error": f"Audio loading failed: {str(e)}"}, status_code=400)

        # Truncate to requested duration
        if len(sound) > duration * 1000:
            sound = sound[:duration * 1000]

        # Split into 30-second chunks for better reliability with Google API
        chunk_length_ms = 30000 
        chunks = make_chunks(sound, chunk_length_ms)
        
        full_transcript = []
        detected_lang_name = None
        
        # Determine languages to use
        if lang_code is None:
            languages_to_try = ["en-IN", "ml-IN", "hi-IN", "ta-IN", "kn-IN", "te-IN"]
            # Detect language on the first chunk
            first_chunk = chunks[0]
            buf = io.BytesIO()
            first_chunk.export(buf, format="wav")
            buf.seek(0)
            
            best_lang = "en-IN"
            best_text = ""
            
            with sr.AudioFile(buf) as source:
                audio_chunk = recognizer.record(source)
                for lang in languages_to_try:
                    try:
                        text = recognizer.recognize_google(audio_chunk, language=lang)
                        if text:
                            best_lang = lang
                            best_text = text
                            break
                    except:
                        continue
            
            lang_code = best_lang
            if best_text:
                full_transcript.append(best_text)
                # Skip first chunk in the loop below
                chunks_to_process = chunks[1:]
            else:
                chunks_to_process = chunks[1:]
                
            # Map lang code to name
            lang_names = {
                "en-IN": "English", "ml-IN": "Malayalam", "hi-IN": "Hindi",
                "ta-IN": "Tamil", "kn-IN": "Kannada", "te-IN": "Telugu"
            }
            detected_lang_name = lang_names.get(lang_code, lang_code)
        else:
            chunks_to_process = chunks

        # Process remaining chunks
        for i, chunk in enumerate(chunks_to_process):
            buf = io.BytesIO()
            chunk.export(buf, format="wav")
            buf.seek(0)
            
            with sr.AudioFile(buf) as source:
                audio_chunk = recognizer.record(source)
                try:
                    text = recognizer.recognize_google(audio_chunk, language=lang_code)
                    if text:
                        full_transcript.append(text)
                except sr.UnknownValueError:
                    continue
                except sr.RequestError:
                    return JSONResponse(content={"error": "Google API unavailable"}, status_code=503)
                except Exception:
                    continue
        
        final_text = " ".join(full_transcript).strip()
        
        if not final_text:
            return JSONResponse(
                content={"error": "Speech could not be understood. Try speaking more clearly or check audio quality."}, 
                status_code=400
            )

        response_data = {"transcript": final_text}
        if detected_lang_name:
            response_data["detected_language"] = detected_lang_name
        else:
            response_data["language"] = language
            
        return response_data

    except Exception as e:
        return JSONResponse(content={"error": f"Server error: {str(e)}"}, status_code=500)
    finally:
        # Cleanup temp
        if os.path.exists(temp_filename):
            try:
                os.remove(temp_filename)
            except:
                pass

@app.post("/translate")
async def translate_text(request: Request):
    """
    Translate text between supported languages.
    Supported languages: English, Malayalam, Hindi, Tamil, Kannada, Telugu
    """
    try:
        data = await request.json()
        text = data.get("text", "")
        source_lang = data.get("source_language", "auto")
        target_lang = data.get("target_language", "english")
        
        if not text:
            return JSONResponse(
                content={"error": "No text provided for translation"}, 
                status_code=400
            )
        
        # Language code mapping for Google Translate
        TRANSLATE_CODES = {
            "auto": "auto",
            "english": "en",
            "malayalam": "ml",
            "hindi": "hi",
            "tamil": "ta",
            "kannada": "kn",
            "telugu": "te"
        }
        
        # Language names for display
        LANG_NAMES = {
            "en": "English",
            "ml": "Malayalam",
            "hi": "Hindi",
            "ta": "Tamil",
            "kn": "Kannada",
            "te": "Telugu"
        }
        
        source_code = TRANSLATE_CODES.get(source_lang.lower(), "auto")
        target_code = TRANSLATE_CODES.get(target_lang.lower(), "en")
        
        # Prepare translator
        from httpx import Timeout
        translator = Translator(timeout=Timeout(15.0))
        
        # Google Translate character limit is approx 5000
        # For safety and better context, we'll split by sentences or blocks if very long
        MAX_CHARS = 3000
        
        if len(text) <= MAX_CHARS:
            translation = translator.translate(text, src=source_code, dest=target_code)
            translated_text = translation.text
            detected_src = translation.src
        else:
            # Split text into chunks that don't break words
            text_chunks = []
            while len(text) > 0:
                if len(text) <= MAX_CHARS:
                    text_chunks.append(text)
                    break
                
                # Find last punctuation or space before limit
                split_idx = text.rfind('. ', 0, MAX_CHARS)
                if split_idx == -1: split_idx = text.rfind(' ', 0, MAX_CHARS)
                if split_idx == -1: split_idx = MAX_CHARS
                
                text_chunks.append(text[:split_idx])
                text = text[split_idx:].strip()
            
            translated_parts = []
            detected_src = "auto"
            for chunk in text_chunks:
                part = translator.translate(chunk, src=source_code, dest=target_code)
                translated_parts.append(part.text)
                detected_src = part.src # Keep last or consistent one
            
            translated_text = " ".join(translated_parts)
        
        # Get labels
        detected_lang_label = LANG_NAMES.get(detected_src, detected_src)
        target_lang_name = LANG_NAMES.get(target_code, target_code)
        
        return {
            "original_text": text,
            "translated_text": translated_text,
            "source_language": detected_lang_label,
            "target_language": target_lang_name
        }
        
    except Exception as e:
        return JSONResponse(
            content={"error": f"Translation failed: {str(e)}"}, 
            status_code=500
        )
