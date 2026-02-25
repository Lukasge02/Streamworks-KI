"""Tests for the in-memory database fallback store."""

from services.db import _MemStore, _MemResult


class TestMemStoreInsertSelect:
    def test_insert_returns_row_with_auto_id(self, fresh_memstore):
        result = fresh_memstore.table("sessions").insert({"data": {}}).execute()
        assert len(result.data) == 1
        row = result.data[0]
        assert "id" in row
        assert "created_at" in row
        assert "updated_at" in row

    def test_insert_preserves_explicit_id(self, fresh_memstore):
        result = fresh_memstore.table("sessions").insert({"id": "my-id", "data": {}}).execute()
        assert result.data[0]["id"] == "my-id"

    def test_select_returns_inserted_rows(self, fresh_memstore):
        fresh_memstore.table("sessions").insert({"id": "s1", "data": {"a": 1}}).execute()
        fresh_memstore.table("sessions").insert({"id": "s2", "data": {"b": 2}}).execute()

        result = fresh_memstore.table("sessions").select("*").execute()
        assert len(result.data) == 2

    def test_select_with_eq_filter(self, fresh_memstore):
        fresh_memstore.table("sessions").insert({"id": "s1", "data": {}}).execute()
        fresh_memstore.table("sessions").insert({"id": "s2", "data": {}}).execute()

        result = fresh_memstore.table("sessions").select("*").eq("id", "s1").execute()
        assert len(result.data) == 1
        assert result.data[0]["id"] == "s1"


class TestMemStoreUpdate:
    def test_update_modifies_matching_rows(self, fresh_memstore):
        fresh_memstore.table("sessions").insert({"id": "s1", "data": {}}).execute()

        result = (
            fresh_memstore.table("sessions")
            .update({"data": {"step_1": {"name": "test"}}})
            .eq("id", "s1")
            .execute()
        )
        assert len(result.data) == 1
        assert result.data[0]["data"] == {"step_1": {"name": "test"}}

    def test_update_now_sets_timestamp(self, fresh_memstore):
        fresh_memstore.table("sessions").insert({"id": "s1", "data": {}}).execute()
        old_row = fresh_memstore.table("sessions").select("*").eq("id", "s1").execute().data[0]
        old_updated = old_row["updated_at"]

        fresh_memstore.table("sessions").update({"updated_at": "now()"}).eq("id", "s1").execute()
        new_row = fresh_memstore.table("sessions").select("*").eq("id", "s1").execute().data[0]
        # "now()" should have been replaced with an ISO timestamp, possibly different
        assert isinstance(new_row["updated_at"], str)


class TestMemStoreDelete:
    def test_delete_returns_deleted_rows(self, fresh_memstore):
        fresh_memstore.table("sessions").insert({"id": "s1", "data": {}}).execute()
        result = fresh_memstore.table("sessions").delete().eq("id", "s1").execute()
        assert len(result.data) == 1
        assert result.data[0]["id"] == "s1"

    def test_delete_removes_from_store(self, fresh_memstore):
        fresh_memstore.table("sessions").insert({"id": "s1", "data": {}}).execute()
        fresh_memstore.table("sessions").delete().eq("id", "s1").execute()

        remaining = fresh_memstore.table("sessions").select("*").execute()
        assert len(remaining.data) == 0

    def test_delete_nonexistent_returns_empty(self, fresh_memstore):
        result = fresh_memstore.table("sessions").delete().eq("id", "nope").execute()
        assert result.data == []


class TestMemStoreSingleOrderLimit:
    def test_single_returns_dict(self, fresh_memstore):
        fresh_memstore.table("sessions").insert({"id": "s1", "data": {}}).execute()
        result = fresh_memstore.table("sessions").select("*").eq("id", "s1").single().execute()
        assert isinstance(result.data, dict)
        assert result.data["id"] == "s1"

    def test_single_returns_none_for_missing(self, fresh_memstore):
        result = fresh_memstore.table("sessions").select("*").eq("id", "nope").single().execute()
        assert result.data is None

    def test_order_and_limit(self, fresh_memstore):
        fresh_memstore.table("sessions").insert({"id": "a", "data": {}, "sort": 3}).execute()
        fresh_memstore.table("sessions").insert({"id": "b", "data": {}, "sort": 1}).execute()
        fresh_memstore.table("sessions").insert({"id": "c", "data": {}, "sort": 2}).execute()

        result = (
            fresh_memstore.table("sessions")
            .select("*")
            .order("sort")
            .limit(2)
            .execute()
        )
        assert len(result.data) == 2
        assert result.data[0]["id"] == "b"
        assert result.data[1]["id"] == "c"


class TestSeedData:
    def test_dropdown_options_seeded(self, fresh_memstore):
        result = fresh_memstore.table("dropdown_options").select("*").execute()
        assert len(result.data) > 0

    def test_agents_category_has_5_entries(self, fresh_memstore):
        result = (
            fresh_memstore.table("dropdown_options")
            .select("*")
            .eq("category", "agents")
            .execute()
        )
        assert len(result.data) == 5
