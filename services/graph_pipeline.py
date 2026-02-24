"""
Interview IQ — LangGraph Pipeline logic.
Handles JD analysis and question generation using LangChain and LangGraph.
"""

import os
import logging
from typing import TypedDict, List, Optional
from datetime import datetime

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, START, END
from dotenv import load_dotenv

from models.schemas import (
    JobDescriptionAnalysis,
    InterviewQuestion,
    InterviewQuestionSet,
    GenerationConfig,
)

load_dotenv()
logger = logging.getLogger(__name__)

# ─── Configuration ────────────────────────────────────────────────────────────

MODEL_NAME = "llama-3.3-70b-versatile"

def get_llm():
    return ChatGroq(
        model=MODEL_NAME,
        temperature=0.3,
        max_retries=2,
    )

# ─── Graph State ──────────────────────────────────────────────────────────────

class InterviewState(TypedDict):
    """The state maintained throughout the LangGraph workflow."""
    raw_jd_text: str
    config: GenerationConfig
    analysis: Optional[JobDescriptionAnalysis]
    questions: Optional[List[InterviewQuestion]]
    error: Optional[str]

# ─── Nodes ────────────────────────────────────────────────────────────────────

async def analyze_jd_node(state: InterviewState):
    """Phase 1: Analyze the JD text and extract structured info."""
    logger.info("🔍 Node: analyze_jd")
    llm = get_llm().with_structured_output(JobDescriptionAnalysis)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an expert HR analyst. Analyze the job description and extract structured information."),
        ("user", "{jd_text}")
    ])
    
    chain = prompt | llm
    
    try:
        analysis = await chain.ainvoke({"jd_text": state["raw_jd_text"]})
        return {"analysis": analysis}
    except Exception as e:
        logger.error(f"Error in JD analysis node: {e}")
        return {"error": f"JD Analysis failed: {str(e)}"}

async def generate_questions_node(state: InterviewState):
    """Phase 2: Generate interview questions based on the analysis."""
    logger.info("🧠 Node: generate_questions")
    
    if state.get("error"):
        return state

    analysis = state["analysis"]
    config = state["config"]
    
    # We use a separate model instance for questions with higher temperature
    llm = ChatGroq(
        model=MODEL_NAME,
        temperature=0.7,
    ).with_structured_output(InterviewQuestionSet)

    categories_str = ", ".join(c.value for c in config.categories)
    skills_str = ", ".join(s.name for s in analysis.key_skills)

    prompt = ChatPromptTemplate.from_messages([
        ("system", (
            "You are a world-class interview coach. Generate exactly {num_questions} "
            "interview questions based on the provided Job Description Analysis. "
            "Difficulty: {difficulty}. Categories: {categories}. "
            "Target Skills: {skills}."
        )),
        ("user", "Role: {role}\nSummary: {summary}\nResponsibilities: {responsibilities}")
    ])

    chain = prompt | llm
    
    try:
        result = await chain.ainvoke({
            "num_questions": config.num_questions,
            "difficulty": config.difficulty.value,
            "categories": categories_str,
            "skills": skills_str,
            "role": analysis.role_title,
            "summary": analysis.role_summary,
            "responsibilities": "\n".join(analysis.responsibilities)
        })
        
        # Ensure metadata is set correctly
        result.generation_timestamp = datetime.now().isoformat()
        result.model_used = MODEL_NAME
        result.jd_analysis = analysis
        
        return {"questions": result.questions}
    except Exception as e:
        logger.error(f"Error in question generation node: {e}")
        return {"error": f"Question generation failed: {str(e)}"}

# ─── Graph Construction ───────────────────────────────────────────────────────

def build_graph():
    workflow = StateGraph(InterviewState)

    # Add nodes
    workflow.add_node("analyze_jd", analyze_jd_node)
    workflow.add_node("generate_questions", generate_questions_node)

    # Define edges
    workflow.add_edge(START, "analyze_jd")
    workflow.add_edge("analyze_jd", "generate_questions")
    workflow.add_edge("generate_questions", END)

    return workflow.compile()

# The compiled graph instance
interview_graph = build_graph()
