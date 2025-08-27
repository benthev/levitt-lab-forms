import gc
import pandas as pd
import pygsheets
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()


def get_responses(title, worksheet="Form Responses 1"):
    gc = pygsheets.authorize(service_file=os.getenv("SERVICE_ACCOUNT_FILE"))
    sheet = gc.open(title)
    wks = sheet.worksheet_by_title("Form Responses 1")
    all_records = wks.get_all_records()
    df = pd.DataFrame(all_records)
    if df.empty:
        print(f"No responses found in '{title}'.")
    else:
        print(f"✅ Found {len(df)} responses from '{title}' ")

    return df


def attribute_topics(df):
    return df


def clean_responses(df):
    # Convert Timestamp to datetime
    df['Timestamp'] = pd.to_datetime(df['Timestamp'], errors='coerce')
    df['week'] = df['Timestamp'].dt.isocalendar().week
    df['year-week'] = df['Timestamp'].dt.strftime('%Y-%W')

    # Scale certain columns from base-5 to base-10 for responses before Aug 13, 2025
    cols_to_scale = ['I felt comfortable as a student in this Seminar.',
                     'I felt like my voice mattered in this Seminar.',
                     'I felt like I could connect with the Guide as a person.',
                     'The content of the Seminar was interesting to me.']
    cols_to_scale = [col for col in cols_to_scale if col in df.columns]
    df.loc[df['Timestamp'] < datetime(
        2025, 8, 13), cols_to_scale] = df.loc[df['Timestamp'] < datetime(2025, 8, 13), cols_to_scale]*2

    # Drop columns that are completely empty
    df = df.replace(r'^\s*$', pd.NA, regex=True)
    df = df.dropna(axis=1, how='all')

    # Convert quant questions to numeric if not already
    cols_quant = ['I felt comfortable as a student in this Seminar.',
                  'I felt like my voice mattered in this Seminar.',
                  'I felt like I could connect with the Guide as a person.',
                  'The content of the Seminar was interesting to me.',
                  'I learned a lot from the Seminar.',
                  'How much did it "wow" you?', 'How much fun did you have?',
                  'Did it leave you wanting to learn more about this topic?']
    cols_quant = [col for col in cols_quant if col in df.columns]
    # df[cols_quant] = df[cols_quant].apply(pd.to_numeric, errors='coerce')
    df = df.astype({col: 'Int64' for col in cols_quant})
    print(df[cols_quant].describe())

    # Attribute Guides
    cols_guide = ["What was the name of the Guide who delivered your Seminar?",
                  "What was the name of the Guide who delivered your Wonder Session?"]
    cols_guide = [col for col in cols_guide if col in df.columns]
    df['Guide'] = df[cols_guide[0]]

    return df
