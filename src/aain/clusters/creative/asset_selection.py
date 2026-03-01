from __future__ import annotations

from typing import Any

from aain.core.agent import BaseAgent
from aain.core.blackboard import Blackboard
from aain.core.events import Event
from aain.core.types import EventType
from aain.models.campaign import Campaign
from aain.models.creative import CreativeAsset

MOCK_ASSETS: dict[str, list[CreativeAsset]] = {
    "camp_001": [
        CreativeAsset(asset_id="asset_001", campaign_id="camp_001", asset_type="image",
                      url="/assets/salesforce_banner.png", tags=["crm", "enterprise"]),
    ],
    "camp_002": [
        CreativeAsset(asset_id="asset_002", campaign_id="camp_002", asset_type="image",
                      url="/assets/hubspot_banner.png", tags=["crm", "startup", "free"]),
    ],
    "camp_003": [
        CreativeAsset(asset_id="asset_003", campaign_id="camp_003", asset_type="image",
                      url="/assets/shopify_banner.png", tags=["ecommerce", "store"]),
    ],
}


class AssetSelectionAgent(BaseAgent):
    """Selects best-performing visuals and adjusts format by placement."""

    @property
    def subscriptions(self) -> list[EventType]:
        return [EventType.PIPELINE_STAGE]

    async def process(self, event: Event, blackboard: Blackboard) -> Any:
        winning = blackboard.read("winning_campaign")
        if not winning:
            candidates = blackboard.read("candidate_campaigns", [])
            winning = candidates[0] if candidates else None

        if not winning:
            blackboard.write(self.agent_id, "selected_assets", [])
            return []

        campaign: Campaign = winning
        assets = MOCK_ASSETS.get(campaign.campaign_id, [])

        if not assets:
            assets = [
                CreativeAsset(
                    asset_id=f"default_{campaign.campaign_id}",
                    campaign_id=campaign.campaign_id,
                    asset_type="text",
                    tags=campaign.targeting_categories,
                )
            ]

        blackboard.write(self.agent_id, "selected_assets", assets)
        return assets
