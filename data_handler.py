import pandas as pd
import json
import os
from typing import List, Dict

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
FEEDBACK_FILE = os.path.join(DATA_DIR, "feedback.xlsx")
DISEASE_DATA_FILE = os.path.join(DATA_DIR, "diseases.json")

class DataHandler:
    def __init__(self):
        self._ensure_data_dir()
        self.diseases = self._load_diseases()

    def _ensure_data_dir(self):
        if not os.path.exists(DATA_DIR):
            os.makedirs(DATA_DIR)

    def _load_diseases(self) -> List[Dict]:
        if not os.path.exists(DISEASE_DATA_FILE):
            # Create a mock dataset if it doesn't exist
            mock_data = [
                {
                    "name": "Diabetes Type 2",
                    "symptoms": ["increased thirst", "frequent urination", "hunger", "fatigue"],
                    "recommendations": {
                        "eat": ["Leafy greens", "Whole grains", "Fatty fish", "Beans"],
                        "avoid": ["Sugary drinks", "White bread", "Processed foods"],
                        "reason": "Low glycemic index foods help maintain stable blood sugar levels."
                    }
                },
                {
                    "name": "Hypertension",
                    "symptoms": ["headache", "shortness of breath", "nosebleeds"],
                    "recommendations": {
                        "eat": ["Fruits", "Vegetables", "Whole grains", "Low-fat dairy"],
                        "avoid": ["Salt", "Red meat", "Alcohol", "Saturated fats"],
                        "reason": "DASH diet helps lower blood pressure by reducing sodium intake."
                    }
                }
            ]
            with open(DISEASE_DATA_FILE, 'w') as f:
                json.dump(mock_data, f, indent=4)
            return mock_data
        
        with open(DISEASE_DATA_FILE, 'r') as f:
            return json.load(f)

    def save_feedback(self, feedback_data: dict):
        df = pd.DataFrame([feedback_data])
        if os.path.exists(FEEDBACK_FILE):
            existing_df = pd.read_excel(FEEDBACK_FILE)
            df = pd.concat([existing_df, df], ignore_index=True)
        
        df.to_excel(FEEDBACK_FILE, index=False)

    def get_disease_info(self, disease_name: str):
        for disease in self.diseases:
            if disease["name"].lower() == disease_name.lower():
                return disease
        return None

    def search_diseases(self, query: str) -> List[str]:
        query = query.lower()
        return [d["name"] for d in self.diseases if query in d["name"].lower()]
