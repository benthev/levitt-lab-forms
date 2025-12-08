import pandas as pd
from openai import OpenAI
import json
from typing import List, Dict, Optional, Tuple
import os
from dotenv import load_dotenv

load_dotenv()


class TopicCategorizer:
    def __init__(self, api_key: str = os.getenv("OPENAI_API_KEY"), cache_file: str = "topic_cache.json", use_cache: bool = True):
        if api_key is None:
            raise ValueError(
                "API key must be provided either as argument or OPENAI_API_KEY environment variable")
        self.client = OpenAI(api_key=api_key)
        self.cache_file = cache_file
        self.use_cache = use_cache
        self.topic_cache = self._load_cache() if use_cache else {}

    def _load_cache(self) -> Dict[str, Tuple[Optional[str], Optional[str]]]:
        """Load cached topic mappings from file"""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r') as f:
                    cache_data = json.load(f)
                    # Convert list back to tuple for consistency
                    return {k: tuple(v) if v else (None, None) for k, v in cache_data.items()}
            except Exception as e:
                print(f"Warning: Could not load cache file: {e}")
                return {}
        return {}

    def _save_cache(self):
        """Save topic mappings to cache file"""
        if not self.use_cache:
            return
        try:
            # Convert tuples to lists for JSON serialization
            cache_data = {k: list(v) if v else None for k, v in self.topic_cache.items()}
            with open(self.cache_file, 'w') as f:
                json.dump(cache_data, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save cache file: {e}")

    def _get_cache_key(self, topic: str, reference_topics: List[str]) -> str:
        """Generate a cache key for a topic and reference topics combination"""
        # Create a stable key based on topic and sorted reference topics
        ref_topics_str = "|".join(sorted(reference_topics))
        return f"{topic}:::{ref_topics_str}"

    def create_categorization_prompt(self, topic: str, reference_topics: List[str]) -> str:
        """Create a prompt to find the closest matching topic"""
        prompt = (
            "You are an expert at categorizing and matching topics. "
            "Given a topic and a list of reference topics, find the closest semantic match. "
            "Consider synonyms, related concepts, and broader/narrower topic relationships.\n\n"
            f"Topic to categorize: '{topic}'\n\n"
            "Reference topics to match against:\n"
        )

        for i, ref_topic in enumerate(reference_topics, 1):
            prompt += f"{i}. {ref_topic}\n"

        prompt += (
            "\nPlease respond with only the number (1, 2, 3, etc.) of the closest matching reference topic. "
            "If no reasonable match exists, respond with '0'.\n\n"
            "Number:"
        )

        return prompt

    def find_closest_topic(self, topic: str, reference_topics: List[str]) -> Tuple[Optional[str], Optional[str]]:
        """Find the closest matching topic from the reference list"""
        if not topic or not reference_topics:
            return None, None

        # Check cache first if enabled
        if self.use_cache:
            cache_key = self._get_cache_key(topic, reference_topics)
            if cache_key in self.topic_cache:
                print(f"    ✓ Cache hit for '{topic}'")
                return self.topic_cache[cache_key]

        prompt = self.create_categorization_prompt(topic, reference_topics)

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=10,
                temperature=0.1
            )

            result = response.choices[0].message.content.strip()

            try:
                match_index = int(result)
                if match_index == 0:
                    matched_result = (None, "no_match")
                elif 1 <= match_index <= len(reference_topics):
                    # Simple confidence based on temperature and successful match
                    confidence = "high" if len(
                        reference_topics) <= 10 else "medium"
                    matched_result = (reference_topics[match_index - 1], confidence)
                else:
                    matched_result = (None, "invalid_response")
                
                # Cache the result if caching is enabled
                if self.use_cache:
                    cache_key = self._get_cache_key(topic, reference_topics)
                    self.topic_cache[cache_key] = matched_result
                    self._save_cache()
                return matched_result
            except ValueError:
                matched_result = (None, "parse_error")
                if self.use_cache:
                    cache_key = self._get_cache_key(topic, reference_topics)
                    self.topic_cache[cache_key] = matched_result
                    self._save_cache()
                return matched_result

        except Exception as e:
            print(f"Error categorizing topic '{topic}': {str(e)}")
            matched_result = (None, "api_error")
            if self.use_cache:
                cache_key = self._get_cache_key(topic, reference_topics)
                self.topic_cache[cache_key] = matched_result
                self._save_cache()
            return matched_result

    def categorize_dataframe_topics(self, df: pd.DataFrame, reference_topics: List[str],
                                    topic_column: str = 'topic') -> pd.DataFrame:
        """Categorize all topics in a dataframe against reference topics"""
        if topic_column not in df.columns:
            raise ValueError(f"Column '{topic_column}' not found in dataframe")

        df_copy = df.copy()
        df_copy['matched_topic'] = None
        df_copy['match_confidence'] = None

        unique_topics = df_copy[topic_column].dropna().unique()
        topic_mapping = {}
        confidence_mapping = {}

        print(f"Processing {len(unique_topics)} unique topics...")

        for i, topic in enumerate(unique_topics, 1):
            print(f"  {i}/{len(unique_topics)}: '{topic}'")
            matched_topic, confidence = self.find_closest_topic(
                topic, reference_topics)
            topic_mapping[topic] = matched_topic
            confidence_mapping[topic] = confidence

        # Apply mappings to dataframe
        df_copy['matched_topic'] = df_copy[topic_column].map(topic_mapping)
        df_copy['match_confidence'] = df_copy[topic_column].map(
            confidence_mapping)

        return df_copy

    def get_categorization_summary(self, df: pd.DataFrame, topic_column: str = 'topic',
                                   matched_column: str = 'matched_topic') -> Dict:
        """Get summary statistics of the topic categorization"""
        # Ensure columns exist
        if topic_column not in df.columns:
            raise ValueError(f"Column '{topic_column}' not found in dataframe")
        if matched_column not in df.columns:
            raise ValueError(
                f"Column '{matched_column}' not found in dataframe")

        # Calculate basic stats
        total_topics = df[topic_column].dropna().nunique()
        matched_topics = df[matched_column].dropna().nunique()
        unmatched_count = df[df[matched_column].isna(
        ) & df[topic_column].notna()].shape[0]

        # Get unmatched topics
        unmatched_mask = df[matched_column].isna() & df[topic_column].notna()
        unmatched_topics = df[unmatched_mask][topic_column].unique(
        ).tolist() if unmatched_mask.any() else []

        # Get topic mapping counts (handle potential NaN values)
        try:
            mapping_counts = df.groupby(
                [topic_column, matched_column], dropna=False).size().reset_index(name='count')
        except Exception as e:
            print(f"Warning: Could not generate mapping details: {e}")
            mapping_counts = pd.DataFrame()

        # Print unmatched topics if any exist
        if unmatched_topics:
            print(f"\n⚠️  Unmatched topics ({len(unmatched_topics)}):")
            for topic in sorted(unmatched_topics):
                print(f"  - '{topic}'")
        else:
            print("\n✅ All topics were successfully matched!")

        print(str(unmatched_count) + " unmatched entries / " +
              str(total_topics) + " total entries")

        return {
            'total_unique_topics': total_topics,
            'total_unique_matched_topics': matched_topics,
            'unmatched_entries': unmatched_count,
            'unmatched_topics': unmatched_topics,
            'mapping_details': mapping_counts.to_dict('records') if not mapping_counts.empty else []
        }

    def get_reference_topics(self, column, filepath="https://docs.google.com/spreadsheets/d/1i5OZu7UVwcwQpYk7R8gSwvlW3FigO906etXPYG4t_Ec/export?format=csv&gid=0"):
        df = pd.read_csv(filepath)
        df["week_start"] = pd.to_datetime(
            df["Week Start"], format="%Y/%m/%d", errors='coerce')
        df = df[df["week_start"] <= pd.Timestamp.today()]
        topics = df[column].dropna().tolist()
        topics = [topic for topic in topics if not any(
            substring in topic.upper() for substring in ["NO WONDER SESSION", "NO SEMINAR"])]
        return topics
