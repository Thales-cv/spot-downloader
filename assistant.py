from openai import OpenAI
from config import Config


class AIAssistant:
    def __init__(self):
        self.enabled = bool(Config.OPENAI_API_KEY)
        self.client = OpenAI(api_key=Config.OPENAI_API_KEY) if self.enabled else None
        self.history = []

    def add_event(self, role, content):
        # Keep a short rolling context
        self.history.append({"role": role, "content": content})
        if len(self.history) > 30:
            self.history = self.history[-30:]

    def initial_message(self):
        msg = "Cole aqui a sua playlist do spotfy"
        self.add_event("assistant", msg)
        return msg

    def ask_storage_mode(self, total_songs=None):
        if total_songs is None:
            base_msg = (
                "Como você quer armazenar as músicas? "
                "Opções: separar por pasta de gênero ou por momentos do SET."
            )
        else:
            base_msg = (
                f"Encontrei {total_songs} músicas. "
                "Como você quer armazenar as músicas? "
                "Opções: separar por pasta de gênero ou por momentos do SET."
            )

        if not self.enabled:
            msg = base_msg
            self.add_event("assistant", msg)
            return msg

        try:
            prompt = (
                "Você é uma assistente de DJ que organiza músicas para um set. "
                f"{'Foram encontradas ' + str(total_songs) + ' faixas. ' if total_songs is not None else ''}"
                "Pergunte ao usuário como deseja armazenar as músicas. "
                "As opções devem ser: separar por pasta de gênero ou por momentos do SET. "
                "Responda de forma curta e objetiva."
            )
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Você é uma assistente de DJ objetiva."},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=60,
                temperature=0.3,
            )
            msg = response.choices[0].message.content.strip()
            self.add_event("assistant", msg)
            return msg
        except Exception:
            msg = base_msg
            self.add_event("assistant", msg)
            return msg

    def user_message(self, text):
        self.add_event("user", text)

    def respond(self, text):
        self.add_event("user", text)
        if not self.enabled:
            msg = "Posso ajudar a organizar seu set: cole a playlist e escolha o tipo de organização."
            self.add_event("assistant", msg)
            return msg

        try:
            messages = [{"role": "system", "content": "Você é uma assistente de DJ objetiva."}]
            messages.extend(self.history)
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=120,
                temperature=0.4,
            )
            msg = response.choices[0].message.content.strip()
            self.add_event("assistant", msg)
            return msg
        except Exception:
            msg = "Tive um problema para responder agora. Tente novamente."
            self.add_event("assistant", msg)
            return msg
