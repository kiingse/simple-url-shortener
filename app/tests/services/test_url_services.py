import string
from unittest.mock import patch

import pytest

from app.common.config import config
from app.models import URLMapping
from app.url.dto.url_dto import OriginalURLSchema, ShortURLSchema
from app.url.errors import Missing
from app.url.services.url_service import URL_PATH


@pytest.mark.asyncio
class TestURLMappingService:
    async def test_get_original_url_existing(self, service, mock_url_repository):
        # Arrange
        short_code = "abc123"
        url_mapping = URLMapping(
            id=1, original_url="https://example.com", short_code=short_code
        )
        mock_url_repository.get_by_short_code.return_value = url_mapping

        # Act
        result = await service.get_original_url(short_code)

        # Assert
        assert isinstance(result, OriginalURLSchema)
        assert str(result.original_url) == "https://example.com/"
        mock_url_repository.get_by_short_code.assert_called_with(short_code=short_code)

    async def test_get_original_url_not_existing(self, service, mock_url_repository):
        # Arrange
        short_code = "nonexistent"
        mock_url_repository.get_by_short_code.return_value = None

        # Act & Assert
        with pytest.raises(Missing) as exc_info:
            await service.get_original_url(short_code)

        assert "Short code not found" in str(exc_info.value)
        mock_url_repository.get_by_short_code.assert_called_with(short_code=short_code)

    async def test_create_short_code_existing_url(self, service, mock_url_repository):
        # Arrange
        original_url = "https://example.com"
        existing_mapping = URLMapping(
            id=1, original_url=original_url, short_code="abc123"
        )
        mock_url_repository.get_by_url.return_value = existing_mapping

        # Act
        result = await service.create_short_code(original_url)

        # Assert
        assert isinstance(result, ShortURLSchema)
        assert str(result.short_url) == f"{URL_PATH}abc123"
        mock_url_repository.get_by_url.assert_called_with(original_url)
        mock_url_repository.add.assert_not_called()

    @patch(
        "app.url.services.url_service.URLMappingService._URLMappingService__create_short_code"  # noqa: E501
    )
    async def test_create_short_code_new_url(
        self, mock_create_short_code, service, mock_url_repository
    ):
        # Arrange
        original_url = "https://newexample.com"
        short_code = "xyz789"
        mock_url_repository.get_by_url.return_value = None
        mock_url_repository.get_by_short_code.return_value = None
        mock_create_short_code.return_value = short_code

        new_mapping = URLMapping(id=2, original_url=original_url, short_code=short_code)
        mock_url_repository.add.return_value = new_mapping

        # Act
        result = await service.create_short_code(original_url)

        # Assert
        assert isinstance(result, ShortURLSchema)
        assert str(result.short_url) == f"{URL_PATH}{short_code}"
        mock_url_repository.get_by_url.assert_called_with(original_url)
        mock_url_repository.get_by_short_code.assert_called_with(short_code)
        mock_url_repository.add.assert_called_once()
        added_mapping = mock_url_repository.add.call_args[0][0]
        assert added_mapping.original_url == original_url
        assert added_mapping.short_code == short_code

    def test_create_short_code_method(self, service):
        # Act
        short_code = service._URLMappingService__create_short_code()

        # Assert
        assert isinstance(short_code, str)
        assert len(short_code) == config.SHORT_CODE_LENGTH

        allowed_chars = set(string.ascii_letters + string.digits)
        assert all(c in allowed_chars for c in short_code)
