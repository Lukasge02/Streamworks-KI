"""Tests for the options endpoint."""


class TestOptionsCategories:
    def test_list_categories(self, client):
        resp = client.get("/api/options/categories")
        assert resp.status_code == 200
        categories = resp.json()
        assert isinstance(categories, list)
        assert len(categories) > 0
        # Should be sorted alphabetically
        assert categories == sorted(categories)

    def test_agents_returns_5(self, client):
        resp = client.get("/api/options/agents")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 5

    def test_job_type_returns_3(self, client):
        resp = client.get("/api/options/job_type")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 3

    def test_unknown_category_returns_empty(self, client):
        resp = client.get("/api/options/nonexistent_category")
        assert resp.status_code == 200
        assert resp.json() == []
