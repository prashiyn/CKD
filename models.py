from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import date

class MedicalHistory(BaseModel):
    report_obtained_date: Optional[date] = Field(None, description="Date when the medical report was obtained")
    first_diagnosis_age: Optional[int] = Field(None, description="Age when first diagnosed with kidney disease")
    current_age_during_dialysis: Optional[int] = Field(None, description="Current age during dialysis if applicable")

class Demographics(BaseModel):
    gender: Optional[Literal["male", "female", "other"]] = Field(None, description="Patient's gender")
    age: Optional[int] = Field(None, description="Patient's current age")

class MedicalConditions(BaseModel):
    hypertension: Optional[bool] = Field(None, description="Whether the patient has hypertension")
    diabetes_type_1: Optional[bool] = Field(None, description="Whether the patient has Type 1 diabetes")
    diabetes_type_2: Optional[bool] = Field(None, description="Whether the patient has Type 2 diabetes")
    cardiovascular_disease: Optional[bool] = Field(None, description="Whether the patient has cardiovascular disease")

class Symptoms(BaseModel):
    appetite_changes: Optional[Literal["increased", "decreased", "unchanged"]] = Field(None, description="Changes in appetite")
    pedal_edema: Optional[bool] = Field(None, description="Swelling in feet and ankles")
    hematuria: Optional[bool] = Field(None, description="Blood in urine")
    nocturia: Optional[bool] = Field(None, description="Excessive urination at night")
    flank_discomfort: Optional[bool] = Field(None, description="Pain in the side or back")
    decreased_urine_output: Optional[bool] = Field(None, description="Reduced amount of urine")
    fatigue: Optional[bool] = Field(None, description="Feeling tired or weak")
    nausea_vomiting: Optional[bool] = Field(None, description="Feeling sick or throwing up")
    metallic_taste: Optional[bool] = Field(None, description="Metallic taste in mouth")
    unintended_weight_loss: Optional[bool] = Field(None, description="Losing weight without trying")
    itching: Optional[bool] = Field(None, description="Persistent itching")
    mental_state_changes: Optional[Literal["none", "confusion", "memory_problems"]] = Field(None, description="Changes in mental state")
    breathing_difficulty: Optional[bool] = Field(None, description="Difficulty breathing")

class PatientData(BaseModel):
    medical_history: MedicalHistory
    demographics: Demographics
    medical_conditions: MedicalConditions
    symptoms: Symptoms 

class PatientQnA(BaseModel):
    question: str
    answer: str
