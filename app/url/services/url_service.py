import random
import string

from fastapi import Depends

from app.common.config import config
from app.models import URLMapping
from app.url.dto.url_dto import OriginalURLSchema, ShortURLSchema
from app.url.errors import Missing
from app.url.repositories import AsyncURLMappingRepository

URL_PATH = f"{config.SERVER_HOST}{config.API_PREFIX}/"


class URLMappingService:
    def __init__(
        self,
        url_repository: AsyncURLMappingRepository = Depends(),
    ):
        self.url_repository = url_repository

    async def get_original_url(self, short_code: str) -> OriginalURLSchema | None:
        original_url = await self.url_repository.get_by_short_code(
            short_code=short_code
        )

        if not original_url:
            raise Missing(message="Short code not found.")

        return OriginalURLSchema.model_validate(original_url)

    async def create_short_code(self, original_url: str) -> ShortURLSchema:
        existing_url = await self.url_repository.get_by_url(original_url)

        if existing_url:
            return ShortURLSchema(short_url=f"{URL_PATH}{existing_url.short_code}")

        short_code = self.__create_short_code()

        if await self.url_repository.get_by_short_code(short_code):
            short_code = self.__create_short_code()

        url_mapping = URLMapping(original_url=original_url, short_code=short_code)
        url_mapping = await self.url_repository.add(url_mapping)

        short_url = f"{URL_PATH}{url_mapping.short_code}"

        return ShortURLSchema(short_url=short_url)

    def __create_short_code(self) -> str:
        return "".join(
            random.choices(
                string.ascii_letters + string.digits, k=config.SHORT_CODE_LENGTH
            )
        )
