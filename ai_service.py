import json
import os
import google.generativeai as genai
from typing import Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()

class AIService:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
        else:
            self.model = None

    def _clean_json_response(self, text: str) -> str:
        text = text.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        return text.strip()

    def generate_insights(self, candidate_data: Dict[str, Any]) -> Dict[str, Any]:
        name = candidate_data.get("name", "Candidate")
        role = candidate_data.get("role", "Software Professional")
        exp = candidate_data.get("experience", "Fresher")
        edu = candidate_data.get("education", "Graduate")
        ats = candidate_data.get("ats_score", 70)
        matched = candidate_data.get("Matched_Skills", [])
        missing = candidate_data.get("Missing_Skills", [])

        smart_fallback = {
            "candidate_summary": f"{name} is a dedicated {role} with {exp} of professional background and a {edu} qualification. Exhibits solid alignment with core technical requirements.",
            "key_strengths": matched[:3] if matched else ["Core Programming", "Problem Solving", "Quick Learner"],
            "areas_for_improvement": missing[:2] if missing else ["Advanced Cloud Infrastructure"],
            "suitable_roles": [role, "Software Engineer", "Technical Associate"],
            "skill_gap_analysis": missing[:3] if missing else ["None identified as critical."],
            "swot_analysis": {
                "strengths": f"Demonstrated proficiency in {', '.join(matched[:3]) if matched else 'core technologies'} with robust project execution capabilities.",
                "weaknesses": f"Potential skill gaps in specific secondary tools such as {', '.join(missing[:2]) if missing else 'advanced frameworks'}.",
                "opportunities": "High potential for rapid professional growth in dynamic engineering environments.",
                "threats": "Competitive industry landscape requiring continuous technology updates."
            },
            "interview_questions": [
                {"skill": matched[0] if matched else "Core", "question": f"Can you walk us through a challenging architectural decision you made while working with {matched[0] if matched else 'your tech stack'}?"},
                {"skill": "System Design", "question": "How do you handle scalability and performance optimization in high-traffic applications?"},
                {"skill": "Problem Solving", "question": "Describe a scenario where you had to troubleshoot a critical production bug under pressure."}
            ],
            "ai_hiring_recommendation": "Highly Recommended" if ats >= 75 else "Pending Review" if ats >= 50 else "Rejected",
            "ai_explanation": f"Evaluated at {ats}% ATS score, indicating strong foundational capability matching role expectations."
        }

        if not self.model:
            return smart_fallback

        prompt = f"""
        You are an Expert IT Recruiter and Technical HR Analyst. 
        Analyze the following Candidate JSON profile and provide a strictly formatted JSON response.
        
        Candidate Profile:
        {json.dumps(candidate_data, indent=2)}

        You must respond ONLY with a valid JSON object using the exact keys below. Do not add any markdown formatting or extra text outside the JSON.
        Ensure "swot_analysis" values are plain strings (not dictionaries or lists), and "interview_questions" is an array of objects containing "skill" and "question".
        
        Required Output Format:
        {{
            "candidate_summary": "A 2-3 line professional summary.",
            "key_strengths": ["Strength 1", "Strength 2"],
            "areas_for_improvement": ["Improvement 1"],
            "suitable_roles": ["Role 1"],
            "skill_gap_analysis": ["Gap 1"],
            "swot_analysis": {{
                "strengths": "Plain text paragraph describing strengths.",
                "weaknesses": "Plain text paragraph describing weaknesses.",
                "opportunities": "Plain text paragraph describing opportunities.",
                "threats": "Plain text paragraph describing threats."
            }},
            "interview_questions": [
                {{"skill": "Python", "question": "Question text..."}}
            ],
            "ai_hiring_recommendation": "Highly Recommended",
            "ai_explanation": "Explanation text."
        }}
        """

        try:
            response = self.model.generate_content(prompt)
            cleaned_text = self._clean_json_response(response.text)
            ai_insights = json.loads(cleaned_text)
            return ai_insights
        except Exception:
            return smart_fallback