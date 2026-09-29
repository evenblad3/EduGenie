import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from ai_service import generate_response, parse_json_response

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Quiz"])


class QuizRequest(BaseModel):
    topic: str = Field(..., min_length=1, max_length=500)


class QuizQuestion(BaseModel):
    question: str
    options: list[str]
    correct_answer: str


class QuizResponse(BaseModel):
    questions: list[QuizQuestion]


def validate_quiz_data(data) -> list[dict]:
    if not isinstance(data, list) or not data:
        raise ValueError("Quiz data must be a non-empty list.")

    validated = []
    for index, item in enumerate(data[:3]):
        if not isinstance(item, dict):
            raise ValueError(f"Question {index + 1} is invalid.")

        question = str(item.get("question") or "").strip()
        options = item.get("options")
        correct_answer = str(item.get("correct_answer") or "").strip()

        if not question or not isinstance(options, list):
            raise ValueError(f"Question {index + 1} missing required fields.")

        opts = [str(o).strip() for o in options if str(o).strip()][:4]
        if len(opts) < 2:
            raise ValueError(f"Question {index + 1} has insufficient options.")
        while len(opts) < 4:
            opts.append(f"Option {len(opts) + 1}")

        if not correct_answer:
            raise ValueError(f"Question {index + 1} missing correct answer.")

        if correct_answer not in opts:
            matches = [o for o in opts if correct_answer.lower() in o.lower() or o.lower() in correct_answer.lower()]
            correct_answer = matches[0] if matches else opts[0]

        validated.append({
            "question": question,
            "options": opts,
            "correct_answer": correct_answer,
        })

    if not validated:
        raise ValueError("No valid questions extracted.")

    return validated


@router.post("/quiz", response_model=QuizResponse)
async def generate_quiz(request: QuizRequest):
    prompt = f"""Generate 3 multiple-choice quiz questions for topic: {request.topic}

Respond ONLY with a valid JSON array of objects, each formatted as:
{{
  "question": "string",
  "options": ["option1", "option2", "option3", "option4"],
  "correct_answer": "exact string matching one option"
}}"""

    try:
        raw_response = await generate_response(prompt, max_tokens=3000)
        parsed = parse_json_response(raw_response)
        validated = validate_quiz_data(parsed)
        return QuizResponse(questions=[QuizQuestion(**q) for q in validated])
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        logger.error(f"Quiz error: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate quiz.")