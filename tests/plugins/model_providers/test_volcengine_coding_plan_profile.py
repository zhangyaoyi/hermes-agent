"""Behavior contracts for the bundled Volcengine ARK Coding Plan profile."""

from hermes_cli.auth import PROVIDER_REGISTRY, resolve_provider
from hermes_cli.models import provider_model_ids
from providers import get_provider_profile


EXPECTED_CODING_PLAN_MODELS = [
    "ark-code-latest",
    "doubao-seed-evolving",
    "doubao-seed-2.1-turbo",
    "doubao-seed-2.0-lite",
    "minimax-m3",
    "kimi-k2.7-code",
    "kimi-k3",
    "glm-5.3",
    "glm-5.3-flash",
    "deepseek-v4-flash",
    "deepseek-v4-pro",
]


def test_profile_resolves_with_dedicated_endpoint_and_credentials(monkeypatch):
    profile = get_provider_profile("volcengine-coding-plan")

    assert profile is not None
    assert profile.base_url == "https://ark.cn-beijing.volces.com/api/coding/v3"
    assert profile.env_vars == ("ARK_CODING_PLAN_API_KEY",)
    assert "volcengine" not in profile.aliases
    assert "ARK_API_KEY" not in profile.env_vars
    assert resolve_provider("ark-coding") == "volcengine-coding-plan"
    assert PROVIDER_REGISTRY["volcengine-coding-plan"].inference_base_url == profile.base_url

    monkeypatch.setenv("ARK_CODING_PLAN_API_KEY", "ark-test")
    assert resolve_provider() == "volcengine-coding-plan"


def test_picker_uses_verified_allowlist_instead_of_live_models_endpoint():
    profile = get_provider_profile("volcengine-coding-plan")

    assert profile is not None
    assert profile.fetch_models(api_key="ark-test") == EXPECTED_CODING_PLAN_MODELS
    assert provider_model_ids("volcengine-coding-plan") == EXPECTED_CODING_PLAN_MODELS
    assert "auto" not in provider_model_ids("volcengine-coding-plan")
