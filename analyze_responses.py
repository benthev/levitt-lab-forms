import pandas as pd
from summarizer import SimpleTextSummarizer

cols_quant = ['I felt comfortable as a student in this Seminar.',
              'I felt like my voice mattered in this Seminar.',
              'I felt like I could connect with the Guide as a person.',
              'The content of the Seminar was interesting to me.',
              'I learned a lot from the Seminar.',
              'How much did it "wow" you?', 'How much fun did you have?',
              'Did it leave you wanting to learn more about this topic?']

cols_qual = ['What is your impression of this Guide? Feel free to use 2-4 words (or phrases) to describe them.',
             'What did you learn? What will stick with you from the Seminar?',
             'What did you find most effective or enjoyable about the Guide and the Seminar they facilitated?',
             "What didn't work for you about the Guide or the Seminar they facilitated? ",
             'Let us know if you have more thoughts or feedback!']


def guide_level_summary(df):
    cols_quant_avail = [col for col in cols_quant if col in df.columns]
    stats_means = df.groupby('Guide', dropna=False)[cols_quant_avail].mean()
    stats_means['mean_overall'] = stats_means[cols_quant_avail].mean(axis=1)
    stats_counts = df.groupby(
        'Guide', dropna=False).size().reset_index(name='Count')
    stats = pd.merge(stats_means, stats_counts, on='Guide',
                     left_index=False, right_index=False)
    stats = stats.sort_values(by='mean_overall', ascending=False)

    return stats


def week_level_summary(df):
    cols_quant_avail = [col for col in cols_quant if col in df.columns]
    stats_means = df.groupby(
        'week_start', dropna=False)[cols_quant_avail].mean()
    stats_means['mean_overall'] = stats_means[cols_quant_avail].mean(axis=1)
    stats_counts = df.groupby(
        'week_start', dropna=False).size().reset_index(name='Count')
    stats = pd.merge(stats_means, stats_counts, on='week_start',
                     left_index=False, right_index=False)
    stats = stats.sort_values(by='week_start', ascending=False)

    return stats


def summarize_qualitative_feedback(df):
    cols_qual_avail = [col for col in cols_qual if col in df.columns]
    summaries = {}
    for col in cols_qual_avail:
        feedback = df[col].dropna().tolist()
        summarizer = SimpleTextSummarizer()
        summaries[col] = summarizer.summarize_texts(feedback)
    return summaries
