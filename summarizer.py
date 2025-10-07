import pandas as pd
from openai import OpenAI
import json
from typing import List, Dict
import os
from dotenv import load_dotenv

load_dotenv()


class SimpleTextSummarizer:
    def __init__(self, api_key: str = os.getenv("OPENAI_API_KEY")):
        if api_key is None:
            raise ValueError(
                "API key must be provided either as argument or OPENAI_API_KEY environment variable")
        self.client = OpenAI(
            # This is the default and can be omitted
            api_key=api_key
        )
        self.expert_examples = []

    def add_expert_examples(self, examples: List[Dict]):
        """
        Add expert examples for few-shot learning
        Format: [{"texts": ["text1", "text2"], "summary": "expert summary"}]
        """
        self.expert_examples = examples

    def create_prompt(self, texts: List[str], is_positive: bool) -> str:
        """Create prompt with few-shot examples"""
        prompt = ("You are modelling an expert at summarizing feedback for separate student guides (teachers/educators). " +
                  "We want you to provide insightful but tactful feedback in two forms: positive and constructive." +
                  "You will summarize feedback into concise statements, separated by guide and type (positive/constructive), based on provided texts, " +
                  "which will be separate (but possibly overlapping) for positive and constructive feedback statements and for each student guide.")

        # Add expert examples
        if is_positive:
            texts_col = "positive_texts"
            
        else:
            texts_col = "constructive_texts"
        for i, example in enumerate(self.expert_examples, start=1):
            prompt += f"Example {i}:\n"
            prompt += "Texts to summarize:\n"
            for j, text in enumerate(example[texts_col], 1):
                prompt += f"- {text}\n"
            prompt += f"\nExpert Summary: {example['summary']}\n\n"

        # Add current task
        prompt += "Now summarize these texts:\n"
        for i, text in enumerate(texts, 1):
            prompt += f"- {text}\n"

        prompt += "\nProvide a concise summary:"
        return prompt

    def summarize_texts(self, texts: List[str]) -> str:
        """Summarize a list of texts"""
        prompt = self.create_prompt(texts)

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300,
                temperature=0.3
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"Error: {str(e)}"

    def process_dataframe(self, df: pd.DataFrame, text_column: str) -> Dict:
        """Process pandas DataFrame column and return summary"""
        texts = df[text_column].dropna().tolist()

        print(f"Processing {len(texts)} texts...")

        # Summarize all texts at once
        summary = self.summarize_texts(texts)

        return {
            "total_items": len(texts),
            "summary": summary
        }
