from fastapi import APIRouter, Depends, HTTPException, Response, Body
from utils.ppt_generator import PPTGenerator
from utils.security import require_role
from utils.masking import mask_all_sensitive

router = APIRouter(tags=["Download"])

@router.post("/download-ppt")
async def download_ppt(
    ppt_json: dict = Body(...),
    user=Depends(require_role(["Executive", "Senior Manager", "Analyst", "Junior Staff"]))
):
    try:
        # Junior Staff sees masked content
        if user["role"] == "Junior Staff":
            masked_slides = []
            for slide in ppt_json.get("slides", []):
                masked_slide = {
                    "title": slide["title"],
                    "content": [
                        {
                            "statement": mask_all_sensitive(p.get("statement", "")),
                            "status": p.get("status", "needs_review"),
                            "design_hint": p.get("design_hint", "")
                        }
                        for p in slide.get("content", [])
                    ]
                }
                masked_slides.append(masked_slide)
            ppt_json = {"slides": masked_slides, "summary": ppt_json.get("summary", "")}

        ppt_generator = PPTGenerator(output_dir="generated_ppt")
        ppt_path = ppt_generator.generate_ppt(ppt_json, file_name="AI_Presentation.pptx")

        with open(ppt_path, "rb") as f:
            ppt_bytes = f.read()

        return Response(
            content=ppt_bytes,
            media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
            headers={"Content-Disposition": "attachment; filename=AI_Presentation.pptx"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f" Failed to generate PPT: {e}")
