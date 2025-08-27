import pandas as pd
from datetime import datetime
import auth
import config


class FormsClient:
    """Simple client to fetch Google Forms responses."""

    def __init__(self):
        self.forms_service, self.sheets_service = auth.get_authenticated_services()

    def get_form_info(self, form_id):
        """Get basic information about the form."""
        if not self.forms_service:
            return None

        try:
            form = self.forms_service.forms().get(formId=form_id).execute()
            return {
                'title': form.get('info', {}).get('title', 'Unknown'),
                'description': form.get('info', {}).get('description', ''),
                'questions': len(form.get('items', []))
            }
        except Exception as e:
            print(f"Error getting form info: {e}")
            return None

    def get_responses(self, form_id):
        """Get all responses from the form."""
        if not self.forms_service:
            return []

        try:
            # Get form structure first
            form = self.forms_service.forms().get(formId=form_id).execute()

            # Get responses
            response = self.forms_service.forms().responses().list(formId=form_id).execute()
            responses = response.get('responses', [])

            print(f"Found {len(responses)} responses")
            return self._process_responses(form, responses)

        except Exception as e:
            print(f"Error getting responses: {e}")
            return []

    def get_responses_from_sheet(self, spreadsheet_id, sheet_range='Form Responses 1'):
        """Alternative: Get responses from the linked Google Sheet."""
        if not self.sheets_service:
            return pd.DataFrame()

        try:
            result = self.sheets_service.spreadsheets().values().get(
                spreadsheetId=spreadsheet_id,
                range=sheet_range
            ).execute()

            values = result.get('values', [])
            if not values:
                print("No data found in sheet")
                return pd.DataFrame()
            # print(values)

            headers = values[0]
            print(len(headers))
            data_rows = values[1:]
            print(data_rows[1])
            print(len(data_rows[1]))
            print(len(data_rows))

            # Convert to DataFrame
            df = pd.DataFrame(values[1:], columns=values[0])
            print(f"Found {len(df)} responses in sheet")
            return df

        except Exception as e:
            print(f"Error getting sheet data: {e}")
            return pd.DataFrame()

    def _process_responses(self, form, responses):
        """Process raw API responses into a readable format."""
        if not responses:
            return pd.DataFrame()

        # Build question mapping
        questions = {}
        for item in form.get('items', []):
            if 'questionItem' in item:
                question_id = item['questionItem']['question']['questionId']
                questions[question_id] = item['title']

        # Process each response
        processed_responses = []
        for response in responses:
            row = {
                'response_id': response.get('responseId', ''),
                'timestamp': response.get('lastSubmittedTime', ''),
            }

            # Add answers
            for question_id, answer_data in response.get('answers', {}).items():
                question_text = questions.get(
                    question_id, f'Question_{question_id}')

                # Extract answer based on type
                if 'textAnswers' in answer_data:
                    answers = [
                        ta.get('value', '') for ta in answer_data['textAnswers'].get('answers', [])]
                    row[question_text] = '; '.join(answers)
                elif 'fileUploadAnswers' in answer_data:
                    row[question_text] = 'File uploaded'
                else:
                    row[question_text] = str(answer_data)

            processed_responses.append(row)

        return pd.DataFrame(processed_responses)

    def save_to_csv(self, df, filename=None):
        """Save responses to CSV file."""
        if df.empty:
            print("No data to save")
            return

        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{config.OUTPUT_DIR}/form_responses_{timestamp}.csv"

        df.to_csv(filename, index=False)
        print(f"Saved {len(df)} responses to {filename}")
        return filename
