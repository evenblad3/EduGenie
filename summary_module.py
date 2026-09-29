import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from ai_service import generate_response, parse_json_response

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Summary"])


class SummaryRequest(BaseModel):
    text: str = Field(..., min_length=10, max_length=10000)


class SummaryResponse(BaseModel):
    summary: str
    key_points: list[str] = Field(default_factory=list)


@router.post("/summarize", response_model=SummaryResponse)
async def summarize_text(request: SummaryRequest):
    prompt = f"""Summarize the following text concisely while preserving key details.

Respond ONLY with a valid JSON object formatted as:
{{
  "summary": "concise summary paragraph",
  "key_points": ["point 1", "point 2", "point 3"]
}}

Text to summarize:
{request.text}"""

    try:
        raw_response = await generate_response(prompt, max_tokens=1500)

        try:
            parsed = parse_json_response(raw_response)
            summary = str(parsed.get("summary") or "").strip()
            raw_key_points = parsed.get("key_points", [])

            if not summary:
                raise ValueError("Missing summary in response.")

            if not isinstance(raw_key_points, list):
                raw_key_points = []

            key_points = [str(kp).strip() for kp in raw_key_points if str(kp).strip()]

            return SummaryResponse(summary=summary, key_points=key_points)

        except (ValueError, AttributeError):
            logger.warning("Failed to parse structured summary, returning raw output.")
            return SummaryResponse(summary=raw_response.strip(), key_points=[])

    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        logger.error(f"Summary error: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate summary.")