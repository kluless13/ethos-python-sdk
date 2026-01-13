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

# Initialize the client (no API key needed!)
client = Ethos()

# Look up a user by Twitter handle
user = client.users.get_by_twitter("vitalikbuterin")
print(f"@{user.username}: Score {user.score}")

# Get network statistics
stats = client.profiles.stats()
print(f"Active profiles: {stats.active_profiles}")

# When done, close the client
client.close()
```

---

## Features

- **No API key required** - Public read access to all Ethos data
- **Simple, Pythonic API** - Resource-based design (`client.vouches.list()`)
- **Type hints everywhere** - Full autocomplete and mypy support
- **Pydantic models** - Validated, typed response objects
- **Auto-pagination** - Iterate through all results seamlessly via generators
- **Built-in rate limiting** - Respects API limits automatically
- **Retry with backoff** - Handles transient failures gracefully
- **Async support** - `async/await` ready for high-performance apps

---

## Available Resources

| Resource | Description |
|----------|-------------|
| `client.profiles` | Profile stats, search, and listing |
| `client.users` | User lookups (by Twitter, address, Discord, etc.) |
| `client.markets` | Reputation markets (trust/distrust trading) |
| `client.vouches` | Vouch relationships between users |
| `client.reviews` | Reviews between users |
| `client.activities` | On-chain activity feed |
| `client.scores` | Credibility scores |
| `client.votes` | Market votes |
| `client.xp` | XP/experience data |

---

## Usage Guide

### 1. Network Statistics

```python
from ethos import Ethos

client = Ethos()

stats = client.profiles.stats()
print(f"Active profiles: {stats.active_profiles}")      # e.g., 35,833
print(f"Invites available: {stats.invites_available}")  # e.g., 39,310
```

---

### 2. Looking Up Users

```python
# By Twitter/X handle
user = client.users.get_by_twitter("edoweb3")

print(f"ID: {user.id}")                           # 1945278
print(f"Profile ID: {user.profile_id}")           # 6694
print(f"Username: {user.username}")               # edoweb3
print(f"Score: {user.score}")                     # 1783 (credibility score)
print(f"XP Total: {user.xp_total}")               # 122887
print(f"Vouches received: {user.stats.vouch.received.count}")  # 24
print(f"Vouches given: {user.stats.vouch.given.count}")        # 25
```

**Other lookup methods:**

```python
# By Ethereum address
user = client.users.get_by_address("0x1234...")

# By profile ID
user = client.users.get(profile_id=6694)

# By Discord ID
user = client.users.get_by_discord("690326861091438693")

# By Telegram ID
user = client.users.get_by_telegram("788216335")

# By Farcaster FID
user = client.users.get_by_farcaster("1117623")
```

---

### 3. Fetching Markets

The SDK uses **generators** for efficient pagination - data is fetched lazily as you iterate:

```python
# Iterate through all markets
for market in client.markets.list():
    print(f"Profile {market.profile_id}")
    print(f"  Trust votes: {market.trust_votes}")
    print(f"  Distrust votes: {market.distrust_votes}")
    print(f"  Trust price: {market.trust_price:.2f}")  # 0.0 to 1.0
    print(f"  Trust %: {market.trust_percentage:.1f}%")
    print(f"  Sentiment: {market.market_sentiment}")   # bullish/bearish/neutral
```

**Get specific markets:**

```python
# By profile ID
market = client.markets.get_by_profile(profile_id=123)

# By market ID
market = client.markets.get(market_id=456)

# Top markets
most_trusted = client.markets.most_trusted(limit=10)
most_distrusted = client.markets.most_distrusted(limit=10)
top_volume = client.markets.top_by_volume(limit=10)
```

**Market properties:**

| Property | Type | Description |
|----------|------|-------------|
| `market.profile_id` | `int` | The Ethos profile ID |
| `market.trust_votes` | `int` | Number of trust votes |
| `market.distrust_votes` | `int` | Number of distrust votes |
| `market.trust_price` | `float` | Trust price (0.0 to 1.0) |
| `market.distrust_price` | `float` | Distrust price (0.0 to 1.0) |
| `market.trust_percentage` | `float` | Trust as percentage (0-100) |
| `market.total_volume` | `float` | Total trading volume |
| `market.market_sentiment` | `str` | "bullish", "bearish", or "neutral" |
| `market.is_volatile` | `bool` | True if close to 50/50 |

---

### 4. Fetching Vouches

```python
# Iterate through all vouches
for vouch in client.vouches.list():
    print(f"From: {vouch.author_profile_id}")
    print(f"To: {vouch.target_profile_id}")
    print(f"Staked: {vouch.staked}")          # Wei amount as string
    print(f"Staked ETH: {vouch.staked_eth}")  # Converted to ETH
    print(f"Active: {vouch.is_active}")
```

**Get vouches for a specific user:**

```python
# Vouches received by a profile
received = client.vouches.for_profile(profile_id=6694)
print(f"Received {len(received)} vouches")

for vouch in received:
    print(f"  From profile {vouch.author_profile_id}: {vouch.staked_eth:.4f} ETH")

