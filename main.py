#!/usr/bin/env python3
"""
Simple script to fetch Google Forms responses.
"""

import pandas as pd
import os
from forms_client import FormsClient
from read_responses import get_responses, clean_responses
from analyze_responses import guide_level_summary, topic_level_summary, topic_guide_level_summary, correlation_analysis
from few_shot_examples import prepare_few_shot_examples
from summarizer import SimpleTextSummarizer
from topic_categorizer import TopicCategorizer
from drive_uploader import upload_files_to_drive
from excel_utils import save_excel_with_autofit


FORMS = [
    {"school": "Tempe", "session_type": "Seminar",
     "sheet_title": "Seminar Feedback (Tempe) (Responses)"},
    {"school": "Tempe", "session_type": "Wonder Session",
     "sheet_title": "Wonder Session Feedback (Tempe) (Responses)"},
    {"school": "Da Vinci", "session_type": "Seminar",
     "sheet_title": "DV: Seminar (OX) Feedback (Responses)"},
    {"school": "Da Vinci", "session_type": "Wonder Session",
     "sheet_title": "Wonder Session Feedback (Da Vinci) (Responses)"},
]


def process_form(school, session_type, sheet_title, categorizer):
    """Fetch, clean, categorize, analyze and save one school/session-type form."""
    school_slug = school.lower().replace(" ", "")
    type_slug = "seminar" if session_type == "Seminar" else "wonder"
    prefix = f"{school_slug}_{type_slug}"

    print(f"\n📥 Fetching responses for {school} {session_type}...")
    df = get_responses(sheet_title)
    if df.empty:
        print(f"   ⚠️  No responses found for '{sheet_title}' - skipping.")
        return None

    print(f"\n🧼 Cleaning responses...")
    df = clean_responses(df)

    print(f"\n🎯 Categorizing topics...")
    reference_topics = categorizer.get_reference_topics(session_type)
    df = categorizer.categorize_dataframe_topics(df, reference_topics)
    categorizer.get_categorization_summary(df)

    print(f"\n📊 Analysing responses...")
    guide_stats = guide_level_summary(df)
    topic_stats = topic_level_summary(df)
    topic_guide_stats = topic_guide_level_summary(df)
    corr = correlation_analysis(df)

    print(f"\n--- {school} {session_type} Guide Stats ---")
    print(guide_stats)
    print(f"\n--- {school} {session_type} Topic Stats ---")
    print(topic_stats)
    print(f"\n--- {school} {session_type} Correlation Matrix ---")
    print(corr)

    save_excel_with_autofit(topic_stats, f'output/{prefix}_topic_stats.xlsx')
    save_excel_with_autofit(guide_stats, f'output/{prefix}_guide_stats.xlsx')
    save_excel_with_autofit(
        topic_guide_stats, f'output/{prefix}_topic_guide_stats.xlsx')
    save_excel_with_autofit(
        corr, f'output/{prefix}_correlation_matrix.xlsx', index=True)

    comparison = df[['topic', 'matched_topic']].copy()
    comparison.columns = ['Original Topic', 'Matched Topic']
    comparison = comparison.sort_values('Original Topic')
    save_excel_with_autofit(
        comparison, f'output/topic comparisons/{prefix}_topic_comparison.xlsx')

    comparison['School'] = school
    comparison['Session Type'] = session_type
    return comparison


def main():
    print("🚀 Feedback Forms Response Fetcher")
    print("-" * 40)

    categorizer = TopicCategorizer()

    comparisons_by_school = {}
    for form in FORMS:
        comparison = process_form(
            form["school"], form["session_type"], form["sheet_title"], categorizer)
        if comparison is not None:
            comparisons_by_school.setdefault(
                form["school"], []).append(comparison)

    # Combined per-school topic comparison (Seminar + Wonder Session)
    print("\n📋 Generating combined topic comparison files...")
    for school, comparisons in comparisons_by_school.items():
        school_slug = school.lower().replace(" ", "")
        combined = pd.concat(comparisons, ignore_index=True)
        combined = combined.sort_values(['Session Type', 'Original Topic'])
        save_excel_with_autofit(
            combined,
            f'output/topic comparisons/{school_slug}_combined_topic_comparison.xlsx')
    print("   💾 Saved topic comparison files")

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
