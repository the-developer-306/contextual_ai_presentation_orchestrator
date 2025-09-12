import json
from agents.outline_generator_agent import OutlineGeneratorAgent
from agents.content_expansion_agent import ContentExpansionAgent
from agents.qa_agent import QAAgent
from agents.format_optimizer_agent import FormatOptimizerAgent

class PresentationOrchestrator:
    def __init__(self, persist_directory="vector_db"):
        """
        Initialize all agents in the pipeline.
        Only OutlineGeneratorAgent and QAAgent require persist_directory.
        """
        self.outline_agent = OutlineGeneratorAgent(persist_directory=persist_directory)
        self.expansion_agent = ContentExpansionAgent()
        self.qa_agent = QAAgent(persist_directory=persist_directory)
        self.format_optimizer = FormatOptimizerAgent()

    def generate_presentation(self, topic: str, persist_directory: str = "vector_db"):
        """
        Orchestrates the entire workflow:
        1. Generate Outline
        2. Expand Outline
        3. Validate Expanded Content
        4. Format Final PPT JSON
        """
        try:
            print("\n🔹 Step 1: Generating outline...")
            outline = self.outline_agent.generate_outline(topic)
            print(" Outline generated successfully!")
            print(json.dumps(outline, indent=4))

            print("\n🔹 Step 2: Expanding outline...")
            expanded = self.expansion_agent.expand_outline(outline)
            print(" Expansion completed successfully!")
            print(json.dumps(expanded, indent=4))

            print("\n🔹 Step 3: Validating expanded content...")
            validated = self.qa_agent.validate_content(expanded)
            print(" Validation completed successfully!")
            print(json.dumps(validated, indent=4))

            print("\n🔹 Step 4: Optimizing format for PPT...")
            final_presentation = self.format_optimizer.optimize_format(expanded, validated)
            print(json.dumps(final_presentation, indent=4))
            print(" Format optimization completed successfully!")
            print(" PPT Generation completed successfully!")

            return final_presentation

        except Exception as e:
            print(f" Error in orchestration: {e}")
            return {
                "slides": [
                    {
                        "title": " Orchestration failed",
                        "content": ["Manual intervention required"]
                    }
                ],
                "summary": " Pipeline execution failed"
            }
