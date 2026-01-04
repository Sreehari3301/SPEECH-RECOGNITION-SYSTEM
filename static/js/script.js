/* Simple WAV Recorder implementation */
let audioContext;
let mediaStream;
let recorder;
let input;
let isRecording = false;
let startTime;
let timerInterval;

const recordBtn = document.getElementById('recordBtn');
const recordText = document.getElementById('recordText');
const visualizer = document.getElementById('visualizer');
const timer = document.getElementById('timer');
const uploadClickTarget = document.getElementById('uploadClickTarget');
const audioInput = document.getElementById('audioInput');
const fileName = document.getElementById('fileName');

const transcriptionBox = document.getElementById('transcriptionBox');
const loader = document.getElementById('loader');
const copyBtn = document.getElementById('copyBtn');
const clearBtn = document.getElementById('clearBtn');

// Translation elements
const translateBtn = document.getElementById('translateBtn');
const translateFrom = document.getElementById('translateFrom');
const translateTo = document.getElementById('translateTo');
const translationOutput = document.getElementById('translationOutput');
const languageSelect = document.getElementById('languageSelect');
const copyTranslationBtn = document.getElementById('copyTranslationBtn');
const durationInput = document.getElementById('durationInput');

// ... WAV Encoding Logic ...
function writeString(view, offset, string) {
    for (let i = 0; i < string.length; i++) {
        view.setUint8(offset + i, string.charCodeAt(i));
    }
}

function encodeWAV(samples, sampleRate) {
    const buffer = new ArrayBuffer(44 + samples.length * 2);
    const view = new DataView(buffer);

    /* RIFF identifier */
    writeString(view, 0, 'RIFF');
    /* file length */
    view.setUint32(4, 36 + samples.length * 2, true);
    /* RIFF type */
    writeString(view, 8, 'WAVE');
    /* format chunk identifier */
    writeString(view, 12, 'fmt ');
    /* format chunk length */
    view.setUint32(16, 16, true);
    /* sample format (raw) */
    view.setUint16(20, 1, true);
    /* channel count */
    view.setUint16(22, 1, true);
    /* sample rate */
    view.setUint32(24, sampleRate, true);
    /* byte rate (sample rate * block align) */
    view.setUint32(28, sampleRate * 2, true);
    /* block align (channel count * bytes per sample) */
    view.setUint16(32, 2, true);
    /* bits per sample */
    view.setUint16(34, 16, true);
    /* data chunk identifier */
    writeString(view, 36, 'data');
    /* data chunk length */
    view.setUint32(40, samples.length * 2, true);

    floatTo16BitPCM(view, 44, samples);

    return view;
}

function floatTo16BitPCM(output, offset, input) {
    for (let i = 0; i < input.length; i++, offset += 2) {
        let s = Math.max(-1, Math.min(1, input[i]));
        s = s < 0 ? s * 0x8000 : s * 0x7FFF;
        output.setInt16(offset, s, true);
    }
}

function flattenArray(channelBuffer, recordingLength) {
    const result = new Float32Array(recordingLength);
    let offset = 0;
    for (let i = 0; i < channelBuffer.length; i++) {
        const buffer = channelBuffer[i];
        result.set(buffer, offset);
        offset += buffer.length;
    }
    return result;
}

// Global chunks
let leftChannel = [];
let recordingLength = 0;

async function startRecording() {
    leftChannel = [];
    recordingLength = 0;

    try {
        mediaStream = await navigator.mediaDevices.getUserMedia({ audio: true });
        audioContext = new (window.AudioContext || window.webkitAudioContext)();
        input = audioContext.createMediaStreamSource(mediaStream);

        // bufferSize: 2048, 4096, 8192, 16384
        const bufferSize = 2048;
        recorder = audioContext.createScriptProcessor(bufferSize, 1, 1);

        recorder.onaudioprocess = (e) => {
            if (!isRecording) return;
            const left = e.inputBuffer.getChannelData(0);
            leftChannel.push(new Float32Array(left));
            recordingLength += left.length;
        };

        input.connect(recorder);
        recorder.connect(audioContext.destination);

        isRecording = true;
        updateUIState(true);
        startTimer();

    } catch (err) {
        console.error("Error accessing microphone:", err);
        alert("Could not access microphone.");
    }
}

function stopRecording() {
    isRecording = false;
    updateUIState(false);
    stopTimer();

    // Stop tracks
    if (mediaStream) {
        mediaStream.getTracks().forEach(track => track.stop());
    }
    if (audioContext) {
        // Suspend/Close to stop processing
        audioContext.close();
    }

    // Encode
    const flatData = flattenArray(leftChannel, recordingLength);
    const view = encodeWAV(flatData, audioContext ? audioContext.sampleRate : 44100);
    const blob = new Blob([view], { type: 'audio/wav' });

    // Send to server
    sendFile(blob, "recording.wav");
}

/* UI Logic */
recordBtn.addEventListener('click', () => {
    if (!isRecording) {
        startRecording();
    } else {
        stopRecording();
    }
});

uploadClickTarget.addEventListener('click', () => {
    audioInput.click();
});

audioInput.addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (file) {
        fileName.textContent = file.name;
        sendFile(file, file.name);
    }
});

function updateUIState(recording) {
    if (recording) {
        recordBtn.classList.add('recording');
        recordText.textContent = "Stop Recording";
        visualizer.classList.remove('hidden');
        timer.classList.remove('hidden');
    } else {
        recordBtn.classList.remove('recording');
        recordText.textContent = "Start Recording";
        visualizer.classList.add('hidden');
    }
}

