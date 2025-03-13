from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from pydantic import HttpUrl

from app.url.dto.url_dto import OriginalURLSchema, ShortURLSchema
from app.url.errors import Duplicate, Missing
from app.url.services import URLMappingService

router = APIRouter()


@router.get(
    "/{short_code}",
    response_model=OriginalURLSchema,
    status_code=status.HTTP_200_OK,
)
async def redirect_url(
    short_code: str = Path(..., max_length=2083, pattern=r"^[a-zA-Z0-9]+$"),
    url_service: URLMappingService = Depends(),
):
    try:
        original_url = await url_service.get_original_url(short_code)
    except Missing as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message,
        )

    return original_url


@router.post(
    path="/short-url",
    response_model=ShortURLSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_short_code(
    original_url: HttpUrl = Query(..., max_length=2083),
    url_service: URLMappingService = Depends(),
):
    try:
        short_code = await url_service.create_short_code(str(original_url))
    except Duplicate as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=e.message,
        )

    return short_code
