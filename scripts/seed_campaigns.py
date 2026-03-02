#!/usr/bin/env python3
"""Seed mock campaign data for testing.

Prints campaign catalog as JSON for inspection or piping to other tools.

Usage:
    python scripts/seed_campaigns.py
    python scripts/seed_campaigns.py --format table
"""

from __future__ import annotations

import argparse
import json

from aain.models.campaign import Campaign, Creative, Advertiser


def generate_campaigns() -> list[Campaign]:
    return [
        Campaign(
            campaign_id="camp_001",
            advertiser_id="adv_salesforce",
            name="Salesforce CRM",
            budget_total=10000.0, budget_remaining=7500.0,
            base_bid=2.50, targeting_categories=["saas", "crm", "business"],
            creatives=[Creative(
                creative_id="cr_001",
                headline="Salesforce — The #1 CRM Platform",
                body="Grow your business with the world's most trusted CRM.",
                cta_text="Start Free Trial",
            )],
        ),
        Campaign(
            campaign_id="camp_002",
            advertiser_id="adv_hubspot",
            name="HubSpot CRM",
            budget_total=8000.0, budget_remaining=6000.0,
            base_bid=2.00, targeting_categories=["saas", "crm", "startup"],
            creatives=[Creative(
                creative_id="cr_002",
                headline="HubSpot — Free CRM for Growing Teams",
                body="All-in-one CRM platform. Free forever. No credit card required.",
                cta_text="Get Started Free",
            )],
        ),
        Campaign(
            campaign_id="camp_003",
            advertiser_id="adv_shopify",
            name="Shopify Ecommerce",
            budget_total=12000.0, budget_remaining=9000.0,
            base_bid=3.00, targeting_categories=["ecommerce", "store", "online"],
            creatives=[Creative(
                creative_id="cr_003",
                headline="Shopify — Build Your Online Store",
                body="Start selling online today with the platform trusted by millions.",
                cta_text="Start Free Trial",
            )],
        ),
        Campaign(
            campaign_id="camp_004",
            advertiser_id="adv_aws",
            name="AWS Cloud Services",
            budget_total=15000.0, budget_remaining=12000.0,
            base_bid=4.00, targeting_categories=["saas", "cloud", "infrastructure"],
            creatives=[Creative(
                creative_id="cr_004",
                headline="AWS — Cloud Computing for Every Workload",
                body="200+ services. Pay only for what you use.",
                cta_text="Explore AWS",
            )],
        ),
        Campaign(
            campaign_id="camp_005",
            advertiser_id="adv_coursera",
            name="Coursera Online Learning",
            budget_total=5000.0, budget_remaining=4000.0,
            base_bid=1.50, targeting_categories=["education", "course", "learning"],
            creatives=[Creative(
                creative_id="cr_005",
                headline="Coursera — Learn New Skills",
                body="Access 7,000+ courses from top universities and companies.",
                cta_text="Start Learning",
            )],
        ),
        Campaign(
            campaign_id="camp_006",
            advertiser_id="adv_stripe",
            name="Stripe Payments",
            budget_total=9000.0, budget_remaining=7200.0,
            base_bid=3.50, targeting_categories=["finance", "payments", "saas"],
            creatives=[Creative(
                creative_id="cr_006",
                headline="Stripe — Payments Infrastructure for the Internet",
                body="Accept payments globally. Developer-first APIs.",
                cta_text="Start Now",
            )],
        ),
        Campaign(
            campaign_id="camp_007",
            advertiser_id="adv_notion",
            name="Notion Workspace",
            budget_total=6000.0, budget_remaining=5000.0,
            base_bid=1.80, targeting_categories=["saas", "productivity", "business"],
            creatives=[Creative(
                creative_id="cr_007",
                headline="Notion — Your All-in-One Workspace",
                body="Notes, docs, wikis, and project management. All in one tool.",
                cta_text="Try Notion Free",
            )],
        ),
    ]


def generate_advertisers() -> list[Advertiser]:
    return [
        Advertiser(advertiser_id="adv_salesforce", name="Salesforce",
                   campaigns=["camp_001"], total_spend=2500.0),
        Advertiser(advertiser_id="adv_hubspot", name="HubSpot",
                   campaigns=["camp_002"], total_spend=2000.0),
        Advertiser(advertiser_id="adv_shopify", name="Shopify",
                   campaigns=["camp_003"], total_spend=3000.0),
        Advertiser(advertiser_id="adv_aws", name="Amazon Web Services",
                   campaigns=["camp_004"], total_spend=3000.0),
        Advertiser(advertiser_id="adv_coursera", name="Coursera",
                   campaigns=["camp_005"], total_spend=1000.0),
        Advertiser(advertiser_id="adv_stripe", name="Stripe",
                   campaigns=["camp_006"], total_spend=1800.0),
        Advertiser(advertiser_id="adv_notion", name="Notion",
                   campaigns=["camp_007"], total_spend=1000.0),
    ]


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed campaign data")
    parser.add_argument("--format", choices=["json", "table"], default="json")
    args = parser.parse_args()

    campaigns = generate_campaigns()
    advertisers = generate_advertisers()

    if args.format == "json":
        data = {
            "campaigns": [c.model_dump() for c in campaigns],
            "advertisers": [a.model_dump() for a in advertisers],
        }
        print(json.dumps(data, indent=2))
    else:
        print(f"\n{'Campaign':<25} {'Advertiser':<20} {'Budget':>10} {'Remaining':>10} {'Bid':>8} {'Categories'}")
        print("-" * 100)
        for c in campaigns:
            cats = ", ".join(c.targeting_categories[:3])
            print(f"{c.name:<25} {c.advertiser_id:<20} ${c.budget_total:>8.0f} ${c.budget_remaining:>8.0f} ${c.base_bid:>6.2f} {cats}")

        print(f"\n  Total campaigns: {len(campaigns)}")
        print(f"  Total advertisers: {len(advertisers)}")
        print(f"  Total budget: ${sum(c.budget_total for c in campaigns):,.0f}")
        print()


if __name__ == "__main__":
    main()
