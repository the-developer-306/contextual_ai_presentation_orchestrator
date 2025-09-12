import os
import json
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

class FormatOptimizerAgent:
    def __init__(self):
        # Load Groq API key
        groq_api_key = os.getenv("GROQ_API_KEY")
        if not groq_api_key:
            raise ValueError(" Missing GROQ_API_KEY in .env file")

        # Use deterministic JSON-friendly LLM
        self.llm = ChatGroq(
            groq_api_key=groq_api_key,
            model="llama-3.1-8b-instant",
            temperature=0,
            max_tokens=2500
        )

    def optimize_format(self, expanded_json: dict, validated_json: dict, batch_size: int = 5):
        """
        Combines expanded + validated content into a final PPT-ready JSON.
        Now processes slides in batches to avoid exceeding token limits.
        """
        all_slides = []
        slides = expanded_json["slides"]
        validated_slides = validated_json["slides"]

        for i in range(0, len(slides), batch_size):
            # Slice slides for the current batch
            batch_expanded = {"slides": slides[i:i + batch_size]}
            batch_validated = {"slides": validated_slides[i:i + batch_size]}

            prompt = f"""
            You are an API that outputs ONLY valid JSON.
            Do NOT include explanations, reasoning, or <think> tags.
            Do NOT output anything before or after the JSON.

            Combine the expanded content and QA validation results into a **final PPT-ready JSON**.

            Rules:
            - Preserve slide titles.
            - For each expanded statement:
                - If QA marked it as "accurate", include it under "status": "accurate".
                - If QA marked it as "needs_review", include it but flag as "status": "needs_review".
            - Include for each point:
                - "statement" → final verified or review-needed text
                - "status" → "accurate" or "needs_review"
                - "design_hint" → minimal suggestion to make the slide visually appealing.

            ### STRICT JSON FORMAT:
            {{
                "slides": [
                    {{
                        "title": "Slide title",
                        "content": [
                            {{
                                "statement": "Final verified statement or needs-review statement",
                                "status": "accurate or needs_review",
                                "design_hint": "Suggested minimal visual styling"
                            }}
                        ]
                    }}
                ]
            }}

            Expanded content:
            {json.dumps(batch_expanded)}

            QA validation results:
            {json.dumps(batch_validated)}
            """

            try:
                response = self.llm.invoke(prompt)
                text_response = response.content.strip()
                batch_result = json.loads(text_response)
                all_slides.extend(batch_result["slides"])

            except json.JSONDecodeError:
                print(f" JSON parsing failed in FormatOptimizerAgent for slides {i} - {i+batch_size}")
                all_slides.extend([
                    {
                        "title": s["title"],
                        "content": [{
                            "statement": " Formatting failed for this slide",
                            "status": "needs_review",
                            "design_hint": "Manual design needed"
                        }]
                    }
                    for s in batch_expanded["slides"]
                ])
            except Exception as e:
                print(f" LLM request failed for slides {i} - {i+batch_size}: {e}")
                all_slides.extend([
                    {
                        "title": s["title"],
                        "content": [{
                            "statement": " Optimization failed",
                            "status": "needs_review",
                            "design_hint": "Manual formatting required"
                        }]
                    }
                    for s in batch_expanded["slides"]
                ])

        # Build final JSON summary
        accurate_count = sum(
            1 for slide in all_slides for point in slide["content"] if point["status"] == "accurate"
        )
        needs_review_count = sum(
            1 for slide in all_slides for point in slide["content"] if point["status"] == "needs_review"
        )

        return {
            "slides": all_slides,
            "summary": f"{accurate_count} statements accurate, {needs_review_count} statements need manual review"
        }
