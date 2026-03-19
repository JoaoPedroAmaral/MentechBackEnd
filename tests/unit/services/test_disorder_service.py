import pytest
from unittest.mock import MagicMock
from app.services.disorder_service import DisorderService
from app.utils.exceptions import ValidationError, NotFoundError, ConflictError

@pytest.fixture
def mock_repo():
    return MagicMock()

@pytest.fixture
def service(mock_repo):
    return DisorderService(repo=mock_repo)

class TestDisorderService:

    def test_get_by_id_success(self, service, mock_repo):
        mock_repo.get_by_id.return_value = {"cd_transtorno": 1, "nm_transtorno": "Ansiedade"}
        
        result = service.get_by_id(1)
        
        assert result["nm_transtorno"] == "Ansiedade"
        mock_repo.get_by_id.assert_called_once_with(1)

    def test_get_by_id_not_found(self, service, mock_repo):
        mock_repo.get_by_id.return_value = None
        
        with pytest.raises(NotFoundError):
            service.get_by_id(999)

    def test_create_validation_error_missing_fields(self, service):
        with pytest.raises(ValidationError) as exc:
            service.create("", "", None, None, None, None)
        assert "Missing required fields" in str(exc.value)

    def test_create_validation_error_length(self, service):
        with pytest.raises(ValidationError) as exc:
            service.create("ABC", "6B00", None, None, None, None)
        assert "Invalid field length" in str(exc.value)

    def test_create_normalization(self, service, mock_repo):
        mock_repo.exists_duplicate.return_value = False
        mock_repo.create.return_value = 1
        
        service.create("  ansiedade  ", " 6b00 ", "texto longo", None, None, None)
        
        mock_repo.create.assert_called_once_with(
            "Ansiedade",
            "6b00",
            "Texto longo", 
            None,
            None,
            None
        )

    def test_create_duplicate_conflict(self, service, mock_repo):
        mock_repo.exists_duplicate.return_value = True
        
        with pytest.raises(ConflictError):
            service.create("Ansiedade", "6B00", None, None, None, None)
