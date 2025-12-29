"""
Dataset Quality Validator for Diabetes Digital Twin
This script helps you assess if a dataset is suitable for building the digital twin.
"""

import pandas as pd
import numpy as np
from datetime import datetime
import json

class DatasetValidator:
    def __init__(self, dataset_path):
        """
        Initialize validator with dataset path
        Args:
            dataset_path: Path to CSV file containing patient data
        """
        self.dataset_path = dataset_path
        self.df = None
        self.report = {}
    
    def load_data(self):
        """Load the dataset"""
        try:
            self.df = pd.read_csv(self.dataset_path)
            print(f"✓ Successfully loaded dataset: {len(self.df)} records")
            return True
        except Exception as e:
            print(f"✗ Error loading dataset: {e}")
            return False
    
    def check_required_fields(self):
        """Check if dataset has minimum required fields"""
        required_fields = {
            'patient_id': 'Unique identifier for each patient',
            'glucose_mgdl': 'Blood glucose readings in mg/dL',
            'timestamp': 'When the measurement was taken'
        }
        
        recommended_fields = {
            'age': 'Patient age',
            'hba1c': 'HbA1c percentage',
            'weight_kg': 'Patient weight',
            'carbs_grams': 'Carbohydrate intake',
            'insulin_units': 'Insulin dosage'
        }
        
        print("\n=== FIELD AVAILABILITY ===")
        
        # Check required fields
        missing_required = []
        for field, description in required_fields.items():
            if field in self.df.columns:
                print(f"✓ {field}: {description}")
            else:
                print(f"✗ {field}: {description} - MISSING!")
                missing_required.append(field)
        
        # Check recommended fields
        print("\nRecommended fields:")
        for field, description in recommended_fields.items():
            if field in self.df.columns:
                print(f"✓ {field}: {description}")
            else:
                print(f"○ {field}: {description} - Not found")
        
        self.report['missing_required'] = missing_required
        return len(missing_required) == 0
    
    def assess_data_quality(self):
        """Assess overall data quality"""
        print("\n=== DATA QUALITY ASSESSMENT ===")
        
        # Basic statistics
        if 'patient_id' in self.df.columns:
            unique_patients = self.df['patient_id'].nunique()
            print(f"Total patients: {unique_patients}")
            self.report['total_patients'] = unique_patients
        
        total_records = len(self.df)
        print(f"Total records: {total_records}")
        self.report['total_records'] = total_records
        
        # Check for missing data
        print("\nMissing data analysis:")
        missing_data = {}
        for col in self.df.columns:
            missing_count = self.df[col].isna().sum()
            missing_pct = (missing_count / len(self.df)) * 100
            if missing_pct > 0:
                print(f"  {col}: {missing_pct:.2f}% missing ({missing_count} records)")
                missing_data[col] = missing_pct
        
        self.report['missing_data'] = missing_data
        
        # Date range analysis
        if 'timestamp' in self.df.columns:
            try:
                self.df['timestamp'] = pd.to_datetime(self.df['timestamp'])
                date_range = f"{self.df['timestamp'].min()} to {self.df['timestamp'].max()}"
                print(f"\nDate range: {date_range}")
                self.report['date_range'] = date_range
            except:
                print("\n⚠ Warning: Could not parse timestamp field")
        
        # Glucose statistics
        if 'glucose_mgdl' in self.df.columns:
            print(f"\nGlucose statistics:")
            print(f"  Mean: {self.df['glucose_mgdl'].mean():.2f} mg/dL")
            print(f"  Std: {self.df['glucose_mgdl'].std():.2f} mg/dL")
            print(f"  Min: {self.df['glucose_mgdl'].min():.2f} mg/dL")
            print(f"  Max: {self.df['glucose_mgdl'].max():.2f} mg/dL")
    
    def calculate_quality_score(self):
        """Calculate overall quality score (0-100)"""
        score = 0
        
        # Patient count (30 points)
        if self.report.get('total_patients', 0) >= 100:
            score += 30
        elif self.report.get('total_patients', 0) >= 50:
            score += 20
        elif self.report.get('total_patients', 0) >= 10:
            score += 10
        
        # Record count (30 points)
        if self.report.get('total_records', 0) >= 10000:
            score += 30
        elif self.report.get('total_records', 0) >= 5000:
            score += 20
        elif self.report.get('total_records', 0) >= 1000:
            score += 10
        
        # Missing data (40 points)
        if not self.report.get('missing_required'):
            critical_fields = ['glucose_mgdl', 'patient_id', 'timestamp']
            missing_data = self.report.get('missing_data', {})
            
            critical_missing = sum(missing_data.get(field, 0) for field in critical_fields if field in missing_data)
            
            if critical_missing < 5:
                score += 40
            elif critical_missing < 15:
                score += 25
            elif critical_missing < 30:
                score += 10
        
        self.report['quality_score'] = score
        return score
    
    def generate_recommendation(self):
        """Generate recommendation based on quality score"""
        score = self.report.get('quality_score', 0)
        
        print("\n" + "="*50)
        print(f"OVERALL QUALITY SCORE: {score}/100")
        print("="*50)
        
        if score >= 80:
            print("✓ EXCELLENT - This dataset is suitable for Digital Twin development")
            print("  Recommendation: Proceed with implementation")
        elif score >= 60:
            print("○ GOOD - This dataset can work with some preprocessing")
            print("  Recommendation: Clean missing data, then proceed")
        elif score >= 40:
            print("⚠ FAIR - This dataset has limitations")
            print("  Recommendation: Consider supplementing with additional data sources")
        else:
            print("✗ POOR - This dataset may not be sufficient")
            print("  Recommendation: Look for alternative datasets or collect more data")
        
        print("\n")
    
    def save_report(self, output_path='dataset_quality_report.json'):
        """Save the quality report to a JSON file"""
        with open(output_path, 'w') as f:
            json.dump(self.report, f, indent=2, default=str)
        print(f"Report saved to: {output_path}")
    
    def run_full_assessment(self):
        """Run complete assessment pipeline"""
        print("="*50)
        print("DIABETES DATASET QUALITY VALIDATOR")
        print("="*50)
        
        if not self.load_data():
            return False
        
        if not self.check_required_fields():
            print("\n⚠ WARNING: Dataset is missing required fields!")
            print("The Digital Twin requires at minimum: patient_id, glucose_mgdl, timestamp")
            return False
        
        self.assess_data_quality()
        self.calculate_quality_score()
        self.generate_recommendation()
        
        return True


if __name__ == "__main__":
    import sys
    
    print("Diabetes Digital Twin - Dataset Validator")
    print("-" * 50)
    
    if len(sys.argv) > 1:
        dataset_path = sys.argv[1]
    else:
        print("\nUsage: python data_validator.py <path_to_dataset.csv>")
        print("\nExample:")
        print("  python data_validator.py data/raw/diabetes_data.csv")
        print("\nNo dataset provided. Exiting...")
        sys.exit(1)
    
    validator = DatasetValidator(dataset_path)
    
    if validator.run_full_assessment():
        validator.save_report()
        print("\n✓ Assessment complete!")
    else:
        print("\n✗ Assessment failed. Please check your dataset.")
