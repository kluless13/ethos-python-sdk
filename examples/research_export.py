"""
Research example: Building a vouch network dataset.

This example shows how to use the SDK to collect data
for analyzing the Ethos vouch network.
"""

import csv
from pathlib import Path
from ethos import Ethos


def export_vouch_network(output_path: str = "vouch_network.csv", limit: int = 1000):
    """
    Export vouch relationships to a CSV file.

    Creates a file with columns:
    - voucher_id: Profile who gave the vouch
    - target_id: Profile who received the vouch
    - amount_eth: Amount staked in ETH
    - is_active: Whether vouch is currently active
    """

    print(f"Collecting vouches (limit: {limit})...")

    with Ethos(client_name="ethos-research") as client:
        vouches_data = []

        for i, vouch in enumerate(client.vouches.list(limit=limit)):
            vouches_data.append(
                {
                    "vouch_id": vouch.id,
                    "voucher_id": vouch.author_profile_id,
                    "target_id": vouch.target_profile_id,
                    "amount_eth": vouch.amount_eth,
                    "is_active": vouch.is_active,
                }
            )

            if (i + 1) % 100 == 0:
                print(f"  Collected {i + 1} vouches...")

        print(f"Total vouches collected: {len(vouches_data)}")

    # Write to CSV
    output = Path(output_path)
    with output.open("w", newline="") as f:
        if vouches_data:
            writer = csv.DictWriter(f, fieldnames=vouches_data[0].keys())
            writer.writeheader()
            writer.writerows(vouches_data)

    print(f"Exported to {output_path}")
    return vouches_data


def export_profiles_with_twitter(output_path: str = "profiles_twitter.csv", limit: int = 500):
    """
    Export profiles that have linked Twitter accounts.

    Useful for cross-platform analysis between Ethos and Twitter.
    """

    print(f"Collecting profiles with Twitter links...")

    with Ethos(client_name="ethos-research") as client:
        profiles_data = []

        for i, profile in enumerate(client.profiles.list(limit=limit)):
            twitter = profile.twitter_handle
            if twitter:
                profiles_data.append(
                    {
                        "profile_id": profile.id,
                        "twitter_handle": twitter,
                        "score": profile.score,
                        "score_level": profile.score_level,
                        "vouches_received": profile.vouches_received_count,
                        "vouches_given": profile.vouches_given_count,
                        "reviews_positive": profile.reviews_positive,
                        "reviews_negative": profile.reviews_negative,
                    }
                )

            if (i + 1) % 100 == 0:
                print(f"  Processed {i + 1} profiles, found {len(profiles_data)} with Twitter...")

        print(f"Total profiles with Twitter: {len(profiles_data)}")

    # Write to CSV
    output = Path(output_path)
    with output.open("w", newline="") as f:
        if profiles_data:
            writer = csv.DictWriter(f, fieldnames=profiles_data[0].keys())
            writer.writeheader()
            writer.writerows(profiles_data)

    print(f"Exported to {output_path}")
    return profiles_data


def analyze_score_distribution():
    """
    Analyze the distribution of credibility scores.
    """

    print("Analyzing score distribution...")

    with Ethos(client_name="ethos-research") as client:
        scores = {
            "untrusted": 0,
            "questionable": 0,
            "neutral": 0,
            "reputable": 0,
            "exemplary": 0,
        }

        total = 0
        for profile in client.profiles.list(limit=1000):
            scores[profile.score_level] += 1
            total += 1

        print(f"\nScore Distribution (n={total}):")
        print("-" * 30)
        for level, count in scores.items():
            pct = (count / total * 100) if total > 0 else 0
            print(f"  {level:12} : {count:4} ({pct:5.1f}%)")


if __name__ == "__main__":
    # Export vouch network
    export_vouch_network(limit=100)
    print()

    # Export profiles with Twitter
    export_profiles_with_twitter(limit=200)
    print()

    # Analyze score distribution
    analyze_score_distribution()
