import openai
from app.core.config import settings


class GPTService:
    def __init__(self):
        openai.api_key = settings.OPENAI_API_KEY

    async def explain_grammar(self, sentence: str, context: str) -> str:
        """
        Uses OpenAI to explain Japanese grammar concisely.
        """
        prompt = f"""
        Explain the grammatical structure of the following Japanese sentence concisely.
        Sentence: {sentence}
        Context: {context}
        Provide a brief explanation in English.
        """

        response = await openai.ChatCompletion.acreate(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200,
            temperature=0.5,
        )
        return response.choices[0].message.content.strip()
