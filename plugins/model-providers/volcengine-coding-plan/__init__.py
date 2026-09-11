"""Volcengine ARK Coding Plan provider profile.

Coding Plan uses a dedicated subscription endpoint and credential tier. Its
live /models response is not an authoritative list of models covered by the
plan, so the picker uses the allow-list verified against /chat/completions.
"""

from providers import register_provider
from providers.base import ProviderProfile


CODING_PLAN_MODELS = (
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
)


class VolcengineCodingPlanProfile(ProviderProfile):
    """Coding Plan profile with an authoritative static model catalog."""

    def fetch_models(
        self,
        *,
        api_key: str | None = None,
        base_url: str | None = None,
        timeout: float = 8.0,
    ) -> list[str] | None:
        return list(CODING_PLAN_MODELS)


volcengine_coding_plan = VolcengineCodingPlanProfile(
    name="volcengine-coding-plan",
    aliases=("volc-coding", "ark-coding", "volcengine-coding"),
    display_name="Volcengine ARK (Coding Plan)",
    description="Volcengine ARK Coding Plan subscription coding tier",
    signup_url="https://www.volcengine.com/docs/82379/1928261",
    env_vars=("ARK_CODING_PLAN_API_KEY",),
    base_url="https://ark.cn-beijing.volces.com/api/coding/v3",
    auth_type="api_key",
    fallback_models=CODING_PLAN_MODELS,
)

register_provider(volcengine_coding_plan)
