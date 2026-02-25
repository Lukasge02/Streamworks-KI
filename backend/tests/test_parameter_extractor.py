"""Tests for the parameter extractor service."""

import json
from unittest.mock import patch, MagicMock

from services.parameter_extractor import (
    _load_parameter_schema,
    _build_json_schema,
    extract_parameters,
)


class TestLoadParameterSchema:
    def test_loads_yaml(self):
        schema = _load_parameter_schema()
        assert isinstance(schema, dict)
        assert "parameter_groups" in schema or "job_types" in schema


class TestBuildJsonSchema:
    def test_produces_valid_schema(self):
        schema = _load_parameter_schema()
        json_schema = _build_json_schema(schema)

        assert json_schema["type"] == "json_schema"
        inner = json_schema["json_schema"]["schema"]
        assert "job_type" in inner["properties"]
        assert "confidence" in inner["properties"]
        assert "parameters" in inner["properties"]

    def test_job_type_has_enum(self):
        schema = _load_parameter_schema()
        json_schema = _build_json_schema(schema)
        jt = json_schema["json_schema"]["schema"]["properties"]["job_type"]
        assert "enum" in jt
        assert len(jt["enum"]) >= 1

    def test_job_types_are_strings_not_dicts(self):
        """Regression: job_types from YAML dict must be extracted as key list."""
        schema = _load_parameter_schema()
        json_schema = _build_json_schema(schema)
        jt_enum = json_schema["json_schema"]["schema"]["properties"]["job_type"]["enum"]
        assert isinstance(jt_enum, list)
        for item in jt_enum:
            assert isinstance(item, str), f"Expected string, got {type(item)}: {item}"


class TestExtractParameters:
    def test_with_mocked_openai(self):
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = json.dumps({
            "job_type": "FILE_TRANSFER",
            "confidence": 0.9,
            "parameters": {"source_path": "/data/in", "dest_path": None},
            "suggestions": ["Bitte Agent angeben"],
        })

        with patch("services.parameter_extractor.OpenAI") as MockOpenAI:
            mock_client = MagicMock()
            mock_client.chat.completions.create.return_value = mock_response
            MockOpenAI.return_value = mock_client

            result = extract_parameters("Transfer files from /data/in daily")

        assert result["job_type"] == "FILE_TRANSFER"
        assert result["confidence"] == 0.9
        assert "source_path" in result["parameters"]
        # Null values should be stripped
        assert "dest_path" not in result["parameters"]

    def test_null_values_removed(self):
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = json.dumps({
            "job_type": "STANDARD",
            "confidence": 0.5,
            "parameters": {"a": "val", "b": None, "c": None, "d": "other"},
            "suggestions": [],
        })

        with patch("services.parameter_extractor.OpenAI") as MockOpenAI:
            mock_client = MagicMock()
            mock_client.chat.completions.create.return_value = mock_response
            MockOpenAI.return_value = mock_client

            result = extract_parameters("some description")

        assert set(result["parameters"].keys()) == {"a", "d"}


class TestAnalyzeEndpoint:
    def test_empty_description_returns_400(self, client):
        resp = client.post("/api/wizard/analyze", json={"description": ""})
        assert resp.status_code == 400

    def test_whitespace_description_returns_400(self, client):
        resp = client.post("/api/wizard/analyze", json={"description": "   "})
        assert resp.status_code == 400
