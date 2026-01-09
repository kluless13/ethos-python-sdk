"""
Async usage example for ethos-py SDK.

This example demonstrates how to use the async client
for concurrent requests.
"""

import asyncio
from ethos import AsyncEthos


async def main():
    async with AsyncEthos(client_name="ethos-py-async-example") as client:

        # Fetch multiple profiles concurrently
        print("Fetching profiles concurrently...")

        # Search for profiles
        profiles = await client.profiles.search("crypto", limit=5)

        # Fetch vouches for each profile concurrently
        tasks = [client.vouches.for_profile(p.id) for p in profiles]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        for profile, vouches in zip(profiles, results):
            if isinstance(vouches, Exception):
                print(f"  {profile.display_name}: Error fetching vouches")
            else:
                print(f"  {profile.display_name}: {len(vouches)} vouches")


if __name__ == "__main__":
    asyncio.run(main())
