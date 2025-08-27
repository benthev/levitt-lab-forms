#!/usr/bin/env python3
"""
Simple script to fetch Google Forms responses.
"""

from forms_client import FormsClient
from read_responses import get_responses, clean_responses
from analyze_responses import guide_level_summary, week_level_summary


def main():
    print("🚀 Feedback Forms Response Fetcher")
    print("-" * 40)

    # Fetch responses
    print(f"\n📥 Fetching responses...")
    seminar_df = get_responses(
        "Seminar Feedback (Responses)")

    wonder_df = get_responses(
        "Wonder Session Feedback (Responses)")

    # Clean responses
    print("\n🧼 Cleaning responses...")
    seminar_df = clean_responses(seminar_df)
    wonder_df = clean_responses(wonder_df)

    # Analyse responses
    print("\n📊 Analysing responses...")

    seminar_guide_stats = guide_level_summary(seminar_df)
    wonder_guide_stats = guide_level_summary(wonder_df)

    print("\n--- Seminar Guide Stats ---")
    print(seminar_guide_stats)
    print("\n--- Wonder Session Guide Stats ---")
    print(wonder_guide_stats)

    seminar_weekly_stats = week_level_summary(seminar_df)
    wonder_weekly_stats = week_level_summary(wonder_df)

    print("\n--- Seminar Weekly Stats ---")
    print(seminar_weekly_stats)
    print("\n--- Wonder Session Weekly Stats ---")
    print(wonder_weekly_stats)

    # Save to CSV
    # filename = client.save_to_csv(responses_df)
    # print(f"   💾 Saved to: {filename}")


if __name__ == "__main__":
    main()
