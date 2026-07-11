import math
from typing import Dict, Any, List

class ATSEngine:
    """
    🎯 The Master Decision Engine (10/10 Enterprise Edition)
    Calculates dynamic ATS scores, hiring zones, and generates XAI (Explainable AI) metrics.
    """

    def __init__(self, custom_weights: Dict[str, float] = None):
        # ✅ FEATURE: Dynamic Weightage synced with parser keys
        self.weights = custom_weights or {
            "skills": 0.60,        
            "resume_score": 0.20,  
            "experience": 0.10,    
            "education": 0.10      
        }
        
        # ✅ PRO-FEATURE: Floating-point tolerance check instead of exact match
        total_weight = sum(self.weights.values())
        if not math.isclose(total_weight, 1.0, rel_tol=1e-5):
            raise ValueError(f"System Error: ATS weightages must equal 1.0 (100%). Current sum: {total_weight}")

    def _validate_data(self, resume_data: Dict[str, Any], skill_match_data: Dict[str, Any]) -> List[str]:
        """✅ FEATURE: Resume Data Validation & Warning Generation"""
        warnings = []
        if not skill_match_data.get("Matched_Skills") and not skill_match_data.get("Match_Percentage_Value"):
            warnings.append("⚠️ Missing Job Description skill alignment data.")
        if not resume_data.get("education_score"):
            warnings.append("⚠️ Education metrics missing or unreadable.")
        if not resume_data.get("experience_score"):
            warnings.append("⚠️ Experience timeline missing.")
        if not resume_data.get("resume_score"):
            warnings.append("⚠️ Resume formatting metrics missing (Fallback applied).")
        return warnings

    def _get_hiring_zone_and_reco(self, score: float) -> tuple:
        """✅ FEATURE: Hiring Zone & Recruitment Recommendation Mapping"""
        if score >= 90:
            return "Excellent", "Highly Recommended"
        elif score >= 75:
            return "Good", "Recommended"
        elif score >= 60:
            return "Average", "Needs Improvement"
        else:
            return "Poor", "Not Recommended"

    def evaluate_candidate(self, resume_data: Dict[str, Any], skill_match_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main Engine that processes parsed resume data and skill match reports 
        to generate the final ATS Score and Explainable AI (XAI) Dashboard JSON.
        """
        validation_warnings = self._validate_data(resume_data, skill_match_data)

        # 1. Extract Base Scores (Out of 100) - Keys strictly matched for integration
        base_skill_score = float(skill_match_data.get("Match_Percentage_Value", 0.0))
        base_resume_score = float(resume_data.get("resume_score", 50.0)) 
        base_exp_score = float(resume_data.get("experience_score", 50.0))
        base_edu_score = float(resume_data.get("education_score", 50.0))

        # 2. Apply Dynamic Weightage (Calculate Earned Points)
        earned_skills = round(base_skill_score * self.weights["skills"], 1)
        earned_resume = round(base_resume_score * self.weights["resume_score"], 1)
        earned_exp = round(base_exp_score * self.weights["experience"], 1)
        earned_edu = round(base_edu_score * self.weights["education"], 1)

        total_ats_score = round(earned_skills + earned_resume + earned_exp + earned_edu, 1)

        # 3. Get Zones and Recommendations
        hiring_zone, recommendation = self._get_hiring_zone_and_reco(total_ats_score)

        # 4. Build XAI (Explainable AI) Reasons
        xai_reasons = []
        if base_skill_score >= 80: 
            xai_reasons.append("Strong Technical Skill Match with JD requirements")
        elif base_skill_score < 50: 
            xai_reasons.append("Critical Technical Skills Missing for target role")
            
        if base_resume_score >= 80: 
            xai_reasons.append("Excellent Document Structure & Formatting")
            
        missing_skills = skill_match_data.get("Missing_Skills", [])
        if missing_skills:
            xai_reasons.append(f"Missing core skills: {', '.join(missing_skills[:3])}")
            
        xai_reasons.extend(validation_warnings)

        # 5. Decision Routing
        forward_to_ai = total_ats_score >= 60.0

        # ❤️ FINAL OUTPUT GENERATION: Complete Schema for UI & Database
        return {
            "ats_score": total_ats_score,
            "match_o_meter": total_ats_score,                
            "hiring_zone": hiring_zone,                      
            "recommendation": recommendation,                
            "forward_to_ai": forward_to_ai,                  
            "ranking_score": total_ats_score,                
            
            # ✅ PRO-FEATURE: Enhanced Score Breakdown (Perfect for UI Progress Bars & Graphs)
            "score_breakdown": {
                "skills": {"base": base_skill_score, "weight": self.weights["skills"], "earned": earned_skills},
                "resume": {"base": base_resume_score, "weight": self.weights["resume_score"], "earned": earned_resume},
                "experience": {"base": base_exp_score, "weight": self.weights["experience"], "earned": earned_exp},
                "education": {"base": base_edu_score, "weight": self.weights["education"], "earned": earned_edu}
            },
            
            "keyword_traceability": {
                "matched": skill_match_data.get("Matched_Skills", []),
                "missing": missing_skills
            },
            
            "xai_xray": {
                "reason": xai_reasons
            }
        }