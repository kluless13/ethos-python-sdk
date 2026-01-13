"""
Market model for Ethos reputation markets.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, model_validator


class MarketUser(BaseModel):
    """User info embedded in market response."""

    profile_id: int = Field(..., alias="profileId")
    username: str | None = None
    score: int | None = None

    model_config = {
        "populate_by_name": True,
        "extra": "allow",
    }


class Market(BaseModel):
    """
    A reputation market on Ethos Markets.

    Reputation markets allow users to trade trust/distrust votes
    on a person's reputation using an LMSR-based AMM.
    These markets are perpetual (never resolve).
    """

    id: int

    # Subject of the market (may be at top level or nested in user object)
    profile_id: int | None = Field(None, alias="profileId")

    # Nested user object from API
    user: MarketUser | None = None

    @model_validator(mode="before")
    @classmethod
    def extract_profile_id_from_user(cls, data: dict[str, Any]) -> dict[str, Any]:
        """Extract profileId from nested user object if not at top level."""
        if isinstance(data, dict):
            # If profileId is missing but user.profileId exists, copy it up
            if data.get("profileId") is None and data.get("user"):
                user_data = data.get("user", {})
                if isinstance(user_data, dict) and user_data.get("profileId"):
                    data["profileId"] = user_data["profileId"]
        return data

    # Market state
    trust_votes: int = Field(0, alias="trustVotes")
    distrust_votes: int = Field(0, alias="distrustVotes")

    # Prices (0.0 to 1.0)
    trust_price: float = Field(0.5, alias="trustPrice")
    distrust_price: float = Field(0.5, alias="distrustPrice")

    # Volume
    total_volume: float = Field(0.0, alias="totalVolume")

    # Market parameters
    liquidity_parameter: float | None = Field(None, alias="liquidityParameter")

    # Status
    is_active: bool = Field(True, alias="isActive")

    # Timestamps
    created_at: datetime | None = Field(None, alias="createdAt")
    updated_at: datetime | None = Field(None, alias="updatedAt")

    model_config = {
        "populate_by_name": True,
        "extra": "allow",
    }

    @property
    def trust_percentage(self) -> float:
        """Get trust as a percentage (0-100)."""
        return self.trust_price * 100

    @property
    def distrust_percentage(self) -> float:
        """Get distrust as a percentage (0-100)."""
        return self.distrust_price * 100

    @property
    def market_sentiment(self) -> str:
        """
        Get overall market sentiment.

        Returns:
            "bullish" if trust > 60%
            "bearish" if distrust > 60%
            "neutral" otherwise
        """
        if self.trust_price > 0.6:
            return "bullish"
        elif self.distrust_price > 0.6:
            return "bearish"
        else:
            return "neutral"

    @property
    def is_volatile(self) -> bool:
        """Check if market is volatile (close to 50/50)."""
        return 0.4 <= self.trust_price <= 0.6
