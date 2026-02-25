"""Tests for the wizard XML generation endpoint."""


class TestGenerateXmlEndpoint:
    def test_generate_xml_with_session(self, client):
        # Create session and add data
        sid = client.post("/api/wizard/sessions").json()["id"]
        client.put(
            f"/api/wizard/sessions/{sid}/steps",
            json={"step": 1, "data": {"stream_name": "EndpointTest", "job_type": "STANDARD"}},
        )

        resp = client.post("/api/wizard/generate-xml", json={"session_id": sid})
        assert resp.status_code == 200
        data = resp.json()
        assert "xml" in data
        assert "GECK003_EndpointTest" in data["xml"]
        assert data["filename"] == "EndpointTest.xml"

    def test_stream_name_override(self, client):
        sid = client.post("/api/wizard/sessions").json()["id"]
        client.put(
            f"/api/wizard/sessions/{sid}/steps",
            json={"step": 1, "data": {"stream_name": "Original"}},
        )

        resp = client.post(
            "/api/wizard/generate-xml",
            json={"session_id": sid, "stream_name": "Overridden"},
        )
        assert resp.status_code == 200
        assert "GECK003_Overridden" in resp.json()["xml"]

    def test_nonexistent_session_returns_404(self, client):
        resp = client.post(
            "/api/wizard/generate-xml",
            json={"session_id": "does-not-exist"},
        )
        assert resp.status_code == 404

    def test_empty_session_generates_with_warnings(self, client):
        sid = client.post("/api/wizard/sessions").json()["id"]
        resp = client.post("/api/wizard/generate-xml", json={"session_id": sid})
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["warnings"]) > 0
