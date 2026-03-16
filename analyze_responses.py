import pandas as pd
from summarizer import SimpleTextSummarizer

cols_quant = ['I felt like my voice mattered in this Seminar.',
              'The content of the Seminar was interesting to me.',
              'I learned a lot from the Seminar.', 'How much fun did you have?',
              'Did it leave you wanting to learn more about this topic?']

cols_qual = ['Let us know if you have more thoughts or feedback!']


def quant_summary(df, agg_cols):
    cols_quant_avail = [col for col in cols_quant if col in df.columns]
    stats_means = df.groupby(agg_cols, dropna=False)[
        cols_quant_avail].mean().round(3)
    stats_means['mean_overall'] = stats_means[cols_quant_avail].mean(
        axis=1).round(3)
    stats_counts = df.groupby(
        agg_cols, dropna=False).size().reset_index(name='count')
    stats = pd.merge(stats_means, stats_counts, on=agg_cols,
                     left_index=False, right_index=False)
    # Filter to topics with at least 5 responses
    stats = stats[stats['count'] >= 5]
    stats = stats.sort_values(by='mean_overall', ascending=False)

    return stats


def guide_level_summary(df):
    summary = all_feedback_combined(df, 'Guide')
    return summary


def topic_level_summary(df):
    summary = all_feedback_combined(df, 'matched_topic')
    return summary


def topic_guide_level_summary(df):
    summary = all_feedback_combined(df, ['matched_topic', 'Guide'])
    return summary


def qual_summary(df, agg_cols):
    cols_qual_avail = [col for col in cols_qual if col in df.columns]

    summarizer = SimpleTextSummarizer()
    agg_df = df.groupby(agg_cols, dropna=False).apply(
        lambda group: summarizer.summarize_texts(text_list) if (
            text_list := group[cols_qual_avail].stack().dropna().tolist()) else ''
    ).reset_index(name='qual_summary_by_llm')
    print(agg_df)
    return agg_df


def all_feedback_combined(df, agg_cols):
    stats = quant_summary(df, agg_cols)
    qual = qual_summary(df, agg_cols)
    merged_df = pd.merge(stats, qual, on=agg_cols, how='left')
    return merged_df


def correlation_analysis(df):
    cols_quant_avail = [col for col in cols_quant if col in df.columns]
    corr_matrix = df[cols_quant_avail].corr()
    return corr_matrix
