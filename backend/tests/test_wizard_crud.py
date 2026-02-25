"""Tests for wizard session CRUD endpoints."""

import uuid


class TestCreateSession:
    def test_create_returns_201_with_id(self, client):
        resp = client.post("/api/wizard/sessions")
        assert resp.status_code == 201
        data = resp.json()
        assert "id" in data
        # Should be a valid UUID
        uuid.UUID(data["id"])
        assert data["data"] == {}


class TestListSessions:
    def test_list_empty(self, client):
        resp = client.get("/api/wizard/sessions")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_list_after_create(self, client):
        client.post("/api/wizard/sessions")
        client.post("/api/wizard/sessions")
        resp = client.get("/api/wizard/sessions")
        assert resp.status_code == 200
        assert len(resp.json()) == 2


class TestGetSession:
    def test_get_existing(self, client):
        create_resp = client.post("/api/wizard/sessions")
        sid = create_resp.json()["id"]

        resp = client.get(f"/api/wizard/sessions/{sid}")
        assert resp.status_code == 200
        assert resp.json()["id"] == sid

    def test_get_missing_returns_404(self, client):
        resp = client.get("/api/wizard/sessions/nonexistent-id")
        assert resp.status_code == 404


class TestSaveStep:
    def test_save_step_updates_session(self, client):
        sid = client.post("/api/wizard/sessions").json()["id"]

        resp = client.put(
            f"/api/wizard/sessions/{sid}/steps",
            json={"step": 1, "data": {"stream_name": "TestStream"}},
        )
        assert resp.status_code == 200

        session = client.get(f"/api/wizard/sessions/{sid}").json()
        assert session["data"]["step_1"]["stream_name"] == "TestStream"

    def test_multiple_steps_dont_overwrite(self, client):
        sid = client.post("/api/wizard/sessions").json()["id"]

        client.put(
            f"/api/wizard/sessions/{sid}/steps",
            json={"step": 1, "data": {"stream_name": "MyStream"}},
        )
        client.put(
            f"/api/wizard/sessions/{sid}/steps",
            json={"step": 2, "data": {"contact": "admin@test.de"}},
        )

        session = client.get(f"/api/wizard/sessions/{sid}").json()
        assert "step_1" in session["data"]
        assert "step_2" in session["data"]
        assert session["data"]["step_1"]["stream_name"] == "MyStream"

    def test_same_step_overwrites(self, client):
        sid = client.post("/api/wizard/sessions").json()["id"]

        client.put(
            f"/api/wizard/sessions/{sid}/steps",
            json={"step": 1, "data": {"stream_name": "First"}},
        )
        client.put(
            f"/api/wizard/sessions/{sid}/steps",
            json={"step": 1, "data": {"stream_name": "Second"}},
        )

        session = client.get(f"/api/wizard/sessions/{sid}").json()
        assert session["data"]["step_1"]["stream_name"] == "Second"


class TestDeleteSession:
    def test_delete_existing(self, client):
        sid = client.post("/api/wizard/sessions").json()["id"]

        resp = client.delete(f"/api/wizard/sessions/{sid}")
        assert resp.status_code == 204

        # Should be gone now
        resp = client.get(f"/api/wizard/sessions/{sid}")
        assert resp.status_code == 404

    def test_delete_nonexistent_returns_404(self, client):
        resp = client.delete("/api/wizard/sessions/does-not-exist")
        assert resp.status_code == 404
