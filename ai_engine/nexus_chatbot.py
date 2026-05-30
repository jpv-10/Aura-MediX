from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


class AIMedicalDoctor:

    def generate_response(self, user_message):

        # =========================
        # 🚫 STEP 1: BLOCK NON-MEDICAL QUESTIONS
        # =========================
        msg = user_message.lower()

        non_medical = [
            "joke", "movie", "code", "python", "music",
            "cricket", "football", "game", "story", "news",
            "politics", "actor", "song", "comedy"
        ]

        if any(word in msg for word in non_medical):
            return {
                "message": "I am a medical AI assistant and can only answer health-related questions.",
                "type": "blocked",
                "requires_human": False
            }

        # =========================
        # 🧠 STEP 2: SYSTEM PROMPT
        # =========================
        SYSTEM_PROMPT = """
You are AURA MEDIX AI Doctor.

STRICT RULES:
- You ONLY answer medical/health-related questions.
- If user asks non-medical questions, say you cannot answer.
- Do NOT provide coding, jokes, entertainment, or general knowledge.
- Be safe, simple, and professional.
"""

        try:
            # =========================
            # 🤖 STEP 3: GROQ CALL
            # =========================
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_message}
                ]
            )

            return {
                "message": response.choices[0].message.content,
                "type": "ai",
                "requires_human": False
            }

        except Exception as e:
            return {
                "message": f"AI Error: {str(e)}",
                "type": "error",
                "requires_human": False
            }


ai_doctor = AIMedicalDoctor()