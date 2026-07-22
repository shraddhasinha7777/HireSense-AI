import math
from typing import Dict, Any, List

class ATSEngine:
    """
    🎯 The Master Decision Engine (Enterprise Edition)
    Calculates dynamic ATS scores, hiring zones, and generates XAI metrics.
    """

    def __init__(self, custom_weights: Dict[str, float] = None):
        # ⭐ FIXED: Weights exactly synced with Resume Analyzer UI (40-30-20-10)
        self.weights = custom_weights or {
            "skills": 0.40,        
            "resume_score": 0.30,  
            "experience": 0.20,    
            "education": 0.10      
        }
        
        total_weight = sum(self.weights.values())
        if not math.isclose(total_weight, 1.0, rel_tol=1e-5):
            raise ValueError(f"System Error: ATS weightages must equal 1.0. Current sum: {total_weight}")

    def _validate_data(self, resume_data: Dict[str, Any], skill_match_data: Dict[str, Any]) -> List[str]:
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
        # ⭐ FIXED: Strict Status naming to sync with Candidate Management
        if score >= 80:
            return "Excellent", "Highly Recommended"
        elif score >= 65:
            return "Good", "Recommended"
        elif score >= 50:
            return "Average", "Pending Review"
        else:
            return "Poor", "Rejected"

    def evaluate_candidate(self, resume_data: Dict[str, Any], skill_match_data: Dict[str, Any]) -> Dict[str, Any]:
        validation_warnings = self._validate_data(resume_data, skill_match_data)

        base_skill_score = float(skill_match_data.get("Match_Percentage_Value", 0.0))
        base_resume_score = float(resume_data.get("resume_score", 50.0)) 
        base_exp_score = float(resume_data.get("experience_score", 50.0))
        base_edu_score = float(resume_data.get("education_score", 50.0))

        earned_skills = round(base_skill_score * self.weights["skills"], 1)
        earned_resume = round(base_resume_score * self.weights["resume_score"], 1)
        earned_exp = round(base_exp_score * self.weights["experience"], 1)
        earned_edu = round(base_edu_score * self.weights["education"], 1)

        total_ats_score = round(earned_skills + earned_resume + earned_exp + earned_edu, 1)

        hiring_zone, recommendation = self._get_hiring_zone_and_reco(total_ats_score)

        xai_reasons = []
        if base_skill_score >= 80: xai_reasons.append("Strong Technical Skill Match with JD requirements")
        elif base_skill_score < 50: xai_reasons.append("Critical Technical Skills Missing for target role")
        if base_resume_score >= 80: xai_reasons.append("Excellent Document Structure & Formatting")
            
        missing_skills = skill_match_data.get("Missing_Skills", [])
        if missing_skills: xai_reasons.append(f"Missing core skills: {', '.join(missing_skills[:3])}")
        xai_reasons.extend(validation_warnings)

        forward_to_ai = total_ats_score >= 50.0

        return {
            "ats_score": total_ats_score,
            "match_o_meter": total_ats_score,                
            "hiring_zone": hiring_zone,                      
            "recommendation": recommendation,                
            "forward_to_ai": forward_to_ai,                  
            "ranking_score": total_ats_score,                
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