# Vouches given by a profile
given = client.vouches.by_profile(profile_id=6694)
print(f"Given {len(given)} vouches")

# Check if vouch exists between two profiles
vouch = client.vouches.between(voucher_id=456, target_id=123)
if vouch:
    print(f"Vouch exists: {vouch.staked_eth} ETH")
```

**Vouch properties:**

| Property | Type | Description |
|----------|------|-------------|
| `vouch.author_profile_id` | `int` | Who gave the vouch |
| `vouch.target_profile_id` | `int` | Who received the vouch |
| `vouch.staked` | `str` | Staked amount in wei |
| `vouch.staked_wei` | `int` | Staked amount as integer |
| `vouch.staked_eth` | `float` | Staked amount in ETH |
| `vouch.is_staked` | `bool` | Has non-zero stake |
| `vouch.is_active` | `bool` | Staked and not archived |
| `vouch.archived` | `bool` | Whether vouch is archived |

---

### 5. Profiles

```python
# Get profile by ID
profile = client.profiles.get(123)

# Get profile by Ethereum address
profile = client.profiles.get_by_address("0x123...")

# Get profile by Twitter handle
profile = client.profiles.get_by_twitter("username")

# Search profiles
profiles = client.profiles.search("ethereum", limit=20)

# List all profiles (generator)
for profile in client.profiles.list():
    print(f"{profile.username}: {profile.credibility_score}")
```

**Profile properties:**

| Property | Type | Description |
|----------|------|-------------|
| `profile.id` | `int` | Profile ID |
| `profile.address` | `str` | Ethereum address |
| `profile.username` | `str` | Username |
| `profile.score` | `int` | Credibility score |
| `profile.score_level` | `str` | "untrusted", "questionable", "neutral", "reputable", "exemplary" |
| `profile.twitter_handle` | `str \| None` | Twitter username if linked |

---

### 6. Reviews

```python
# List all reviews
for review in client.reviews.list():
    print(f"{review.author_profile_id} → {review.target_profile_id}")

# Filter by target
reviews = client.reviews.list(target_profile_id=123)

# Filter by sentiment
positive = client.reviews.list(score="positive")
negative = client.reviews.list(score="negative")
```

---

## Complete Example

```python
from ethos import Ethos

client = Ethos()

# Get network stats
stats = client.profiles.stats()
print(f"Network has {stats.active_profiles:,} active profiles")

# Look up a user
user = client.users.get_by_twitter("edoweb3")
print(f"\n@{user.username}")
print(f"  Score: {user.score}")
print(f"  Vouches received: {user.stats.vouch.received.count}")

# Get their vouches
vouches = client.vouches.for_profile(user.profile_id)
total_staked = sum(v.staked_eth for v in vouches)
print(f"  Total ETH staked on them: {total_staked:.4f}")

# Check their market
market = client.markets.get_by_profile(user.profile_id)
if market:
    print(f"  Market trust: {market.trust_percentage:.1f}%")
    print(f"  Sentiment: {market.market_sentiment}")

client.close()
```

---

## Async Support

```python
import asyncio
from ethos import AsyncEthos

async def main():
    async with AsyncEthos() as client:
        # All methods work the same, just with await
        stats = await client.profiles.stats()
        user = await client.users.get_by_twitter("vitalikbuterin")
        
        # Async iteration
        async for market in client.markets.list():
            print(market.profile_id)

asyncio.run(main())
```

---

## Configuration

### Client Options

```python
from ethos import Ethos

client = Ethos(
    client_name="my-app",    # Identifies your app to Ethos
    rate_limit=0.5,          # Seconds between requests (default: 0.1)
    timeout=30,              # Request timeout in seconds
    max_retries=3,           # Retry failed requests
)
```

### Environment Variables

```bash
export ETHOS_CLIENT_NAME="my-app"
export ETHOS_API_BASE_URL="https://api.ethos.network/api/v2"
```

---

## Error Handling

```python
from ethos import Ethos
from ethos.exceptions import (
    EthosAPIError,
    EthosNotFoundError,
    EthosRateLimitError,
)

client = Ethos()

try:
    user = client.users.get_by_twitter("nonexistent_user_12345")
except EthosNotFoundError:
    print("User not found")
except EthosRateLimitError:
    print("Rate limited - slow down")
except EthosAPIError as e:
    print(f"API error: {e.status_code} - {e.message}")
```

---

## Response Models

All responses are Pydantic models - convert to dict/JSON easily:

```python
user = client.users.get_by_twitter("username")

# Convert to dictionary
data = user.model_dump()

# Convert to JSON string
json_str = user.model_dump_json()

# Access nested data
print(user.stats.vouch.received.count)
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
- **Data scientists** building trust metrics and social graphs
- **Developers** integrating Ethos into Python applications
- **Analysts** studying Web3 social dynamics

---

## Related Projects

- [Ethos Network](https://ethos.network) - The protocol
- [Ethos API Docs](https://developers.ethos.network) - Official API documentation

---

## License

MIT License - see [LICENSE](LICENSE) for details.

---

## Contributing

Contributions welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) first.

---

## Disclaimer

This is an unofficial SDK and is not affiliated with or endorsed by Ethos Network.
