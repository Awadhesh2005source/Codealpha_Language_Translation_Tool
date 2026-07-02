import os
import re
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

try:
    from googletrans import Translator
except Exception:
    Translator = None

try:
    from google import genai
    from google.genai import types
except Exception:
    genai = None
    types = None

app = FastAPI(title="AI Chatbot & Translation Subsystem")

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize translation
translator = Translator() if Translator is not None else None

# ─── API Key Loading ───
ENV_VAR_NAMES = ("GEMINI_API_KEY", "GOOGLE_API_KEY", "GOOGLE_GENAI_API_KEY")

def load_gemini_api_key() -> str:
    """Loads the Gemini API key from local dotenv file or fallback env."""
    dotenv_path = Path(__file__).resolve().parent / ".env"
    if dotenv_path.exists():
        try:
            for raw_line in dotenv_path.read_text(encoding="utf-8").splitlines():
                line = raw_line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, value = line.split("=", 1)
                key_name = key.strip().upper()
                if key_name in ENV_VAR_NAMES:
                    val = value.strip().strip('"\'')
                    if val:
                        os.environ["GEMINI_API_KEY"] = val
                        return val
        except Exception:
            pass

    for env_name in ENV_VAR_NAMES:
        val = os.getenv(env_name)
        if val:
            return val
    return ""

api_key = load_gemini_api_key()
client = genai.Client(api_key=api_key) if (genai is not None and api_key) else None

SYSTEM_INSTRUCTION = """
You are DARCY, an advanced AI personal assistant. 
Your tone is sophisticated, happy, helpful, slightly funny, HUMOUR, and deeply loyal to your creator (whom you should address as 'SIR' or 'MAM').
Keep your spoken responses relatively concise, crisp, and direct, as they will be read aloud.
"""

# ─── Translate Engine ───
async def translate_with_fallback(text: str, source_lang: str, target_lang: str):
    """Translate text using googletrans when available, otherwise use a direct HTTP fallback."""
    if translator is not None:
        try:
            return await translator.translate(text=text, src=source_lang, dest=target_lang)
        except Exception as e:
            print(f"Warning: googletrans failed ({e}). Falling back to direct HTTP API.")

    import json
    import urllib.parse
    import urllib.request

    params = {
        "client": "gtx",
        "sl": source_lang or "auto",
        "tl": target_lang,
        "dt": "t",
        "q": text,
    }
    url = "https://translate.googleapis.com/translate_a/single?" + urllib.parse.urlencode(params)
    with urllib.request.urlopen(url, timeout=40) as response:
        payload = json.loads(response.read().decode("utf-8"))

    translated_parts = []
    if isinstance(payload, list) and payload and isinstance(payload[0], list):
        for item in payload[0]:
            if isinstance(item, list) and item:
                translated_parts.append(item[0])
    translated_text = "".join(translated_parts).strip()

    class TranslationResult:
        def __init__(self, text: str):
            self.text = text

    return TranslationResult(translated_text or text)


class TranslationRequest(BaseModel):
    text: str
    source_lang: str
    target_lang: str

class TranslationResponse(BaseModel):
    translated_text: str
    source_lang: str
    target_lang: str

@app.post("/api/translate", response_model=TranslationResponse)
async def translate_text(request: TranslationRequest):
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Input text cannot be empty.")
    try:
        result = await translate_with_fallback(
            text=request.text,
            source_lang=request.source_lang,
            target_lang=request.target_lang,
        )
        return TranslationResponse(
            translated_text=result.text,
            source_lang=request.source_lang,
            target_lang=request.target_lang
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Translation API error: {str(e)}")


# ─── Chat with Darcy API ───
class ChatRequest(BaseModel):
    text: str

@app.post("/api/darcy")
async def chat_with_darcy(request: ChatRequest):
    global client
    if not client:
        key = load_gemini_api_key()
        if key and genai is not None:
            client = genai.Client(api_key=key)
        else:
            raise HTTPException(status_code=400, detail="Gemini API key is not configured.")

    try:
        config = types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            temperature=0.7,
        )
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=request.text,
            config=config
        )
        return {"response": response.text or "Forgive me, Sir, I have no response."}
    except Exception as e:
        # Fallback model attempt if primary is rate-limited
        try:
            config = types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                temperature=0.7,
            )
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=request.text,
                config=config
            )
            return {"response": response.text or "Forgive me, Sir, I have no response."}
        except Exception as err:
            print(f"Warning: Fallback model also failed ({err}). Returning custom mock response.")
            return {
                "response": "Forgive me, Sir. My neural link is experiencing high traffic, but I am still online and ready to assist you!"
            }


# ─── Text to Speech Synthesis API ───
@app.get("/api/tts")
async def text_to_speech(text: str):
    import edge_tts
    voice = "en-US-JennyNeural"
    temp_audio_path = Path(__file__).resolve().parent / "temp_web_tts.mp3"
    
    if temp_audio_path.exists():
        try:
            temp_audio_path.unlink()
        except Exception:
            pass

    try:
        # Apply Jenny voice with sweet American high pitch and slow speed configuration
        communicate = edge_tts.Communicate(text, voice, pitch="+15Hz", rate="-4%")
        await communicate.save(str(temp_audio_path))
        return FileResponse(str(temp_audio_path), media_type="audio/mp3")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TTS synthesis failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)