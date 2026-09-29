import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from ai_service import generate_response

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Q&A"])


class QARequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=2000)


class QAResponse(BaseModel):
    answer: str


@router.post("/qa", response_model=QAResponse)
async def answer_question(request: QARequest):
    prompt = f"""You are EduGenie, an educational assistant. Provide a clear, accurate, and structured answer with examples where appropriate.

Question: {request.question}

Answer:"""

    try:
        answer = await generate_response(prompt)
        return QAResponse(answer=answer)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        logger.error(f"Q&A error: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred. Please try again.")