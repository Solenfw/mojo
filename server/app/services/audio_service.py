import os
import json
import urllib.request
import urllib.error

class AudioService:
    def __init__(self):
        self.gemini_key = os.getenv("GEMINI_API_KEY")
        self.openai_key = os.getenv("OPENAI_API_KEY")

    def _call_gemini_rest(self, prompt: str, schema_prompt: str = "") -> str:
        """Helper to invoke Gemini API over standard HTTP without external package dependencies."""
        if not self.gemini_key:
            raise ValueError("GEMINI_API_KEY environment variable is not set.")
        
        full_prompt = f"{prompt}\n\n{schema_prompt}" if schema_prompt else prompt
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={self.gemini_key}"
        
        headers = {"Content-Type": "application/json"}
        data = {
            "contents": [
                {
                    "parts": [{"text": full_prompt}]
                }
            ]
        }
        
        req = urllib.request.Request(url, data=json.dumps(data).encode("utf-8"), headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req) as response:
                res_body = json.loads(response.read().decode("utf-8"))
                return res_body["candidates"][0]["content"]["parts"][0]["text"]
        except urllib.error.HTTPError as e:
            err_content = e.read().decode("utf-8")
            raise RuntimeError(f"Gemini API Call failed: {e.code} - {err_content}")
        except Exception as e:
            raise RuntimeError(f"Failed calling Gemini: {str(e)}")

    def _call_openai_rest(self, prompt: str) -> str:
        """Helper to invoke OpenAI API over standard HTTP as an alternative fallback."""
        if not self.openai_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set.")
            
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.openai_key}"
        }
        data = {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3
        }
        
        req = urllib.request.Request(url, data=json.dumps(data).encode("utf-8"), headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req) as response:
                res_body = json.loads(response.read().decode("utf-8"))
                return res_body["choices"][0]["message"]["content"]
        except Exception as e:
            raise RuntimeError(f"Failed calling OpenAI: {str(e)}")

    def evaluate_pronunciation(self, transcript: str, expected_text: str) -> dict:
        """Analyzes Japanese speaking attempt compared to the expected sentence."""
        prompt = f"""
        You are an expert Japanese speech coach. Analyze the student's spoken transcript compared to the expected sentence.
        
        Expected Japanese Sentence: "{expected_text}"
        Student Spoken Transcript: "{transcript}"
        
        Evaluate spelling, word accuracy, and typical pronunciation issues.
        Provide your assessment as raw JSON.
        JSON format:
        {{
            "accuracy_score": <int 0-100>,
            "fluency_score": <int 0-100>,
            "feedback": "<concise analytical assessment under 3 sentences>",
            "tips": ["<specific pronunciation tip 1>", "<specific pronunciation tip 2>"]
        }}
        """
        
        try:
            if self.gemini_key:
                raw_response = self._call_gemini_rest(prompt, "Return ONLY valid JSON matching the schema.")
            elif self.openai_key:
                raw_response = self._call_openai_rest(prompt)
            else:
                # Mock evaluation fallback if credentials are unset during offline demo testing
                return {
                    "accuracy_score": 85,
                    "fluency_score": 80,
                    "feedback": "Clear reading overall. Watch the vowel length in your target words.",
                    "tips": ["Extend the vowel sound slightly longer", "Keep natural pauses between grammar particles"]
                }
            
            # Clean possible markdown wrap (```json ... ```)
            cleaned = raw_response.strip().strip("```json").strip("```").strip()
            return json.loads(cleaned)
        except Exception as e:
            # Safe default fallback
            return {
                "accuracy_score": 75,
                "fluency_score": 75,
                "feedback": f"Evaluation processed with a localized error: {str(e)[:100]}",
                "tips": ["Read slowly and clearly", "Ensure the microphone is close"]
            }

    def generate_kaiwa_response(self, conversation_history: list) -> dict:
        """Generates the next logical clerk or customer turn in a Kaiwa roleplay scenario."""
        # Convert history format for prompt
        formatted_history = "\n".join([f"{msg['role']}: {msg['content']}" for msg in conversation_history[-5:]])
        
        prompt = f"""
        You are playing the role of a Japanese speaker in a dialog scenario.
        Respond to the user naturally while keeping grammar at a beginner/intermediate level.
        
        Recent Dialog History:
        {formatted_history}
        
        Formulate your reply.
        Return ONLY valid JSON formatted as:
        {{
            "content": "<Japanese response, kanji with standard spacing>",
            "romaji": "<corresponding romaji transcription>",
            "translation": "<English translation>"
        }}
        """
        
        try:
            if self.gemini_key:
                raw_response = self._call_gemini_rest(prompt, "Return ONLY valid JSON.")
            elif self.openai_key:
                raw_response = self._call_openai_rest(prompt)
            else:
                # Default mock flow
                return {
                    "content": "かしこまりました。お会計は八百円になります。",
                    "romaji": "Kashikomarimashita. O-kaikei wa happyaku-en ni narimasu.",
                    "translation": "Understood. The total comes to 800 yen."
                }
            
            cleaned = raw_response.strip().strip("```json").strip("```").strip()
            return json.loads(cleaned)
        except Exception:
            return {
                "content": "はい、少々お待ちください。",
                "romaji": "Hai, shou-shou omachi kudasai.",
                "translation": "Certainly, please wait a moment."
            }