import pandas as pd
from typing import List, Dict

cols_positive = ["What did you find most effective or enjoyable about the Guide and the Seminar they facilitated?",
                 "What is your impression of this Guide? Feel free to use 2-4 words (or phrases) to describe them.",
                 "Let us know if you have more thoughts or feedback!"]
cols_constructive = ["What didn't work for you about the Guide or the Seminar they facilitated? ",
                     "What is your impression of this Guide? Feel free to use 2-4 words (or phrases) to describe them.",
                     "Let us know if you have more thoughts or feedback!"]


def read_few_shot_examples(file_path: str) -> pd.DataFrame:
    """Read few-shot examples from a CSV file"""
    df = pd.read_csv(file_path)
    return df


def combine_few_shot_examples(examples_df: pd.DataFrame, feedback_df: pd.DataFrame) -> List[Dict]:
    """Combine few-shot examples from examples df and feedback df"""
    cols_positive_avail = [
        col for col in cols_positive if col in feedback_df.columns]
    cols_constructive_avail = [
        col for col in cols_constructive if col in feedback_df.columns]

    # Reshape examples so we have separate cols for positive & constructive feedback
    examples_reshaped_df = examples_df.pivot_table(
        index=['Guide', 'date_max'],  # Group by Guide and date
        columns='feedback_type',
        values='feedback_summary',
        # Join multiple feedback summaries with separator
        aggfunc=lambda x: ' | '.join(x)
    ).reset_index()

    # Clean up column names
    # Remove the 'feedback_type' name from columns
    examples_reshaped_df.columns.name = None
    examples_reshaped_df.columns = [
        'Guide', 'date_max', 'constructive_feedback_summary', 'positive_feedback_summary']

    # Merge 2 datasets w/ fake 2nd column
    feedback_df['temp'] = 'A'
    examples_reshaped_df['temp'] = 'B'
    combined_df = pd.merge(feedback_df, examples_reshaped_df, on=[
                           'Guide', 'temp'], how='outer')

    combined_df.dropna(subset=['Guide'], inplace=True)
    combined_df = combined_df[combined_df['Guide'] != 'N/A']

    cols_to_keep = (cols_positive_avail+cols_constructive_avail +
                    ['date_max', 'constructive_feedback_summary', 'positive_feedback_summary'])

    feedback = combined_df.groupby('Guide').agg(
        {col: lambda x: x.dropna().tolist() for col in cols_to_keep}).reset_index()
    feedback['positive_texts'] = feedback[cols_positive_avail].sum(
        axis=1)
    feedback['constructive_texts'] = feedback[cols_constructive_avail].sum(
        axis=1)
    feedback_examples = feedback[[
        'Guide', 'positive_texts', 'constructive_texts', 'constructive_feedback_summary', 'positive_feedback_summary', 'date_max']].to_dict('records')

    return feedback_examples


def prepare_few_shot_examples(file_path: str, feedback_df: pd.DataFrame) -> List[Dict]:
    examples_df = read_few_shot_examples(file_path)
    examples_dict = combine_few_shot_examples(examples_df, feedback_df)
    return examples_dict
