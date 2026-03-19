import pytest
from unittest.mock import patch

class TestDisorderRoutes:

    @patch("app.routes.disorder_routes.DisorderService")
    def test_list_disorders_endpoint(self, mock_service_class, client):
        mock_service = mock_service_class.return_value
        mock_service.get_all.return_value = [{"cd_transtorno": 1, "nm_transtorno": "TDAH"}]
        
        response = client.get("/v1/disorders")
        
        assert response.status_code == 200
        assert response.json["success"] is True
        assert response.json["data"][0]["nm_transtorno"] == "TDAH"

    @patch("app.routes.disorder_routes.DisorderService")
    def test_create_disorder_endpoint_validation(self, mock_service_class, client):
        payload = {"nm_transtorno": "Ansiedade"}
        
        response = client.post("/v1/disorders", json=payload)
        
        assert response.status_code == 400
        assert response.json["success"] is False

    @patch("app.routes.disorder_routes.DisorderService")
    def test_get_disorder_not_found_handling(self, mock_service_class, client):
        from app.utils.exceptions import NotFoundError
        
        mock_service = mock_service_class.return_value
        mock_service.get_by_id.side_effect = NotFoundError("Not Found")
        
        response = client.get("/v1/disorders/999")
        
        assert response.status_code == 404
        assert response.json["success"] is False
        assert response.json["error"]["message"] == "Not Found"

    @patch("app.routes.disorder_routes.DisorderService")
    def test_create_disorder_full_success(self, mock_service_class, client):
        mock_service = mock_service_class.return_value
        mock_service.create_full.return_value = 10
        
        payload = {
            "disorder": {"nm_transtorno": "TDAH", "cid11": "6A05"},
            "subtypes": [],
            "severities": [],
            "criteria": []
        }
        
        response = client.post("/v1/disorders/full", json=payload)
        
        assert response.status_code == 201
        assert response.json["data"]["id"] == 10
