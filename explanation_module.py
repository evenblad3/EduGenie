import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from ai_service import generate_response

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Explanation"])


class ExplainRequest(BaseModel):
    concept: str = Field(..., min_length=1, max_length=1000, description="The concept to explain")


class ExplainResponse(BaseModel):
    explanation: str = Field(..., description="The AI-generated explanation")


@router.post("/explain", response_model=ExplainResponse)
async def explain_concept(request: ExplainRequest):
    prompt = f"""You are EduGenie, an expert educational tutor. Explain the following concept to a student in a clear, simple, and engaging way.

Guidelines:
- Start with a brief overview
- Use simple language and analogies
- Break it into logical sections
- Include a real-world example
- End with a key takeaway
- Use markdown headings (##) and bullet points for structure

Concept: {request.concept}

Explain this concept:"""

    try:
        explanation = await generate_response(prompt)
        return ExplainResponse(explanation=explanation)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        logger.error(f"Explanation error: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred. Please try again.")