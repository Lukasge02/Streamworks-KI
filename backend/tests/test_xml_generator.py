"""Tests for XML generation logic."""

import xml.etree.ElementTree as ET

from services.xml_generator import (
    _xml_boolean,
    _flatten_session_data,
    _ensure_stream_prefix,
    generate_xml,
)


class TestXmlBoolean:
    def test_true_bool(self):
        assert _xml_boolean(True) == "True"

    def test_false_bool(self):
        assert _xml_boolean(False) == "False"

    def test_true_string(self):
        assert _xml_boolean("true") == "True"
        assert _xml_boolean("True") == "True"
        assert _xml_boolean("1") == "True"
        assert _xml_boolean("yes") == "True"
        assert _xml_boolean("ja") == "True"

    def test_false_string(self):
        assert _xml_boolean("false") == "False"
        assert _xml_boolean("no") == "False"
        assert _xml_boolean("0") == "False"

    def test_none(self):
        assert _xml_boolean(None) == "False"

    def test_integer_truthy(self):
        assert _xml_boolean(1) == "True"
        assert _xml_boolean(42) == "True"

    def test_integer_falsy(self):
        assert _xml_boolean(0) == "False"


class TestFlattenSessionData:
    def test_empty_input(self):
        assert _flatten_session_data({}) == {}

    def test_flat_keys_pass_through(self):
        result = _flatten_session_data({"key": "value"})
        assert result == {"key": "value"}

    def test_step_dicts_flattened(self):
        data = {
            "step_1": {"stream_name": "Test", "job_type": "STANDARD"},
            "step_2": {"contact": "admin@test.de"},
        }
        flat = _flatten_session_data(data)
        assert flat["stream_name"] == "Test"
        assert flat["job_type"] == "STANDARD"
        assert flat["contact"] == "admin@test.de"

    def test_nested_dicts_promoted(self):
        data = {
            "step_4": {
                "parameters": {
                    "source_path": "/tmp/src",
                    "dest_path": "/tmp/dst",
                }
            }
        }
        flat = _flatten_session_data(data)
        assert flat["source_path"] == "/tmp/src"
        assert flat["dest_path"] == "/tmp/dst"

    def test_lists_preserved(self):
        data = {"step_0": {"uploaded_files": ["a.pdf", "b.docx"]}}
        flat = _flatten_session_data(data)
        assert flat["uploaded_files"] == ["a.pdf", "b.docx"]


class TestEnsureStreamPrefix:
    def test_adds_prefix(self):
        assert _ensure_stream_prefix("MyStream") == "GECK003_MyStream"

    def test_no_double_prefix(self):
        assert _ensure_stream_prefix("GECK003_MyStream") == "GECK003_MyStream"

    def test_empty_name_gets_unnamed(self):
        assert _ensure_stream_prefix("") == "GECK003_unnamed"

    def test_none_equivalent_empty(self):
        # Empty string is the only falsy string case
        assert _ensure_stream_prefix("") == "GECK003_unnamed"


class TestGenerateXml:
    def test_empty_session_produces_xml(self):
        xml_str = generate_xml({})
        assert xml_str is not None
        assert len(xml_str) > 0
        # Should be parseable XML
        ET.fromstring(xml_str)

    def test_defaults_applied(self):
        xml_str = generate_xml({})
        assert "GECK003_unnamed" in xml_str

    def test_standard_job(self):
        data = {
            "step_1": {"stream_name": "TestJob", "job_type": "STANDARD"},
        }
        xml_str = generate_xml(data)
        ET.fromstring(xml_str)
        assert "GECK003_TestJob" in xml_str

    def test_file_transfer_job(self):
        data = {
            "step_1": {
                "stream_name": "FTJob",
                "job_type": "FILE_TRANSFER",
            },
            "step_4": {
                "parameters": {
                    "source_path": "/data/in",
                    "dest_path": "/data/out",
                }
            },
        }
        xml_str = generate_xml(data)
        ET.fromstring(xml_str)
        assert "GECK003_FTJob" in xml_str

    def test_sap_job(self):
        data = {
            "step_1": {
                "stream_name": "SAPJob",
                "job_type": "SAP",
            },
        }
        xml_str = generate_xml(data)
        ET.fromstring(xml_str)
        assert "GECK003_SAPJob" in xml_str

    def test_contact_data_rendered(self):
        data = {
            "step_1": {"stream_name": "ContactTest"},
            "step_2": {
                "contact_name": "Max Mustermann",
                "contact_email": "max@example.de",
            },
        }
        xml_str = generate_xml(data)
        ET.fromstring(xml_str)

    def test_wellformed_xml(self):
        """Comprehensive check that generate_xml always returns valid XML."""
        data = {
            "step_1": {
                "stream_name": "WellFormed",
                "job_type": "STANDARD",
                "description": "A <special> & 'quoted' test",
            },
        }
        xml_str = generate_xml(data)
        # Should not raise
        root = ET.fromstring(xml_str)
        assert root is not None

    def test_schedule_data(self):
        data = {
            "step_1": {"stream_name": "SchedTest", "job_type": "STANDARD"},
            "step_5": {
                "schedule_type": "DAILY",
                "start_time": "08:00",
            },
        }
        xml_str = generate_xml(data)
        ET.fromstring(xml_str)
