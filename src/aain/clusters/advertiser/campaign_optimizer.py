from __future__ import annotations

from typing import Any

from aain.core.agent import BaseAgent
from aain.core.blackboard import Blackboard
from aain.core.events import Event
from aain.core.types import EventType
from aain.models.campaign import Campaign, Creative
from aain.models.intent import IntentSignal

MOCK_CAMPAIGNS = [
    Campaign(
        campaign_id="camp_001",
        advertiser_id="adv_salesforce",
        name="Salesforce CRM",
        budget_total=10000.0,
        budget_remaining=7500.0,
        base_bid=2.50,
        targeting_categories=["saas", "crm", "business"],
        creatives=[
            Creative(
                creative_id="cr_001",
                headline="Salesforce — The #1 CRM Platform",
                body="Grow your business with the world's most trusted CRM.",
                cta_text="Start Free Trial",
            )
        ],
    ),
    Campaign(
        campaign_id="camp_002",
        advertiser_id="adv_hubspot",
        name="HubSpot CRM",
        budget_total=8000.0,
        budget_remaining=6000.0,
        base_bid=2.00,
        targeting_categories=["saas", "crm", "startup"],
        creatives=[
            Creative(
                creative_id="cr_002",
                headline="HubSpot — Free CRM for Growing Teams",
                body="All-in-one CRM platform. Free forever. No credit card required.",
                cta_text="Get Started Free",
            )
        ],
    ),
    Campaign(
        campaign_id="camp_003",
        advertiser_id="adv_shopify",
        name="Shopify Ecommerce",
        budget_total=12000.0,
        budget_remaining=9000.0,
        base_bid=3.00,
        targeting_categories=["ecommerce", "store", "online"],
        creatives=[
            Creative(
                creative_id="cr_003",
                headline="Shopify — Build Your Online Store",
                body="Start selling online today with the platform trusted by millions.",
                cta_text="Start Free Trial",
            )
        ],
    ),
    Campaign(
        campaign_id="camp_004",
        advertiser_id="adv_aws",
        name="AWS Cloud Services",
        budget_total=15000.0,
        budget_remaining=12000.0,
        base_bid=4.00,
        targeting_categories=["saas", "cloud", "infrastructure"],
        creatives=[
            Creative(
                creative_id="cr_004",
                headline="AWS — Cloud Computing for Every Workload",
                body="200+ services. Pay only for what you use.",
                cta_text="Explore AWS",
            )
        ],
    ),
    Campaign(
        campaign_id="camp_005",
        advertiser_id="adv_coursera",
        name="Coursera Online Learning",
        budget_total=5000.0,
        budget_remaining=4000.0,
        base_bid=1.50,
        targeting_categories=["education", "course", "learning"],
        creatives=[
            Creative(
                creative_id="cr_005",
                headline="Coursera — Learn New Skills",
                body="Access 7,000+ courses from top universities and companies.",
                cta_text="Start Learning",
            )
        ],
    ),
]


class CampaignOptimizerAgent(BaseAgent):
    """Filters and ranks campaigns by relevance to the parsed intent."""

    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self._campaigns = list(MOCK_CAMPAIGNS)

    @property
    def subscriptions(self) -> list[EventType]:
        return [EventType.PIPELINE_STAGE]

    async def process(self, event: Event, blackboard: Blackboard) -> Any:
        intent: IntentSignal | None = blackboard.read("parsed_intent")
        if not intent:
            blackboard.write(self.agent_id, "candidate_campaigns", [])
            return []

        scored: list[tuple[float, Campaign]] = []
        for campaign in self._campaigns:
            if campaign.status != "active" or campaign.budget_remaining <= 0:
                continue
            score = self._score_campaign(campaign, intent)
            if score > 0.1:
                scored.append((score, campaign))

        scored.sort(key=lambda x: x[0], reverse=True)
        candidates = [c for _, c in scored[:5]]

        blackboard.write(self.agent_id, "candidate_campaigns", candidates)
        return candidates

    def _score_campaign(self, campaign: Campaign, intent: IntentSignal) -> float:
        category_overlap = set(campaign.targeting_categories) & set(intent.categories)
        cat_score = len(category_overlap) * 0.3

        query_words = set(intent.query.lower().split())
        target_words = set(w.lower() for w in campaign.targeting_categories)
        keyword_overlap = query_words & target_words
        kw_score = len(keyword_overlap) * 0.2

        budget_ratio = campaign.budget_remaining / max(campaign.budget_total, 1)
        budget_score = budget_ratio * 0.1

        return min(1.0, cat_score + kw_score + budget_score)
