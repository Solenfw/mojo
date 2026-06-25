# server/app/services/vision_service.py
import os
import json
import urllib.request
import urllib.error
from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env file

class VisionService:
    def __init__(self):
        self.gemini_key = os.getenv("GEMINI_API_KEY")

    def evaluate_kanji(self, base64_image: str, target_kanji: str) -> dict:
        """Analyzes a handwritten Kanji image using Gemini Vision."""
        if not self.gemini_key:
            # Fallback mock for local testing without API key
            return {
                "score": 85,
                "feedback": f"Good attempt at '{target_kanji}'. The balance is decent, but ensure your horizontal strokes are slightly angled upwards."
            }

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={self.gemini_key}"
        
        prompt = f"""
        You are a strict but encouraging Japanese calligraphy (Shodo) teacher.
        Evaluate the user's handwritten attempt at the Kanji '{target_kanji}'.
        
        Focus on:
        1. Correct stroke presence.
        2. Overall balance and proportion.
        3. Readability.
        
        Provide your assessment as raw JSON in this exact format:
        {{
            "score": <int 0-100>,
            "feedback": "<concise analytical assessment under 3 sentences>"
        }}
        """

        headers = {"Content-Type": "application/json"}
        data = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt},
                        {
                            "inlineData": {
                                "mimeType": "image/png",
                                "data": base64_image
                            }
                        }
                    ]
                }
            ]
        }
        
        req = urllib.request.Request(url, data=json.dumps(data).encode("utf-8"), headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req) as response:
                res_body = json.loads(response.read().decode("utf-8"))
                raw_text = res_body["candidates"][0]["content"]["parts"][0]["text"]
                cleaned = raw_text.strip().strip("```json").strip("```").strip()
                return json.loads(cleaned)
        except urllib.error.HTTPError as e:
            err_content = e.read().decode("utf-8")
            raise RuntimeError(f"Vision API Call failed: {e.code} - {err_content}")
        except Exception as e:
            return {
                "score": 70,
                "feedback": f"Could not fully analyze image due to a network error: {str(e)[:50]}. Keep practicing!"
            }