"""Cron email deliveries name the job in the Subject header.

Both delivery lanes carry ``Hermes Agent: <job name>`` (job id fallback):

* live lane — ``_live_route_metadata`` stamps ``subject`` into the route/media
  metadata for EMAIL targets only (other platforms never see the key);
* standalone lane — ``_standalone_send`` forwards it to ``_send_to_platform``,
  which passes it to the email plugin's ``standalone_sender_fn``.
"""

import asyncio
from unittest.mock import patch

import pytest

from cron import scheduler_delivery as sched_delivery
from gateway.config import Platform


def _make_target(platform, job, platform_name=None):
    return sched_delivery._TargetDelivery(
        job=job,
        platform=platform,
        platform_name=platform_name or (platform.value if hasattr(platform, "value") else str(platform)),
        chat_id="user@test.com",
        thread_id=None,
        transport=None,
        pconfig=None,
        runtime_adapter=None,
        target_adapters=None,
        config=None,
        loop=None,
        notify_delivery=False,
        origin={},
        origin_target=False,
        origin_user_id=None,
        is_dm_target=True,
        mirror_text="",
        mirror_this_target=False,
        in_channel_surface=False,
        inchannel_continuable=False,
        opened_thread_id=None,
    )


class TestCronEmailSubject:
    def test_cron_email_subject_uses_job_name(self):
        assert sched_delivery._cron_email_subject({"id": "j1", "name": "daily-report"}) == \
            "Hermes Agent: daily-report"

    def test_cron_email_subject_falls_back_to_job_id(self):
        assert sched_delivery._cron_email_subject({"id": "j1"}) == "Hermes Agent: j1"


class TestLiveRouteMetadataSubject:
    def test_email_target_carries_subject(self):
        t = _make_target(Platform.EMAIL, {"id": "j1", "name": "daily-report"})
        _, route_metadata, media_metadata = sched_delivery._live_route_metadata(t)
        assert route_metadata["subject"] == "Hermes Agent: daily-report"
        assert media_metadata["subject"] == "Hermes Agent: daily-report"

    def test_non_email_target_omits_subject(self):
        t = _make_target(Platform.TELEGRAM, {"id": "j1", "name": "daily-report"},
                         platform_name="telegram")
        _, route_metadata, media_metadata = sched_delivery._live_route_metadata(t)
        assert "subject" not in route_metadata
        assert "subject" not in media_metadata


class TestStandaloneSendSubject:
    def test_forwards_subject_to_send_to_platform(self, monkeypatch):
        captured = {}

        async def fake_send_to_platform(platform, pconfig, chat_id, content, **kwargs):
            captured.update(kwargs)
            return {"success": True}

        monkeypatch.setattr("tools.send_message_tool._send_to_platform", fake_send_to_platform)
        t = _make_target(Platform.EMAIL, {"id": "j1", "name": "daily-report"})

        result, err = sched_delivery._standalone_send(t, "report body", [])

        assert err is None
        assert result == {"success": True}
        assert captured["subject"] == "Hermes Agent: daily-report"
