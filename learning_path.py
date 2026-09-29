import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from ai_service import generate_response, parse_json_response

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Roadmap"])


class LearningPathRequest(BaseModel):
    topic: str = Field(..., min_length=1, max_length=500)


class LearningStage(BaseModel):
    stage: str
    title: str
    description: str
    topics: list[str] = Field(default_factory=list)
    resources: list[str] = Field(default_factory=list)
    duration: str = ""


class LearningPathResponse(BaseModel):
    stages: list[LearningStage]


def validate_learning_path(data) -> list[dict]:
    if not isinstance(data, list) or not data:
        raise ValueError("Payload must be a non-empty array of learning phases.")

    validated = []
    for index, item in enumerate(data[:6]):
        if not isinstance(item, dict):
            continue

        stage = str(item.get("stage") or f"Phase {index + 1}").strip()
        title = str(item.get("title") or stage).strip()
        description = str(item.get("description") or "Master the core concepts of this section.").strip()

        raw_topics = item.get("topics", [])
        if not isinstance(raw_topics, list):
            raw_topics = [raw_topics] if raw_topics else []
        topics = [str(t).strip() for t in raw_topics if str(t).strip()]

        raw_resources = item.get("resources", [])
        if not isinstance(raw_resources, list):
            raw_resources = [raw_resources] if raw_resources else []
        resources = [str(r).strip() for r in raw_resources if str(r).strip()]

        duration = str(item.get("duration") or "Flexible timeline").strip()

        validated.append({
            "stage": stage,
            "title": title,
            "description": description,
            "topics": topics,
            "resources": resources,
            "duration": duration,
        })

    if not validated:
        raise ValueError("Failed to extract valid phases from AI response.")

    return validated


@router.post("/learn/recommendations", response_model=LearningPathResponse)
async def create_learning_path(request: LearningPathRequest):
    prompt = f"""Construct an actionable learning curriculum for the subject: {request.topic}

Output ONLY a JSON array containing 4 sequential phases (Beginner, Foundation, Intermediate, Advanced).

Required schema per object:
- "stage": Phase tier name
- "title": Summary focus
- "description": Key learning outcomes (1-2 sentences)
- "topics": List of 3 to 5 core subjects
- "resources": List of 2 to 3 study reference types
- "duration": Target completion timeframe"""

    try:
        raw_response = await generate_response(prompt, max_tokens=2048)
        parsed = parse_json_response(raw_response)
        validated = validate_learning_path(parsed)
        return LearningPathResponse(stages=[LearningStage(**stage) for stage in validated])

    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to generate curriculum: {e}")
        raise HTTPException(status_code=500, detail="Could not build the requested learning path.")