from fastapi import APIRouter
from app.api.v1.endpoints import documents, search

router = APIRouter()

# Регистрируем все эндпоинты из documents.py
router.include_router(documents.router, prefix="/documents", tags=["documents"])

# Регистрируем все эндпоинты из search.py
router.include_router(search.router, prefix="/search", tags=["search"])