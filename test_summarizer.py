from summarizer import SimpleTextSummarizer

SAMPLE_TEXTS = [
    "The seminar was really engaging and I loved the hands-on activities.",
    "I felt like my questions were taken seriously by the guide.",
    "The pace was a bit too fast and I couldn't keep up with some sections.",
    "Great energy from the presenter! Really made the topic come alive.",
    "I wish there had been more time for discussion at the end.",
    "The examples used were very relatable and easy to understand.",
    "Some of the slides were hard to read from the back of the room.",
    "I learned things I had never thought about before. Very eye-opening.",
    "The guide was clearly passionate about the subject which was motivating.",
    "Would have appreciated more interactive elements throughout.",
]


def test_summarizer():
    summarizer = SimpleTextSummarizer()
    summary = summarizer.summarize_texts(SAMPLE_TEXTS)
    print("Summary:\n", summary)
    return summary


if __name__ == "__main__":
    test_summarizer()
