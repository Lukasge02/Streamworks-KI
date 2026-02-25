"""Tests for configuration loading."""

import os


def test_defaults_loaded():
    from config import Settings

    s = Settings(
        _env_file=None,
        openai_api_key="test",
        supabase_url="",
        supabase_key="",
    )
    assert s.openai_model == "gpt-4o"
    assert s.qdrant_url == "http://localhost:6333"
    assert s.backend_port == 8000


def test_extra_ignore_does_not_crash():
    """Ensure NEXT_PUBLIC_* variables don't cause validation errors."""
    from config import Settings

    os.environ["NEXT_PUBLIC_BACKEND_URL"] = "http://localhost:8000"
    try:
        s = Settings(_env_file=None, openai_api_key="test")
        # Should not raise
        assert s.openai_api_key == "test"
    finally:
        os.environ.pop("NEXT_PUBLIC_BACKEND_URL", None)


def test_get_settings_caches():
    from config import get_settings

    s1 = get_settings()
    s2 = get_settings()
    assert s1 is s2
