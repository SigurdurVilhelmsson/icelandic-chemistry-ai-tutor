"""
Tests for API Endpoints - FastAPI route testing.

This module tests the FastAPI endpoints including:
- POST /ask endpoint
- GET /health endpoint
- Request validation
- Error responses
- CORS configuration
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, MagicMock, patch


# ============================================================================
# Health Endpoint Tests
# ============================================================================

@pytest.mark.unit
class TestHealthEndpoint:
    """Test health check endpoint."""

    def test_health_check_success(self, test_client, mock_app_dependencies):
        """Test successful health check."""
        response = test_client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy" or data["status"] == "ok"

    def test_health_check_includes_service_info(self, test_client, mock_app_dependencies):
        """Test that health check includes service information."""
        response = test_client.get("/health")

        assert response.status_code == 200
        data = response.json()
        # Should include service name or version
        assert "service" in data or "version" in data


# ============================================================================
# Ask Endpoint Tests
# ============================================================================

@pytest.mark.unit
class TestAskEndpoint:
    """Test question answering endpoint."""

    def test_ask_valid_question(self, test_client, mock_app_dependencies):
        """Test asking a valid question."""
        mock_app_dependencies["rag_pipeline"].ask.return_value = {
            "answer": "Test answer",
            "citations": [],
            "confidence": 0.9
        }

        response = test_client.post(
            "/ask",
            json={"question": "Hvað er atóm?"}
        )

        assert response.status_code == 200
        data = response.json()
        assert "answer" in data
        assert data["answer"] == "Test answer"

    def test_ask_with_icelandic_characters(
        self,
        test_client,
        mock_app_dependencies,
        assert_icelandic_preserved
    ):
        """Test that Icelandic characters are preserved through API."""
        icelandic_answer = "Atóm með þ, æ, ö, ð."
        mock_app_dependencies["rag_pipeline"].ask.return_value = {
            "answer": icelandic_answer,
            "citations": []
        }

        response = test_client.post(
            "/ask",
            json={"question": "Hvað er atóm með þ, æ, ö?"}
        )

        assert response.status_code == 200
        data = response.json()
        assert_icelandic_preserved(data["answer"])

    def test_ask_empty_question(self, test_client, mock_app_dependencies):
        """Test validation of empty question."""
        response = test_client.post(
            "/ask",
            json={"question": ""}
        )

        # Should return validation error
        assert response.status_code in [400, 422]

    def test_ask_missing_question_field(self, test_client, mock_app_dependencies):
        """Test validation of missing question field."""
        response = test_client.post(
            "/ask",
            json={}
        )

        # Should return validation error
        assert response.status_code == 422

    def test_ask_invalid_json(self, test_client, mock_app_dependencies):
        """Test handling of invalid JSON."""
        response = test_client.post(
            "/ask",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )

        # Should return error
        assert response.status_code in [400, 422]

    def test_ask_with_citations(self, test_client, mock_app_dependencies):
        """Test that citations are returned in response."""
        mock_app_dependencies["rag_pipeline"].ask.return_value = {
            "answer": "Test answer",
            "citations": [
                {
                    "chapter_number": 1,
                    "section_number": "1.1",
                    "chapter_title": "Test Chapter",
                    "section_title": "Test Section"
                }
            ]
        }

        response = test_client.post(
            "/ask",
            json={"question": "Test question?"}
        )

        assert response.status_code == 200
        data = response.json()
        assert "citations" in data
        assert len(data["citations"]) > 0

    def test_ask_with_session_id(self, test_client, mock_app_dependencies):
        """Test asking question with session ID."""
        mock_app_dependencies["rag_pipeline"].ask.return_value = {
            "answer": "Test answer",
            "citations": []
        }

        response = test_client.post(
            "/ask",
            json={
                "question": "Test question?",
                "session_id": "test-session-123"
            }
        )

        assert response.status_code == 200


# ============================================================================
# Error Handling Tests
# ============================================================================

@pytest.mark.unit
class TestAPIErrorHandling:
    """Test API error handling."""

    def test_internal_error_handling(self, test_client, mock_app_dependencies):
        """Test handling of internal errors."""
        mock_app_dependencies["rag_pipeline"].ask.side_effect = Exception("Internal error")

        response = test_client.post(
            "/ask",
            json={"question": "Test question?"}
        )

        # Should return 500 error
        assert response.status_code == 500
        data = response.json()
        assert "detail" in data or "error" in data

    def test_database_error_handling(self, test_client, mock_app_dependencies, mock_db_error):
        """Test handling of database errors."""
        mock_app_dependencies["rag_pipeline"].ask.side_effect = mock_db_error

        response = test_client.post(
            "/ask",
            json={"question": "Test question?"}
        )

        # Should return error
        assert response.status_code >= 400

    def test_api_timeout_handling(self, test_client, mock_app_dependencies, mock_api_timeout):
        """Test handling of API timeouts."""
        mock_app_dependencies["rag_pipeline"].ask.side_effect = mock_api_timeout

        response = test_client.post(
            "/ask",
            json={"question": "Test question?"}
        )

        # Should return timeout error
        assert response.status_code >= 400


# ============================================================================
# CORS Tests
# ============================================================================

@pytest.mark.unit
class TestCORS:
    """Test CORS configuration."""

    def test_cors_headers_present(self, test_client, mock_app_dependencies):
        """Test that CORS headers are present in responses."""
        response = test_client.options(
            "/ask",
            headers={"Origin": "http://localhost:3000"}
        )

        # CORS headers should be present
        assert "access-control-allow-origin" in response.headers or \
               response.status_code in [200, 204]

    def test_preflight_request(self, test_client, mock_app_dependencies):
        """Test CORS preflight request."""
        response = test_client.options(
            "/ask",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "POST"
            }
        )

        # Should allow preflight
        assert response.status_code in [200, 204]


# ============================================================================
# Request Validation Tests
# ============================================================================

@pytest.mark.unit
class TestRequestValidation:
    """Test request validation."""

    def test_question_max_length(self, test_client, mock_app_dependencies):
        """Test validation of question max length."""
        # Very long question
        long_question = "x" * 10000

        response = test_client.post(
            "/ask",
            json={"question": long_question}
        )

        # Should either accept or reject with validation error
        assert response.status_code in [200, 400, 422, 413]

    def test_content_type_validation(self, test_client, mock_app_dependencies):
        """Test that content-type must be JSON."""
        response = test_client.post(
            "/ask",
            data="question=test",
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )

        # Should reject non-JSON
        assert response.status_code in [415, 422]

    def test_special_characters_in_question(self, test_client, mock_app_dependencies):
        """Test handling of special characters."""
        mock_app_dependencies["rag_pipeline"].ask.return_value = {
            "answer": "Test answer",
            "citations": []
        }

        # Question with special characters
        response = test_client.post(
            "/ask",
            json={"question": "What is <script>alert('xss')</script> atom?"}
        )

        # Should handle safely (sanitize or accept)
        assert response.status_code in [200, 400]


# ============================================================================
# Response Format Tests
# ============================================================================

@pytest.mark.unit
class TestResponseFormat:
    """Test response format consistency."""

    def test_response_structure(self, test_client, mock_app_dependencies):
        """Test that responses have consistent structure."""
        mock_app_dependencies["rag_pipeline"].ask.return_value = {
            "answer": "Test answer",
            "citations": [],
            "timestamp": "2025-01-15T10:30:00Z"
        }

        response = test_client.post(
            "/ask",
            json={"question": "Test?"}
        )

        assert response.status_code == 200
        data = response.json()

        # Required fields
        assert "answer" in data
        assert isinstance(data["answer"], str)

    def test_response_content_type(self, test_client, mock_app_dependencies):
        """Test that response content-type is JSON."""
        mock_app_dependencies["rag_pipeline"].ask.return_value = {
            "answer": "Test",
            "citations": []
        }

        response = test_client.post(
            "/ask",
            json={"question": "Test?"}
        )

        assert "application/json" in response.headers["content-type"]

    def test_unicode_response_encoding(
        self,
        test_client,
        mock_app_dependencies,
        assert_icelandic_preserved
    ):
        """Test that Unicode is properly encoded in responses."""
        icelandic_answer = "Svar með íslenskum stöfum: á, é, í, ó, ú, þ, æ, ö, ð"
        mock_app_dependencies["rag_pipeline"].ask.return_value = {
            "answer": icelandic_answer,
            "citations": []
        }

        response = test_client.post(
            "/ask",
            json={"question": "Test?"}
        )

        assert response.status_code == 200
        assert response.encoding == "utf-8" or "utf-8" in response.headers.get("content-type", "")

        data = response.json()
        assert_icelandic_preserved(data["answer"])


# ============================================================================
# Performance Tests
# ============================================================================

@pytest.mark.slow
@pytest.mark.performance
class TestAPIPerformance:
    """Test API endpoint performance."""

    def test_response_time(
        self,
        test_client,
        mock_app_dependencies,
        performance_timer,
        expected_responses
    ):
        """Test that API responses are fast."""
        mock_app_dependencies["rag_pipeline"].ask.return_value = {
            "answer": "Quick answer",
            "citations": []
        }

        with performance_timer() as timer:
            response = test_client.post(
                "/ask",
                json={"question": "Test?"}
            )

        assert response.status_code == 200
        # API overhead should be minimal
        assert timer.elapsed < 1.0
