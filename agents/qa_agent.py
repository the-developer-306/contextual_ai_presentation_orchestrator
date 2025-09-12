import os
import json
from dotenv import load_dotenv
from langchain.agents import AgentExecutor, Tool, create_json_chat_agent
from langchain.memory import ConversationBufferWindowMemory
from langchain import hub
from langchain_groq import ChatGroq
from rag_pipeline.pipeline import RAGPipeline

load_dotenv()

class QAAgent:
    def __init__(self, persist_directory="vector_db"):
        groq_api_key = os.getenv("GROQ_API_KEY")
        if not groq_api_key:
            raise ValueError(" Missing GROQ_API_KEY in .env file")

        # Load RAG pipeline
        self.rag = RAGPipeline(persist_directory=persist_directory).load()
        self.retriever = self.rag.retriever

        # Groq LLM for strict JSON QA
        self.llm = ChatGroq(
            groq_api_key=groq_api_key,
            model="llama-3.1-8b-instant",
            temperature=0,
            max_tokens=1200
        )

        # Conversation memory
        self.memory = ConversationBufferWindowMemory(k=3)

        # Context retriever tool with fewer chunks
        self.tools = [
            Tool(
                name="ContextRetriever",
                func=self.retrieve_context,
                description="Fetch at most 2 short relevant context chunks for verifying facts"
            )
        ]

        # Strict JSON template
        self.prompt = hub.pull("hwchase17/react-chat-json")

        # JSON-only agent
        self.agent = create_json_chat_agent(self.llm, self.tools, self.prompt)

        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=True
        )

    def retrieve_context(self, query):
        """Fetch top-2 relevant chunks from the vector DB"""
        results = self.retriever.get_relevant_documents(query)
        return "\n\n".join([doc.page_content for doc in results[:2]])

    def _try_parse_json(self, raw_output, slide_title):
        """Attempt JSON parsing, fallback if failed"""
        if isinstance(raw_output, dict):
            return raw_output
        try:
            return json.loads(raw_output)
        except json.JSONDecodeError:
            print(f" JSON parsing failed for slide: {slide_title}")
            return {
                "title": slide_title,
                "validation": [
                    {
                        "point": " Validation failed",
                        "status": "needs_review",
                        "reason": "Could not parse model response."
                    }
                ]
            }

    def validate_content(self, expanded_json: dict):
        """
        Validates the expanded slide content against retrieved knowledge base.
        Returns JSON with per-slide verification results.
        """
        validated_slides = []

        for slide in expanded_json["slides"]:
            slide_title = slide["title"]
            detailed_points = slide["detailed_points"]

            # Strict JSON-only prompt
            prompt = f"""
            You are an API that outputs ONLY valid JSON.
            Do NOT add explanations, <think> tags, or commentary.

            Validate EACH statement in the given slide using available context.
            If context is insufficient, mark as "needs_review".

            ### JSON format to return:
            {{
                "title": "{slide_title}",
                "validation": [
                    {{
                        "point": "Expanded statement",
                        "status": "accurate" | "needs_review",
                        "reason": "Why it needs review (if applicable)"
                    }}
                ]
            }}

            Slide to validate:
            {{
                "title": "{slide_title}",
                "detailed_points": {json.dumps(detailed_points)}
            }}
            """

            # Run agent
            result = self.agent_executor.invoke({"input": prompt})
            raw_output = result.get("output") or result.get("response") or result

            # Try parsing JSON safely
            validated_slides.append(self._try_parse_json(raw_output, slide_title))

        return {"slides": validated_slides}
