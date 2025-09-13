from agents.outline_generator_agent import OutlineGeneratorAgent
from agents.content_expansion_agent import ContentExpansionAgent
from agents.qa_agent import QAAgent
from agents.format_optimizer_agent import FormatOptimizerAgent

def test_outline_generator():
    agent = OutlineGeneratorAgent()
    outline = agent.generate_outline("AI and Healthcare")
    assert isinstance(outline, list)
    assert len(outline) > 0

def test_content_expansion():
    agent = ContentExpansionAgent()
    slides = [{"title": "AI", "points": ["intro"]}]
    expanded = agent.expand_content(slides)
    assert any("content" in slide for slide in expanded)

def test_qa_agent():
    agent = QAAgent()
    slides = [{"title": "AI", "content": [{"statement": "AI is useful"}]}]
    verified = agent.verify_facts(slides)
    assert "status" in verified[0]["content"][0]

def test_format_optimizer():
    agent = FormatOptimizerAgent()
    slides = [{"title": "AI", "content": [{"statement": "AI"}]}]
    formatted = agent.optimize_format(slides)
    assert "design_hint" in formatted[0]["content"][0]
