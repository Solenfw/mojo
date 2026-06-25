import json
import os
import urllib.error
import urllib.request


class AudioService:
    DEFAULT_PRONUNCIATION_RESULT = {
        "accuracy_score": 75,
        "fluency_score": 75,
        "score": 75,
        "feedback": "Không thể phân tích phát âm.",
        "tips": [
            "Hãy thử đọc lại chậm và rõ ràng hơn",
            "Đảm bảo micro được đặt gần miệng",
        ],
        "is_correct": True,
    }

    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.model = "gemini-2.5-flash"

    # ==========================================================
    # Core Gemini Client
    # ==========================================================

    def _generate(self, prompt: str) -> str:
        if not self.api_key:
            raise RuntimeError("GEMINI_API_KEY not configured")

        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"{self.model}:generateContent?key={self.api_key}"
        )

        payload = {
            "contents": [
                {
                    "parts": [{"text": prompt}]
                }
            ]
        }

        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urllib.request.urlopen(req) as res:
                body = json.loads(res.read().decode())
                return body["candidates"][0]["content"]["parts"][0]["text"]

        except urllib.error.HTTPError as e:
            error_body = e.read().decode()
            raise RuntimeError(f"Gemini error {e.code}: {error_body}")

    @staticmethod
    def _parse_json(response: str) -> dict:
        cleaned = (
            response.replace("```json", "")
            .replace("```", "")
            .strip()
        )
        return json.loads(cleaned)

    # ==========================================================
    # Pronunciation Evaluation
    # ==========================================================

    def evaluate_pronunciation(
        self,
        transcript: str,
        expected_text: str,
        romaji: str = "",
    ) -> dict:

        if not self.api_key:
            return {
                "accuracy_score": 85,
                "fluency_score": 80,
                "score": 83,
                "feedback": "Phát âm khá rõ ràng. Hãy chú ý các trường âm dài.",
                "tips": [
                    "Kéo dài nguyên âm đúng nhịp",
                    "Giữ nhịp điệu tự nhiên",
                ],
                "is_correct": True,
            }

        prompt = f"""
            You are a Japanese pronunciation coach.

            Expected sentence:
            {expected_text}

            Romaji:
            {romaji}

            Student transcript:
            {transcript}

            Return ONLY valid JSON:

            {{
                "accuracy_score": 0-100,
                "fluency_score": 0-100,
                "score": 0-100,
                "feedback": "Vietnamese feedback",
                "tips": ["tip1", "tip2"],
                "is_correct": true
            }}
            """

        try:
            response = self._generate(prompt)
            return self._parse_json(response)

        except Exception as e:
            result = self.DEFAULT_PRONUNCIATION_RESULT.copy()
            result["feedback"] = f"Lỗi phân tích: {str(e)[:100]}"
            return result

    # ==========================================================
    # Kaiwa Conversation
    # ==========================================================

    def generate_kaiwa_response(self, history: list) -> dict:

        if not self.api_key:
            return {
                "content": "かしこまりました。お会計は八百円になります。",
                "romaji": "Kashikomarimashita. O-kaikei wa happyaku-en ni narimasu.",
                "translation": "Understood. The total comes to 800 yen."
            }

        dialog = "\n".join(
            f"{msg['role']}: {msg['content']}"
            for msg in history[-5:]
        )

        prompt = f"""
            You are a Japanese conversation partner.

            Recent conversation:
            {dialog}

            Return ONLY valid JSON:

            {{
                "content": "Japanese response",
                "romaji": "Romaji",
                "translation": "English translation"
            }}
            """

        try:
            response = self._generate(prompt)
            return self._parse_json(response)

        except Exception:
            return {
                "content": "はい、少々お待ちください。",
                "romaji": "Hai, shoushou omachi kudasai.",
                "translation": "Certainly, please wait a moment."
            }