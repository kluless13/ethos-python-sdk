"""
Basic usage example for ethos-py SDK.

This example demonstrates how to:
1. Initialize the client
2. Look up profiles by different identifiers
3. Access vouch and review data
"""

from ethos import Ethos
from ethos.exceptions import EthosNotFoundError, EthosAPIError


def main():
    # Initialize the client
    with Ethos(client_name="ethos-py-example") as client:

        profile = None

        # Example 1: Search for profiles first (more reliable)
        print("=" * 50)
        print("Searching for profiles...")

        try:
            profiles = client.profiles.search("ethereum", limit=5)
            for p in profiles:
                print(f"  {p.display_name or p.username}: score {p.score}")
                if profile is None:
                    profile = p  # Save first profile for vouch lookup
        except EthosNotFoundError:
            print("  No profiles found")
        except EthosAPIError as e:
            print(f"  API error: {e}")

        # Example 2: Get vouches for a specific profile
        # Note: The vouches endpoint requires at least one filter parameter
        print("\n" + "=" * 50)
        print("Getting vouches...")

        if profile and profile.id:
            print(f"Looking up vouches for profile {profile.id}...")
            try:
                vouch_count = 0
                for vouch in client.vouches.list(target_profile_id=profile.id, limit=5):
                    print(
                        f"  Profile {vouch.author_profile_id} vouched for {vouch.target_profile_id}"
                    )
                    if hasattr(vouch, "amount_eth") and vouch.amount_eth:
                        print(f"    Amount: {vouch.amount_eth:.4f} ETH")
                    vouch_count += 1
                    if vouch_count >= 5:
                        break
                if vouch_count == 0:
                    print("  No vouches found for this profile")
            except EthosNotFoundError:
                print("  No vouches found")
            except EthosAPIError as e:
                print(f"  Could not fetch vouches: {e}")
        else:
            print("  Skipping - no profile ID available")

        # Example 3: Get a profile by Twitter handle
        print("\n" + "=" * 50)
        print("Looking up profile by Twitter handle...")

        try:
            profile = client.profiles.get_by_twitter("trustethos")
            print(f"Found: {profile.display_name}")
            if hasattr(profile, "credibility_score") and profile.credibility_score:
                print(f"  Score: {profile.credibility_score}")
            if hasattr(profile, "vouches_received_count"):
                print(f"  Vouches received: {profile.vouches_received_count}")
        except EthosNotFoundError:
            print("  Profile not found (handle may not be registered on Ethos)")
        except EthosAPIError as e:
            print(f"  Could not find profile: {e}")

        # Example 4: Check recent activities
        print("\n" + "=" * 50)
        print("Recent network activities...")

        try:
            activities = client.activities.recent(limit=5)
            for activity in activities:
                print(f"  [{activity.type}] Profile {activity.author_profile_id}")
        except EthosNotFoundError:
            print("  No activities found")
        except EthosAPIError as e:
            print(f"  Could not fetch activities: {e}")


if __name__ == "__main__":
    main()
