#!/usr/bin/env python3
"""
Simple script to fetch Google Forms responses.
"""

from forms_client import FormsClient
from read_responses import get_responses, clean_responses
from analyze_responses import guide_level_summary, week_level_summary, summarize_qualitative_feedback
from few_shot_examples import prepare_few_shot_examples
from summarizer import SimpleTextSummarizer


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
    seminar_weekly_stats.to_csv('output/seminar_weekly_stats.csv', index=False)
    wonder_weekly_stats.to_csv('output/wonder_weekly_stats.csv', index=False)
    seminar_guide_stats.to_csv('output/seminar_guide_stats.csv', index=False)
    wonder_guide_stats.to_csv('output/wonder_guide_stats.csv', index=False)
    # print(f"   💾 Saved to: {filename}")

    # Summarize qual feedback
    # Prepare few shot examples
    examples_dict = prepare_few_shot_examples(
        'input/few_shot_examples.csv', seminar_df)

    summarizer = SimpleTextSummarizer()
    summarizer.add_expert_examples(examples_dict)
    # feedback_summary = summarizer.summarize(seminar_df[1:100])


if __name__ == "__main__":
    main()
