# ethos-py

**The unofficial Python SDK for [Ethos Network](https://ethos.network) API**

First Python client for interacting with Ethos Network's on-chain reputation protocol.

[![PyPI version](https://img.shields.io/pypi/v/ethos-py.svg)](https://pypi.org/project/ethos-py/)
[![PyPI downloads](https://img.shields.io/pypi/dm/ethos-py.svg)](https://pypi.org/project/ethos-py/)
[![Python 3.9+](https://img.shields.io/pypi/pyversions/ethos-py.svg)](https://pypi.org/project/ethos-py/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

---

## Installation

```bash
pip install ethos-py
```

---

## Quick Start

```python
from ethos import Ethos

# Initialize client
client = Ethos()

# Get a user by Twitter handle
user = client.users.get_by_twitter("vitalikbuterin")
print(f"@{user.username}: Score {user.score}")

# Get profile statistics
stats = client.profiles.stats()
print(f"Active profiles: {stats.active_profiles}")

# List reputation markets
for market in client.markets.list():
    print(f"Profile {market.profile_id}: {market.trust_percentage:.1f}% trust")

# Get vouches for a profile
vouches = client.vouches.for_profile(profile_id=8)
for vouch in vouches:
    print(f"Staked: {vouch.staked_eth:.4f} ETH")

# Search profiles
profiles = client.profiles.search("ethereum")
```

---

## Features

- **Simple, Pythonic API** - Resource-based design (`client.vouches.list()`)
- **Type hints everywhere** - Full autocomplete and mypy support
- **Pydantic models** - Validated, typed response objects
- **Auto-pagination** - Iterate through all results seamlessly
- **Built-in rate limiting** - Respects API limits automatically
- **Retry with backoff** - Handles transient failures gracefully
- **Async support** - `async/await` ready for high-performance apps

---

## Usage

### Users

```python
from ethos import Ethos

client = Ethos()

# Get user by Twitter/X handle
user = client.users.get_by_twitter("vitalikbuterin")
print(f"Score: {user.score}")
print(f"Username: {user.username}")

# Get user by Ethereum address
user = client.users.get_by_address("0x123...")

# Get user by profile ID
user = client.users.get(profile_id=123)
```

### Profiles

```python
# Get profile by ID
profile = client.profiles.get(123)

# Get profile by Ethereum address
profile = client.profiles.get_by_address("0x123...")

# Get profile by Twitter handle
profile = client.profiles.get_by_twitter("username")

# Search profiles
profiles = client.profiles.search("query", limit=20)

# Get global profile statistics
stats = client.profiles.stats()
print(f"Active profiles: {stats.active_profiles}")
print(f"Invites available: {stats.invites_available}")

# List all profiles (auto-paginated)
for profile in client.profiles.list():
    print(profile.credibility_score)
```

### Vouches

```python
# Get vouches received by a profile
vouches = client.vouches.for_profile(profile_id=123)

# Get vouches given by a profile
vouches = client.vouches.by_profile(profile_id=456)

# Check vouch between two profiles
vouch = client.vouches.between(voucher_id=456, target_id=123)

# Filter vouches with multiple criteria
for vouch in client.vouches.list(
    target_profile_id=123,      # Vouches received by profile
    author_profile_id=456,      # Vouches given by profile
):
    print(f"Staked: {vouch.staked_eth:.4f} ETH")
    print(f"Balance: {vouch.amount_eth:.4f} ETH")
    print(f"Active: {vouch.is_active}")
```

### Reviews

```python
# List all reviews
reviews = client.reviews.list()

# Filter by target
reviews = client.reviews.list(target_profile_id=123)

# Filter by sentiment
positive_reviews = client.reviews.list(score="positive")
negative_reviews = client.reviews.list(score="negative")
```

### Markets (Reputation Trading)

```python
# List all reputation markets
for market in client.markets.list():
    print(f"Profile {market.profile_id}: {market.trust_percentage:.1f}% trust")

# Get market for a specific profile
market = client.markets.get_by_profile(profile_id=123)

# Get market by ID
market = client.markets.get(market_id=1)

# Market properties
print(f"Trust price: {market.trust_price}")        # 0.0 to 1.0
print(f"Distrust price: {market.distrust_price}")  # 0.0 to 1.0
print(f"Trust %: {market.trust_percentage}")       # 0 to 100
print(f"Sentiment: {market.market_sentiment}")     # "bullish", "bearish", "neutral"
print(f"Volatile: {market.is_volatile}")           # True if close to 50/50

# Get top markets
most_trusted = client.markets.most_trusted(limit=10)
most_distrusted = client.markets.most_distrusted(limit=10)
top_volume = client.markets.top_by_volume(limit=10)
```

### Activities

```python
# List all activities
activities = client.activities.list()

# Filter by type
vouch_activities = client.activities.list(activity_type="vouch")
review_activities = client.activities.list(activity_type="review")
```

### Credibility Scores

```python
# Get score for an address
score = client.scores.get("0x123...")
print(f"Score: {score.value}")
print(f"Level: {score.level}")  # "untrusted", "neutral", "trusted", etc.
```

---

## Async Support

```python
import asyncio
from ethos import AsyncEthos

async def main():
    async with AsyncEthos() as client:
        profile = await client.profiles.get(123)
        vouches = await client.vouches.list(target_profile_id=123)
        
asyncio.run(main())
```

---

## Configuration

### Environment Variables

```bash
# Optional: Custom client name (for rate limit tracking)
export ETHOS_CLIENT_NAME="my-app"

# Optional: Custom base URL
export ETHOS_API_BASE_URL="https://api.ethos.network/api/v2"
```

### Client Options

```python
from ethos import Ethos

client = Ethos(
    client_name="my-app",           # Identifies your app to Ethos
    rate_limit=0.5,                 # Seconds between requests
    timeout=30,                     # Request timeout
    max_retries=3,                  # Retry failed requests
)
```

---

## Response Models

All responses are Pydantic models with full type hints:

```python
from ethos.types import Profile, Vouch, Market, User, GlobalProfileStats

# Profile model
profile: Profile = client.profiles.get(123)
profile.id                    # int
profile.address               # str
profile.twitter_handle        # Optional[str]
profile.credibility_score     # int
profile.score_level           # "untrusted", "questionable", "neutral", "reputable", "exemplary"

# Vouch model  
vouch: Vouch = client.vouches.get(456)
vouch.staked_wei              # int (wei amount)
vouch.staked_eth              # float (ETH amount)
vouch.is_staked               # bool
vouch.is_active               # bool (staked and not archived)

# Market model
market: Market = client.markets.get(789)
market.trust_price            # float (0.0 to 1.0)
market.trust_percentage       # float (0 to 100)
market.market_sentiment       # "bullish", "bearish", "neutral"

# Convert to dict/JSON
profile.model_dump()
profile.model_dump_json()
```

---

## Error Handling

```python
from ethos import Ethos
from ethos.exceptions import (
    EthosAPIError,
    EthosNotFoundError,
    EthosRateLimitError,
    EthosValidationError,
)

client = Ethos()

try:
    profile = client.profiles.get(999999)
except EthosNotFoundError:
    print("Profile not found")
except EthosRateLimitError:
    print("Rate limited - slow down")
except EthosAPIError as e:
    print(f"API error: {e.status_code} - {e.message}")
```

---

## Pagination

The SDK handles pagination automatically:

```python
# This iterates through ALL vouches, fetching pages as needed
for vouch in client.vouches.list():
    process(vouch)

# Or get a specific page
page = client.vouches.list(limit=100, offset=200)
```

---

## Development

```bash
# Clone the repo
git clone https://github.com/kluless13/ethos-python-sdk.git
cd ethos-python-sdk

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest

# Type checking
mypy src/ethos

# Formatting
black src tests
ruff check src tests
```

---

## Why This Exists

Ethos Network provides a REST API but no official Python SDK. This library fills that gap for:

- **Researchers** analyzing on-chain reputation data
- **Data scientists** building trust metrics
- **Developers** integrating Ethos into Python applications
- **Analysts** studying Web3 social dynamics

---

## Related Projects

- [Ethos Network](https://ethos.network) - The protocol
- [Ethos API Docs](https://developers.ethos.network) - Official API documentation
- [ethos-research](https://github.com/kluless13/ethos-research) - Research using this SDK

---

## License

MIT License - see [LICENSE](LICENSE) for details.

---

## Contributing

Contributions welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) first.

---

## Disclaimer

This is an unofficial SDK and is not affiliated with or endorsed by Ethos Network.
