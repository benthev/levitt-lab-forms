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
    stats = quant_summary(df, 'Guide')
    return stats


def topic_level_summary(df):
    stats = quant_summary(df, 'matched_topic')
    return stats


def topic_guide_level_summary(df):
    stats = quant_summary(df, ['matched_topic', 'Guide'])
    return stats


def summarize_qualitative_feedback(df, agg_cols):
    cols_qual_avail = [col for col in cols_qual if col in df.columns]

    if len(cols_qual_avail) > 1:
        df['qual_feedback'] = df[cols_qual_avail].fillna(
            '').agg(';'.join, axis=1)
    else:
        df['qual_feedback'] = df[cols_qual_avail[0]].fillna(
            '') if cols_qual_avail else ''

    agg_df = df.groupby(agg_cols, dropna=False)['qual_feedback'].apply(
        lambda x: '; '.join(x)).reset_index()

    # summaries = {}
    # for col in cols_qual_avail:
    #     feedback = df[col].dropna().tolist()
    #     summarizer = SimpleTextSummarizer()
    #     summaries[col] = summarizer.summarize_texts(feedback)
    return agg_df


def correlation_analysis(df):
    cols_quant_avail = [col for col in cols_quant if col in df.columns]
    corr_matrix = df[cols_quant_avail].corr()
    return corr_matrix
