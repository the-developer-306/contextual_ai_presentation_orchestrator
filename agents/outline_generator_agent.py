import os
import json
from dotenv import load_dotenv
from langchain.agents import AgentExecutor, Tool, create_json_chat_agent
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferWindowMemory
from langchain import hub
from langchain_groq import ChatGroq
from rag_pipeline.pipeline import RAGPipeline

load_dotenv()  # Load .env file

class OutlineGeneratorAgent:
    def __init__(self, persist_directory="vector_db"):
        # Load API key
        groq_api_key = os.getenv("GROQ_API_KEY")
        if not groq_api_key:
            raise ValueError(" Missing GROQ_API_KEY in .env file")

        # Load RAG pipeline
        self.rag = RAGPipeline(persist_directory=persist_directory).load()
        self.retriever = self.rag.retriever

        # Initialize ChatGroq with Qwen model
        self.llm = ChatGroq(
            groq_api_key=groq_api_key,
            model="llama-3.1-8b-instant",
            temperature=0.3,
            max_tokens=2048
        )

        # Memory for contextual conversations
        self.memory = ConversationBufferWindowMemory(k=3)

        # Define RAG tool
        self.tools = [
            Tool(
                name="ContextRetriever",
                func=self.retrieve_context,
                description="Fetch relevant context from uploaded documents"
            )
        ]

        # Pull a strict JSON-formatted prompt from LangChain Hub
        self.prompt = hub.pull("hwchase17/react-chat-json")

        # Create JSON agent
        self.agent = create_json_chat_agent(self.llm, self.tools, self.prompt)

        # Wrap in AgentExecutor for running the agent
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=True
        )

    def retrieve_context(self, query):
        """Fetch top-5 relevant chunks from the vector DB"""
        results = self.retriever.get_relevant_documents(query)
        return "\n\n".join([doc.page_content for doc in results])

    def generate_outline(self, topic: str, slides: int = 15):
        """Generate a structured presentation outline with strict JSON output"""
        prompt = f"""
                    You are an API that returns ONLY valid JSON.
                    Do NOT include any explanations, reasoning, thoughts, or commentary.
                    Do NOT output <think> tags.
                    Do NOT add any text before or after the JSON.

                    Act as an expert presentation content outliner but ALWAYS respond strictly in JSON.

                    Generate a concise, structured outline of {slides} slides about {topic}.

                    VERY IMPORTANT: You MUST generate outline of EXACTLY {slides} slides.
                    Do NOT reduce or increase the number of slides.
                    If content is insufficient, distribute available information evenly.
                    
                    Use EXACTLY this JSON structure and nothing else:

                    {{ "slides": [ {{"title": "Slide 1 Title", "bullet_points": ["point1", "point2"]}}, ... ] }}
                """

        result = self.agent_executor.invoke({"input": prompt})

        # The agent always returns a dict with the final parsed JSON
        output = result.get("output") or result.get("response") or result

        # Double-check that it's valid JSON
        if isinstance(output, dict):
            return output
        try:
            return json.loads(output)
        except json.JSONDecodeError:
            raise ValueError(" Failed to parse JSON from OutlineGeneratorAgent!")
