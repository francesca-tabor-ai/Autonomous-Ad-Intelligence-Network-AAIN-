from __future__ import annotations

from aain.economy.token_ledger import TokenLedger


class InternalAuction:
    """Competitive bidding for priority processing slots.

    When multiple agents could handle a task, they bid tokens.
    Winner pays second-price.
    """

    def __init__(self, ledger: TokenLedger):
        self.ledger = ledger

    async def run_auction(
        self, task_id: str, bidders: list[tuple[str, float]]
    ) -> tuple[str, float] | None:
        """Run a second-price auction.

        Args:
            task_id: Identifier for the task being auctioned.
            bidders: List of (agent_id, bid_amount) tuples.

        Returns:
            (winner_id, clearing_price) or None if no valid bids.
        """
        valid = [
            (aid, bid)
            for aid, bid in bidders
            if self.ledger.balance(aid) >= bid and bid > 0
        ]
        if not valid:
            return None

        valid.sort(key=lambda x: x[1], reverse=True)
        winner_id, winner_bid = valid[0]

        clearing = valid[1][1] if len(valid) > 1 else winner_bid * 0.5
        self.ledger.deduct(winner_id, clearing)

        return (winner_id, clearing)
