#!/usr/bin/env python3
"""
Simple script to fetch Google Forms responses.
"""

import pandas as pd
import os
from forms_client import FormsClient
from read_responses import get_responses, clean_responses
from analyze_responses import guide_level_summary, topic_level_summary, topic_guide_level_summary, summarize_qualitative_feedback, correlation_analysis
from few_shot_examples import prepare_few_shot_examples
from summarizer import SimpleTextSummarizer
from topic_categorizer import TopicCategorizer
from drive_uploader import upload_files_to_drive
from excel_utils import save_excel_with_autofit


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

    seminar_topic_guide_stats = topic_guide_level_summary(seminar_df)
    wonder_topic_guide_stats = topic_guide_level_summary(wonder_df)

    # Save to Excel
    save_excel_with_autofit(seminar_topic_stats,
                            'output/seminar_topic_stats.xlsx')
    save_excel_with_autofit(
        wonder_topic_stats, 'output/wonder_topic_stats.xlsx')
    save_excel_with_autofit(seminar_guide_stats,
                            'output/seminar_guide_stats.xlsx')
    save_excel_with_autofit(
        wonder_guide_stats, 'output/wonder_guide_stats.xlsx')
    save_excel_with_autofit(seminar_topic_guide_stats,
                            'output/seminar_topic_guide_stats.xlsx')
    save_excel_with_autofit(
        wonder_topic_guide_stats, 'output/wonder_topic_guide_stats.xlsx')
    # print(f"   💾 Saved to: {filename}")

    # Correlation metrics
    seminar_corr = correlation_analysis(seminar_df)
    wonder_corr = correlation_analysis(wonder_df)

    print("\n--- Seminar Correlation Matrix ---")
    print(seminar_corr)
    print("\n--- Wonder Session Correlation Matrix ---")
    print(wonder_corr)

    save_excel_with_autofit(
        seminar_corr, 'output/seminar_correlation_matrix.xlsx', index=True)
    save_excel_with_autofit(
        wonder_corr, 'output/wonder_correlation_matrix.xlsx', index=True)

    # Generate topic comparison CSVs
    print("\n📋 Generating topic comparison CSVs...")
    seminar_comparison = seminar_df[['topic', 'matched_topic']].copy()
    seminar_comparison.columns = ['Original Topic', 'Matched Topic']
    seminar_comparison = seminar_comparison.sort_values('Original Topic')
    save_excel_with_autofit(
        seminar_comparison, 'output/topic comparisons/seminar_topic_comparison.xlsx')

    wonder_comparison = wonder_df[['topic', 'matched_topic']].copy()
    wonder_comparison.columns = ['Original Topic', 'Matched Topic']
    wonder_comparison = wonder_comparison.sort_values('Original Topic')
    save_excel_with_autofit(
        wonder_comparison, 'output/topic comparisons/wonder_topic_comparison.xlsx')

    # Combined comparison
    seminar_comparison['Session Type'] = 'Seminar'
    wonder_comparison['Session Type'] = 'Wonder Session'
    combined_comparison = pd.concat(
        [seminar_comparison, wonder_comparison], ignore_index=True)
    combined_comparison = combined_comparison.sort_values(
        ['Session Type', 'Original Topic'])
    save_excel_with_autofit(
        combined_comparison, 'output/topic comparisons/combined_topic_comparison.xlsx')
    print(f"   💾 Saved topic comparison files")

    # Summarize qual feedback
    # Prepare few shot examples
    # examples_dict = prepare_few_shot_examples(
    #     'input/few_shot_examples.csv', seminar_df)

    # summarizer = SimpleTextSummarizer()
    # summarizer.add_expert_examples(examples_dict)
    # feedback_summary = summarizer.summarize(seminar_df[1:100])

    # Upload files to Google Drive
    drive_folder_id = os.getenv('DRIVE_FOLDER_ID')
    if drive_folder_id:
        upload_files_to_drive(folder_id=drive_folder_id)
    else:
        print("\n⚠️  DRIVE_FOLDER_ID not set in .env - skipping upload to Google Drive")
        print("   To enable uploads, add DRIVE_FOLDER_ID=<your_folder_id> to .env")


if __name__ == "__main__":
    main()