function startTimer() {
    let seconds = 0;
    timer.textContent = "00:00";
    timerInterval = setInterval(() => {
        seconds++;
        const m = Math.floor(seconds / 60).toString().padStart(2, '0');
        const s = (seconds % 60).toString().padStart(2, '0');
        timer.textContent = `${m}:${s}`;
    }, 1000);
}

function stopTimer() {
    clearInterval(timerInterval);
}

async function sendFile(blob, filename) {
    const formData = new FormData();
    formData.append("file", blob, filename);

    // Get selected language and duration
    const selectedLanguage = languageSelect.value;
    const maxDuration = parseInt(durationInput.value) * 60; // Convert to seconds
    formData.append("language", selectedLanguage);
    formData.append("duration", maxDuration);

    showLoader();

    // Clear previous if any, but keep loader
    const placeholder = transcriptionBox.querySelector('.placeholder-text');
    if (placeholder) placeholder.remove();
    // Don't clear content yet if we want to show loading on top? 
    // Actually simpler to clear:
    transcriptionBox.innerHTML = '';
    transcriptionBox.appendChild(loader);


    try {
        const response = await fetch(`/transcribe?language=${selectedLanguage}&duration=${maxDuration}`, {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (response.ok) {
            let displayText = data.transcript;
            if (data.detected_language) {
                displayText = `<p><small style="color: var(--accent-color); font-weight: 600;">Detected: ${data.detected_language}</small></p><p>${data.transcript}</p>`;
            }
            transcriptionBox.innerHTML = displayText;
        } else {
            transcriptionBox.innerHTML = `<p class="error" style="color: var(--error-color)">Error: ${data.error}</p>`;
        }
    } catch (err) {
        transcriptionBox.innerHTML = `<p class="error" style="color: var(--error-color)">Network Error: ${err.message}</p>`;
    } finally {
        hideLoader();
    }
}

function showLoader() {
    loader.classList.remove('hidden');
}

function hideLoader() {
    loader.classList.add('hidden');
}

copyBtn.addEventListener('click', () => {
    const text = transcriptionBox.innerText;
    if (text) {
        // If it starts with "Detected: ", remove it from the copy
        let cleanText = text;
        if (text.includes('Detected:')) {
            const lines = text.split('\n');
            cleanText = lines.slice(1).join('\n').trim();
        }
        navigator.clipboard.writeText(cleanText);
        const original = copyBtn.innerHTML;
        copyBtn.innerHTML = '<i class="fa-solid fa-check"></i>';
        setTimeout(() => copyBtn.innerHTML = original, 2000);
    }
});

copyTranslationBtn.addEventListener('click', () => {
    const text = translationOutput.innerText;
    if (text && text !== 'Transcribe audio first, then click translate...') {
        // If it shows "Language -> Language", try to get just the translation
        let cleanText = text;
        const lines = text.split('\n');
        if (lines.length > 1) {
            cleanText = lines.slice(1).join('\n').trim();
        }

        navigator.clipboard.writeText(cleanText);
        const original = copyTranslationBtn.innerHTML;
        copyTranslationBtn.innerHTML = '<i class="fa-solid fa-check"></i>';
        setTimeout(() => copyTranslationBtn.innerHTML = original, 2000);
    }
});

clearBtn.addEventListener('click', () => {
    transcriptionBox.innerHTML = '<p class="placeholder-text">Press record or upload a file to begin...</p>';
    translationOutput.innerHTML = '<p class="placeholder-text">Transcribe audio first, then click translate...</p>';
    fileName.textContent = '';
    audioInput.value = '';
});

// Translation functionality
translateBtn.addEventListener('click', async () => {
    const transcriptText = transcriptionBox.innerText.trim();

    // Remove "Detected: ..." prefix if present
    let cleanText = transcriptText;
    if (transcriptText.includes('Detected:')) {
        const lines = transcriptText.split('\n');
        cleanText = lines.slice(1).join('\n').trim();
    }

    if (!cleanText || cleanText === 'Press record or upload a file to begin...') {
        translationOutput.innerHTML = '<p class="error" style="color: var(--error-color)">Please transcribe audio first!</p>';
        return;
    }

    const sourceLang = translateFrom.value;
    const targetLang = translateTo.value;

    if (sourceLang !== 'auto' && sourceLang === targetLang) {
        translationOutput.innerHTML = '<p class="error" style="color: var(--error-color)">Source and target languages cannot be the same!</p>';
        return;
    }

    // Show loading state
    translateBtn.disabled = true;
    translateBtn.innerHTML = '<div class="icon-wrapper"><i class="fa-solid fa-spinner fa-spin"></i></div><span>Translating...</span>';

    try {
        const response = await fetch('/translate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                text: cleanText,
                source_language: sourceLang,
                target_language: targetLang
            })
        });

        const data = await response.json();

        if (response.ok) {
            translationOutput.innerHTML = `
                <div class="translation-result">
                    <p><small style="color: var(--accent-color); font-weight: 600;">
                        ${data.source_language} → ${data.target_language}
                    </small></p>
                    <p style="font-size: 1.1rem; margin-top: 0.5rem;">${data.translated_text}</p>
                </div>
            `;
        } else {
            translationOutput.innerHTML = `<p class="error" style="color: var(--error-color)">Error: ${data.error}</p>`;
        }
    } catch (err) {
        let errorMsg = err.message;
        if (errorMsg.includes('timed out')) {
            errorMsg = "Translation server took too long to respond. Please try again in a few seconds.";
        }
        translationOutput.innerHTML = `<p class="error" style="color: var(--error-color)">Translation failed: ${errorMsg}</p>`;
    } finally {
        // Reset button
        translateBtn.disabled = false;
        translateBtn.innerHTML = '<div class="icon-wrapper"><i class="fa-solid fa-language"></i></div><span>Translate</span>';
    }
});
