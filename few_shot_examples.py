import pandas as pd
from typing import List, Dict


def read_few_shot_examples(file_path: str) -> List[Dict]:
    """Read few-shot examples from a JSON file"""
    with open(file_path, "r") as f:
        examples = json.load(f)
    return examples


def prepare_few_shot_examples(df: pd.DataFrame, text_column: str) -> List[Dict]:
    """Prepare few-shot examples from a DataFrame"""
    examples = []
    for _, row in df.iterrows():
        example = {
            "texts": [row[text_column]],
            "summary": ""  # Placeholder for expert summary
        }
        examples.append(example)
    return examples
