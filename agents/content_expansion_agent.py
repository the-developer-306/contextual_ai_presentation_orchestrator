import os
import json
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

class ContentExpansionAgent:
    def __init__(self):
        # Load Groq API key
        groq_api_key = os.getenv("GROQ_API_KEY")
        if not groq_api_key:
            raise ValueError(" Missing GROQ_API_KEY in .env file")

        # Use Groq LLM directly
        self.llm = ChatGroq(
            groq_api_key=groq_api_key,
            model="llama-3.1-8b-instant",
            temperature=0.3,
            max_tokens=1200
        )

    def expand_outline(self, outline_json: dict):
        """
        Expands bullet points into concise statements (≤ 20 words each).
        Processes slide by slide to avoid token limit issues.
        """
        expanded_slides = []

        for slide in outline_json["slides"]:
            slide_title = slide["title"]
            bullet_points = slide["bullet_points"]

            # Construct a minimal, deterministic prompt
            prompt = f"""
                        You are an API that outputs ONLY valid JSON.
                        Do NOT add explanations, reasoning, <think> tags, or commentary.

                        For the given slide, expand EACH bullet point into a concise yet **informative** statement.
                        Treat every bullet point as a **mini-topic** and add relevant details, context, or implications.
                        Make each expanded statement **engaging, clear, and insightful** but limit it to a **maximum of 30 words**.

                        ### JSON format to return:
                        {{
                            "title": "{slide_title}",
                            "detailed_points": [
                                "Expanded statement for bullet 1",
                                "Expanded statement for bullet 2"
                            ]
                        }}

                        Slide to expand:
                        {{
                            "title": "{slide_title}",
                            "bullet_points": {json.dumps(bullet_points)}
                        }}
                    """


            try:
                # Directly call Groq LLM
                response = self.llm.invoke(prompt)
                text_response = response.content.strip()

                # Ensure valid JSON parsing
                expanded_slide = json.loads(text_response)
                expanded_slides.append(expanded_slide)

            except json.JSONDecodeError:
                print(f" JSON parse failed for slide: {slide_title}")
                expanded_slides.append({
                    "title": slide_title,
                    "detailed_points": [" Expansion failed, please retry."]
                })
            except Exception as e:
                print(f" LLM request failed for {slide_title}: {e}")
                expanded_slides.append({
                    "title": slide_title,
                    "detailed_points": [" Expansion failed, please retry."]
                })

        return {"slides": expanded_slides}
