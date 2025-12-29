"""
Patient Data CSV Export Utility
Exports complete patient journey data to CSV
"""

import csv
import json
from datetime import datetime
from typing import List, Dict
import os


class PatientDataExporter:
    """Handles CSV export of patient data"""
    
    def __init__(self, export_dir="exports"):
        self.export_dir = export_dir
        if not os.path.exists(export_dir):
            os.makedirs(export_dir)
    
    def export_patient_complete_data(self, user, consultations: List, medications: List, tickets: List) -> str:
        """
        Export complete patient data to CSV
        Returns: filepath of generated CSV
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"patient_{user.id}_{user.email.replace('@', '_at_')}_{timestamp}.csv"
        filepath = os.path.join(self.export_dir, filename)
        
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # SECTION 1: Patient Information
            writer.writerow([])
            writer.writerow(["=" * 80])
            writer.writerow(["PATIENT INFORMATION"])
            writer.writerow(["=" * 80])
            writer.writerow(["Field", "Value"])
            writer.writerow(["Patient ID", user.id])
            writer.writerow(["Email", user.email])
            writer.writerow(["First Name", user.first_name])
            writer.writerow(["Last Name", user.last_name])
            writer.writerow(["Date of Birth", user.date_of_birth])
            writer.writerow(["Gender", user.gender])
            writer.writerow(["Phone", user.phone_number])
            writer.writerow(["Condition Category", user.condition_category])
            writer.writerow(["Registered At", user.created_at])
            
            # SECTION 2: Medical Profile
            writer.writerow([])
            writer.writerow(["=" * 80])
            writer.writerow(["MEDICAL PROFILE"])
            writer.writerow(["=" * 80])
            if user.medical_data:
                for key, value in user.medical_data.items():
                    writer.writerow([key.replace('_', ' ').title(), value])
            
            # SECTION 3: Consultations
            writer.writerow([])
            writer.writerow(["=" * 80])
            writer.writerow(["CONSULTATION HISTORY"])
            writer.writerow(["=" * 80])
            writer.writerow([f"Total Consultations: {len(consultations)}"])
            writer.writerow([])
            
            for idx, consultation in enumerate(consultations, 1):
                writer.writerow([f"--- CONSULTATION {idx} ---"])
                writer.writerow(["Consultation ID", consultation.id])
                writer.writerow(["Status", consultation.status])
                writer.writerow(["Created At", consultation.created_at])
                writer.writerow(["Updated At", consultation.updated_at])
                
                # Collected Data
                writer.writerow([])
                writer.writerow(["Collected Interview Data:"])
                if consultation.collected_data:
                    condition_type = consultation.collected_data.get('condition_type', 'N/A')
                    writer.writerow(["  Condition Type", condition_type])
                    qa_data = consultation.collected_data.get('qa_data', {})
                    for question, answer in qa_data.items():
                        writer.writerow(["  " + question, answer])
                
                # Conversation History
                writer.writerow([])
                writer.writerow(["Conversation Transcript:"])
                if consultation.conversation_history:
                    for msg in consultation.conversation_history:
                        role = msg.get('role', 'unknown').upper()
                        content = msg.get('content', '')
                        writer.writerow([f"  [{role}]", content])
                
                # Analysis Results
                writer.writerow([])
                writer.writerow(["AI Analysis Results:"])
                if consultation.analysis_result:
                    analysis = consultation.analysis_result
                    writer.writerow(["  Condition", analysis.get('condition', 'N/A')])
                    writer.writerow(["  Severity", analysis.get('severity', 'N/A')])
                    writer.writerow(["  Recommendations", analysis.get('recommendations', 'N/A')])
                    writer.writerow(["  Reasoning", analysis.get('reasoning', 'N/A')])
                
                # Care Plan
                writer.writerow([])
                writer.writerow(["Care Plan:"])
                if consultation.care_plan:
                    plan = consultation.care_plan
                    
                    short_term = plan.get('short_term_plan', {})
                    writer.writerow(["  SHORT-TERM PLAN (1-7 days):"])
                    
                    daily_actions = short_term.get('daily_actions', [])
                    if daily_actions:
                        writer.writerow(["    Daily Actions:"])
                        for action in daily_actions:
                            writer.writerow(["      -", action])
                    
                    monitoring = short_term.get('monitoring', [])
                    if monitoring:
                        writer.writerow(["    Monitoring:"])
                        for item in monitoring:
                            writer.writerow(["      -", item])
                    
                    red_flags = short_term.get('red_flags', [])
                    if red_flags:
                        writer.writerow(["    Red Flags:"])
                        for flag in red_flags:
                            writer.writerow(["      -", flag])
                    
                    long_term = plan.get('long_term_plan', {})
                    writer.writerow(["  LONG-TERM PLAN:"])
                    
                    goals = long_term.get('goals', [])
                    if goals:
                        writer.writerow(["    Goals:"])
                        for goal in goals:
                            writer.writerow(["      -", goal])
                    
                    lifestyle = long_term.get('lifestyle_changes', [])
                    if lifestyle:
                        writer.writerow(["    Lifestyle Changes:"])
                        for change in lifestyle:
                            writer.writerow(["      -", change])
                
                writer.writerow([])
            
            # SECTION 4: Medications
            writer.writerow([])
            writer.writerow(["=" * 80])
            writer.writerow(["MEDICATIONS"])
            writer.writerow(["=" * 80])
            writer.writerow([f"Total Medications: {len(medications)}"])
            writer.writerow([])
            
            if medications:
                writer.writerow(["ID", "Name", "Dosage", "Frequency", "Timing", "Instructions", "Added Date"])
                for med in medications:
                    timing_str = ", ".join(med.timing) if isinstance(med.timing, list) else str(med.timing)
                    writer.writerow([
                        med.id,
                        med.name,
                        med.dosage,
                        med.frequency,
                        timing_str,
                        med.instructions,
                        med.created_at
                    ])
            
            # SECTION 5: Medical Tickets (if Doctor reviewed)
            writer.writerow([])
            writer.writerow(["=" * 80])
            writer.writerow(["MEDICAL TICKETS (Doctor Review)"])
            writer.writerow(["=" * 80])
            writer.writerow([f"Total Tickets: {len(tickets)}"])
            writer.writerow([])
            
            for idx, ticket in enumerate(tickets, 1):
                writer.writerow([f"--- TICKET {idx} ---"])
                writer.writerow(["Ticket ID", ticket.id])
                writer.writerow(["Consultation ID", ticket.consultation_id])
                writer.writerow(["Status", ticket.status])
                writer.writerow(["Created At", ticket.created_at])
                writer.writerow(["Reviewed By Doctor ID", ticket.doctor_id if hasattr(ticket, 'doctor_id') else 'N/A'])
                
                if ticket.medical_ticket_data:
                    ticket_data = ticket.medical_ticket_data
                    summary = ticket_data.get('summary', {})
                    
                    writer.writerow(["Chief Complaint", summary.get('chief_complaint', 'N/A')])
                    writer.writerow(["AI Assessment", summary.get('ai_assessment', 'N/A')])
                    writer.writerow(["Urgency", summary.get('urgency', 'N/A')])
                    writer.writerow(["Doctor Notes", summary.get('doctor_notes', 'N/A')])
                
                writer.writerow([])
            
            # SECTION 6: Export Metadata
            writer.writerow([])
            writer.writerow(["=" * 80])
            writer.writerow(["EXPORT METADATA"])
            writer.writerow(["=" * 80])
            writer.writerow(["Export Date", datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
            writer.writerow(["Export Format", "CSV"])
            writer.writerow(["MedTwin Version", "1.0.0"])
            writer.writerow(["=" * 80])
        
        return filepath
    
    def export_consultation_summary(self, consultations: List) -> str:
        """Export consultation summary table"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"consultations_summary_{timestamp}.csv"
        filepath = os.path.join(self.export_dir, filename)
        
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Consultation ID", "Patient ID", "Condition", "Severity", "Status", "Created", "Updated"])
            
            for c in consultations:
                condition = c.collected_data.get('condition_type', 'N/A') if c.collected_data else 'N/A'
                severity = c.analysis_result.get('severity', 'N/A') if c.analysis_result else 'N/A'
                
                writer.writerow([
                    c.id,
                    c.patient_id,
                    condition,
                    severity,
                    c.status,
                    c.created_at,
                    c.updated_at
                ])
        
        return filepath


# Convenience function
def export_patient_data(user, consultations=None, medications=None, tickets=None):
    """
    Export complete patient data to CSV
    Usage: export_patient_data(user, consultations, medications, tickets)
    """
    exporter = PatientDataExporter()
    return exporter.export_patient_complete_data(
        user, 
        consultations or [], 
        medications or [], 
        tickets or []
    )
