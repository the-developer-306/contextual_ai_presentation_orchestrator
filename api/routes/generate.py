from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from agents.orchestration import PresentationOrchestrator
from utils.security import require_role
from utils.ppt_generator import PPTGenerator

router = APIRouter(tags=["Presentation Generation"])

@router.post("/generate-presentation")
async def generate_presentation(
    topic: str,
    user=Depends(require_role(["Executive", "Senior Manager", "Analyst"]))
):
    try:
        orchestrator = PresentationOrchestrator(persist_directory="vector_db")
        final_ppt_json = orchestrator.generate_presentation(topic, persist_directory="vector_db")

        # Auto-generate PPT
        ppt_generator = PPTGenerator(output_dir="generated_ppt")
        ppt_path = ppt_generator.generate_ppt(final_ppt_json, file_name="AI_Presentation.pptx")

        return JSONResponse(
            status_code=200,
            content={
                "message": " Presentation generated successfully!",
                "topic": topic,
                "ppt_json": final_ppt_json,
                "ppt_path": ppt_path
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f" Failed to generate presentation: {e}")
