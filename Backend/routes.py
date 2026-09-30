 from fastapi import APIRouter, HTTPException

from backend.schemas import DocumentRequest, DocumentResponse
from ai_core.gemini_generator import GeminiDocumentGenerator


router = APIRouter()

generator = GeminiDocumentGenerator()


# ---------------------------------------------------------
# Generate Legal Document
# ---------------------------------------------------------

@router.post(
    "/generate",
    response_model=DocumentResponse,
)
def generate_document(request: DocumentRequest):

    try:

        generated_text = generator.generate_document(
            document_type=request.document_type,
            parties=request.parties,
            terms=request.terms,
            dates=request.dates,
        )

        return DocumentResponse(
            success=True,
            document_type=request.document_type,
            content=generated_text,
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception as exc:

        raise HTTPException(
            status_code=502,
            detail=f"Document generation failed: {exc}",
        ) from exc