import uuid

import pytest

from app.models import URLMapping


@pytest.mark.asyncio
class TestAsyncURLMappingRepository:
    async def test_get_by_url_existing(self, repository, sample_url_mappings):
        # Arrange
        original_url = "https://example.com"

        # Act
        result = await repository.get_by_url(original_url)

        # Assert
        assert result is not None
        assert result.original_url == original_url
        assert result.short_code == "abc123"

    async def test_get_by_url_not_existing(self, repository, clean_db):
        # Arrange
        original_url = "https://nonexistent.com"

        # Act
        result = await repository.get_by_url(original_url)

        # Assert
        assert result is None

    async def test_get_by_short_code_existing(self, repository, sample_url_mappings):
        # Arrange
        short_code = "def456"

        # Act
        result = await repository.get_by_short_code(short_code)

        # Assert
        assert result is not None
        assert result.original_url == "https://test.com"
        assert result.short_code == short_code

    async def test_get_by_short_code_not_existing(self, repository, clean_db):
        # Arrange
        short_code = "nonexistent"

        # Act
        result = await repository.get_by_short_code(short_code)

        # Assert
        assert result is None

    # Data from AsyncBaseRepository tests

    async def test_get_existing(self, repository, sample_url_mappings):
        # Arrange
        url_mapping = sample_url_mappings[0]

        # Act
        result = await repository.get(url_mapping.id)

        # Assert
        assert result is not None
        assert result.id == url_mapping.id
        assert result.original_url == url_mapping.original_url
        assert result.short_code == url_mapping.short_code

    async def test_get_not_existing(self, repository, clean_db):
        # Arrange
        non_existent_id = 9999

        # Act
        result = await repository.get(non_existent_id)

        # Assert
        assert result is None

    async def test_get_all_with_pagination(self, repository, sample_url_mappings):
        # Test first page with limit 2
        result_page1 = await repository.get_all(page=1, limit=2)
        assert len(result_page1) == 2

        # Test second page with limit 2
        result_page2 = await repository.get_all(page=2, limit=2)
        assert len(result_page2) == 1

        # Test empty page
        result_page3 = await repository.get_all(page=3, limit=2)
        assert len(result_page3) == 0

    async def test_add(self, repository, clean_db):
        # Arrange
        unique_url = f"https://new-example-{uuid.uuid4()}.com"
        unique_code = f"new{uuid.uuid4().hex[:6]}"
        new_mapping = URLMapping(original_url=unique_url, short_code=unique_code)

        # Act
        result = await repository.add(new_mapping)

        # Assert
        assert result is not None
        assert result.id is not None
        assert result.original_url == unique_url
        assert result.short_code == unique_code

        # Verify it was actually added to the database
        retrieved = await repository.get_by_url(unique_url)
        assert retrieved is not None
        assert retrieved.short_code == unique_code

    async def test_delete(self, repository, sample_url_mappings):
        # Arrange
        url_mapping_to_delete = sample_url_mappings[0]

        # Act
        await repository.delete(url_mapping_to_delete)

        # Assert - verify it was deleted
        result = await repository.get(url_mapping_to_delete.id)
        assert result is None

        # Also check by URL
        result_by_url = await repository.get_by_url(url_mapping_to_delete.original_url)
        assert result_by_url is None

    async def test_unique_constraints(self, repository, sample_url_mappings):
        # Arrange
        duplicate_url = URLMapping(
            original_url="https://example.com", short_code="unique123"
        )

        duplicate_code = URLMapping(
            original_url="https://unique-url.com", short_code="abc123"
        )

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            await repository.add(duplicate_url)
        assert (
            "unique constraint" in str(exc_info.value).lower()
            or "duplicate key" in str(exc_info.value).lower()
        )

        with pytest.raises(Exception) as exc_info:
            await repository.add(duplicate_code)
        assert (
            "unique constraint" in str(exc_info.value).lower()
            or "duplicate key" in str(exc_info.value).lower()
        )
