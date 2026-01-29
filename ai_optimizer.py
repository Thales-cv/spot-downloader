from openai import OpenAI
from config import Config
import logging

class AIOptimizer:
    def __init__(self):
        if Config.OPENAI_API_KEY:
            self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
            self.enabled = True
        else:
            self.client = None
            self.enabled = False
            
    def refine_search_query(self, artist, title):
        """
        Asks ChatGPT for the best search query to find the official audio
        or a clean lyric video, avoiding long music video intros.
        """
        if not self.enabled:
            return f"{artist} - {title}"

        try:
            prompt = (
                f"I am a DJ downloading songs. I specifically want the 'Extended Mix' or 'Club Mix' if it exists. "
                f"If not, I want the cleanest original audio (Official Audio/Lyric Video). \n"
                f"The song is: '{artist} - {title}'. \n"
                f"Ignore shortness. Ignore official music videos with movie-like intros. \n"
                f"Return ONLY the best YouTube search query. Example: '{artist} - {title} Extended Mix'. "
                f"Do not explain."
            )

            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful DJ assistant. Output only the best search query."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=20,
                temperature=0.3,
            )
            
            refined_query = response.choices[0].message.content.strip()
            # Remove quotes if chatgpt added them
            refined_query = refined_query.strip('"').strip("'")
            return refined_query

        except Exception as e:
            logging.error(f"AI Error: {e}")
            return f"{artist} - {title}"
            
    def validate_match(self, song_name, found_title):
        """
        Ask AI if the found YouTube title looks like a bad match (e.g. live version, cover, etc)
        when we wanted the original.
        """
        if not self.enabled:
            return True # Assume it's fine
            
        try:
            prompt = (
                f"I am looking for the original audio of '{song_name}'. \n"
                f"I found a video titled: '{found_title}'. \n"
                f"Is this likely a good match for the studio audio? \n"
                f"If it says 'Live', 'Cover', 'Reaction', 'Teaser', or 'Preview', say NO. \n"
                f"Otherwise say YES. Answer with only YES or NO."
            )
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=5,
                temperature=0.0,
            )
            
            answer = response.choices[0].message.content.strip().upper()
            return "YES" in answer

        except Exception as e:
            logging.error(f"AI Verification Error: {e}")
            return True

    def detect_genre(self, artist, title):
        """
        Asks ChatGPT to categorize the song into a broad electronic genre.
        """
        if not self.enabled:
            return "Unsorted"

    def detect_set_moment(self, artist, title):
        """
        Classifica a faixa em um momento do set.
        """
        if not self.enabled:
            return "Set"

        try:
            prompt = (
                f"Classifique a faixa '{artist} - {title}' em UM destes momentos do set: "
                "Warmup, Build-up, Peak Time, Breakdown, Closing, Other. "
                "Retorne SOMENTE o nome do momento."
            )

            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=5,
                temperature=0.0,
            )

            moment = response.choices[0].message.content.strip().title()
            valid = ["Warmup", "Build-Up", "Peak Time", "Breakdown", "Closing", "Other"]

            # Normalize "Build-up"
            if moment == "Build-Up":
                moment = "Build-up"

            if moment not in ["Warmup", "Build-up", "Peak Time", "Breakdown", "Closing", "Other"]:
                return "Other"
            return moment

        except Exception as e:
            logging.error(f"AI Set Moment Error: {e}")
            return "Set"
        try:
            prompt = (
                f"Categorize the song '{artist} - {title}' into ONE of these genres: "
                f"House, Tech House, Melodic, Techno, Deep House, Funk, Trance, Drum & Bass, Pop, Other. \n"
                f"Return ONLY the genre name. If unsure, say 'Unsorted'."
            )
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=5,
                temperature=0.0,
            )
            
            genre = response.choices[0].message.content.strip().title()
            valid_genres = ["House", "Tech House", "Melodic", "Techno", "Deep House", "Funk", "Trance", "Drum & Bass", "Pop"]
            
            if genre not in valid_genres:
                return "Other"
            return genre

        except Exception as e:
            logging.error(f"AI Genre Error: {e}")
            return "Unsorted"
