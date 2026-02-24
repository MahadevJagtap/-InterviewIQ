"""
Pydantic models for structured prompts and responses.
Defines the complete data contract for the Interview Question Generator pipeline.
"""

from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum
from datetime import datetime


# ─── Enums ────────────────────────────────────────────────────────────────────

class DifficultyLevel(str, Enum):
    EASY = "Easy"
    MEDIUM = "Medium"
    HARD = "Hard"


class QuestionCategory(str, Enum):
    TECHNICAL = "Technical"
    BEHAVIORAL = "Behavioral"
    SITUATIONAL = "Situational"
    COMPETENCY = "Competency-Based"
    CULTURE_FIT = "Culture Fit"


# ─── Request Models ──────────────────────────────────────────────────────────

class GenerationConfig(BaseModel):
    """User-configurable options for question generation."""
    difficulty: DifficultyLevel = Field(
        default=DifficultyLevel.MEDIUM,
        description="Target difficulty level for the questions"
    )
    num_questions: int = Field(
        default=10,
        ge=3,
        le=30,
        description="Number of questions to generate"
    )
    categories: list[QuestionCategory] = Field(
        default=[
            QuestionCategory.TECHNICAL,
            QuestionCategory.BEHAVIORAL,
            QuestionCategory.SITUATIONAL,
        ],
        description="Question categories to include"
    )


# ─── JD Analysis Models ──────────────────────────────────────────────────────

class SkillRequirement(BaseModel):
    """Individual skill extracted from the JD."""
    name: str = Field(description="Skill name, e.g. 'Python', 'Leadership'")
    proficiency: str = Field(description="Expected proficiency: Beginner / Intermediate / Advanced / Expert")
    category: str = Field(description="Category: Technical / Soft Skill / Domain Knowledge / Tool")


class JobDescriptionAnalysis(BaseModel):
    """Structured analysis of the job description."""
    role_title: str = Field(description="Extracted job title")
    company_name: Optional[str] = Field(default=None, description="Company name if mentioned")
    department: Optional[str] = Field(default=None, description="Department or team")
    experience_range: str = Field(description="Required experience, e.g. '3-5 years'")
    education: Optional[str] = Field(default=None, description="Education requirements")
    key_skills: list[SkillRequirement] = Field(description="Key skills extracted from the JD")
    responsibilities: list[str] = Field(description="Core responsibilities listed in the JD")
    role_summary: str = Field(description="2-3 sentence summary of what this role entails")
    seniority_level: str = Field(description="Inferred seniority: Junior / Mid / Senior / Lead / Principal / Executive")
    industry: Optional[str] = Field(default=None, description="Industry or domain if identifiable")


# ─── Question & Answer Models ────────────────────────────────────────────────

class EvaluationCriteria(BaseModel):
    """Rubric for evaluating a candidate's answer."""
    excellent: str = Field(description="What an excellent answer looks like")
    acceptable: str = Field(description="What a satisfactory answer looks like")
    poor: str = Field(description="Red flags or poor answer indicators")


class InterviewQuestion(BaseModel):
    """A single interview question with its complete context."""
    id: int = Field(description="Sequential question number")
    question: str = Field(description="The interview question text")
    category: QuestionCategory = Field(description="Question category")
    difficulty: DifficultyLevel = Field(description="Question difficulty")
    why_ask: str = Field(description="Why this question is relevant to the role")
    expected_answer: str = Field(description="Ideal / model answer")
    evaluation_criteria: EvaluationCriteria = Field(description="Rubric for scoring")
    follow_up_questions: list[str] = Field(
        default_factory=list,
        description="2-3 follow-up probing questions"
    )
    relevant_skills: list[str] = Field(
        default_factory=list,
        description="Skills this question tests"
    )


class InterviewQuestionSet(BaseModel):
    """Complete set of generated interview questions with metadata."""
    jd_analysis: JobDescriptionAnalysis = Field(description="Parsed JD analysis")
    questions: list[InterviewQuestion] = Field(description="Generated questions")
    total_questions: int = Field(description="Total count of questions")
    generation_timestamp: str = Field(
        default_factory=lambda: datetime.now().isoformat(),
        description="When the questions were generated"
    )
    model_used: str = Field(default="llama-3.3-70b-versatile", description="LLM model used")
