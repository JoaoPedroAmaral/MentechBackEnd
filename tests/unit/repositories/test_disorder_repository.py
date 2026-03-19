import pytest
from unittest.mock import MagicMock, patch
from app.repositories.disorder_repository import DisorderRepository, DuplicateError

@pytest.fixture
def repo():
    return DisorderRepository()

@pytest.fixture
def mock_conn():
    with patch('app.repositories.disorder_repository.get_connection') as mock:
        yield mock

class TestDisorderRepository:
    
    def test_get_by_id_returns_data(self, repo, mock_conn):
        mock_cursor = mock_conn.return_value.cursor.return_value
        mock_cursor.fetchone.return_value = {
            "cd_transtorno": 1,
            "nm_transtorno": "Ansiedade",
            "cid11": "6B00",
            "apoio_diag": "Test",
            "prevalencia": "1%",
            "cd_cid": 10
        }
        
        result = repo.get_by_id(1)
        
        assert result is not None
        assert result["nm_transtorno"] == "Ansiedade"
        assert mock_cursor.execute.called

    def test_create_full_raises_duplicate_error(self, repo, mock_conn):
        mock_cursor = mock_conn.return_value.cursor.return_value
        mock_cursor.fetchone.return_value = (1,)
        
        disorder_data = {
            "nm_transtorno": "TDAH",
            "cid11": "6A05"
        }
        
        with pytest.raises(DuplicateError) as excinfo:
            repo.create_full(disorder_data, [], [], [])
        
        assert "Duplicate disorder" in str(excinfo.value)

    def test_get_all_returns_list(self, repo, mock_conn):
        mock_cursor = mock_conn.return_value.cursor.return_value
        mock_cursor.fetchall.return_value = [{"cd_transtorno": 1, "nm_transtorno": "A"}]
        
        results = repo.get_all()
        
        assert len(results) == 1
        assert results[0]["nm_transtorno"] == "A"

    def test_delete_cascade_calls_execute(self, repo, mock_conn):
        mock_cursor = mock_conn.return_value.cursor.return_value
        
        repo.delete_cascade(1)
        
        assert mock_conn.return_value.commit.called
        assert mock_cursor.execute.called
