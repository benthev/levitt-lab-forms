#!/usr/bin/env python3
"""
Simple script to fetch Google Forms responses.
"""

from forms_client import FormsClient
from read_responses import get_responses, clean_responses
from analyze_responses import guide_level_summary, topic_level_summary, summarize_qualitative_feedback
from few_shot_examples import prepare_few_shot_examples
from summarizer import SimpleTextSummarizer
from topic_categorizer import TopicCategorizer


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

    # Categorize response topics
    print("\\n🎯 Categorizing topics...")
    categorizer = TopicCategorizer()
    seminar_topics = categorizer.get_reference_topics("Seminar")
    wonder_topics = categorizer.get_reference_topics("Wonder Session")
    print("   📚 Processing seminar topics...")
    seminar_df = categorizer.categorize_dataframe_topics(
        seminar_df, seminar_topics
    )

    print("   🔬 Processing wonder session topics...")
    wonder_df = categorizer.categorize_dataframe_topics(
        wonder_df, wonder_topics
    )
    seminar_summary = categorizer.get_categorization_summary(
        seminar_df)
    wonder_summary = categorizer.get_categorization_summary(
        wonder_df)

    # Analyse responses
    print("\n📊 Analysing responses...")

    seminar_guide_stats = guide_level_summary(seminar_df)
    wonder_guide_stats = guide_level_summary(wonder_df)

    print("\n--- Seminar Guide Stats ---")
    print(seminar_guide_stats)
    print("\n--- Wonder Session Guide Stats ---")
    print(wonder_guide_stats)

    seminar_topic_stats = topic_level_summary(seminar_df)
    wonder_topic_stats = topic_level_summary(wonder_df)

    print("\n--- Seminar Topic Stats ---")
    print(seminar_topic_stats)
    print("\n--- Wonder Session Topic Stats ---")
    print(wonder_topic_stats)

    # Save to CSV
    seminar_topic_stats.to_csv('output/seminar_topic_stats.csv', index=False)
    wonder_topic_stats.to_csv('output/wonder_topic_stats.csv', index=False)
    seminar_guide_stats.to_csv('output/seminar_guide_stats.csv', index=False)
    wonder_guide_stats.to_csv('output/wonder_guide_stats.csv', index=False)
    # print(f"   💾 Saved to: {filename}")

    # Summarize qual feedback
    # Prepare few shot examples
    # examples_dict = prepare_few_shot_examples(
    #     'input/few_shot_examples.csv', seminar_df)

    # summarizer = SimpleTextSummarizer()
    # summarizer.add_expert_examples(examples_dict)
    # feedback_summary = summarizer.summarize(seminar_df[1:100])


if __name__ == "__main__":
    main()
