import re
from typing import Dict, Any, List, Set, Optional

class SkillMatcher:
    """
    🎯 HireSense-AI Enterprise Skill Matcher

    Responsibilities:
    ✔ Extract Job Description Skills
    ✔ Normalize Skills & Resolve Synonyms
    ✔ Perform Mathematical Skill Matching (JD vs Resume)
    ✔ Prepare Data for ATS Engine
    """

    def __init__(self):
        # =====================================================
        # INDUSTRY SYNONYM ENGINE
        # =====================================================
        self.synonym_map = {
            "JS": "JAVASCRIPT",
            "JAVASCRIPT ES6": "JAVASCRIPT",
            "TS": "TYPESCRIPT",
            "PY": "PYTHON",
            "ML": "MACHINE LEARNING",
            "AI": "ARTIFICIAL INTELLIGENCE",
            "DL": "DEEP LEARNING",
            "NLP": "NATURAL LANGUAGE PROCESSING",
            "CV": "COMPUTER VISION",
            "TF": "TENSORFLOW",
            "PYTORCH LIGHTNING": "PYTORCH",
            "NODEJS": "NODE.JS",
            "NODE": "NODE.JS",
            "REACTJS": "REACT",
            "REACT.JS": "REACT",
            "VUEJS": "VUE",
            "VUE.JS": "VUE",
            "ANGULARJS": "ANGULAR",
            "POSTGRES": "POSTGRESQL",
            "PGSQL": "POSTGRESQL",
            "MYSQL SERVER": "MYSQL",
            "MSSQL": "SQL SERVER",
            "NOSQL": "NO SQL",
            "MONGODB": "MONGO DB",
            "K8S": "KUBERNETES",
            "DOCKER CONTAINER": "DOCKER",
            "AWS": "AMAZON WEB SERVICES",
            "GCP": "GOOGLE CLOUD",
            "GOOGLE CLOUD PLATFORM": "GOOGLE CLOUD",
            "AZURE CLOUD": "MICROSOFT AZURE",
            "CI/CD PIPELINE": "CI/CD",
            "RESTFUL API": "REST API",
            "RESTFUL SERVICES": "REST API"
        }

        # =====================================================
        # SOFT SKILL LIBRARY
        # =====================================================
        self.soft_skills = {
            "COMMUNICATION", "LEADERSHIP", "TEAMWORK", "TEAM PLAYER",
            "COLLABORATION", "CRITICAL THINKING", "PROBLEM SOLVING",
            "TIME MANAGEMENT", "AGILE", "SCRUM", "MENTORING",
            "PROJECT MANAGEMENT", "JIRA"
        }

        # =====================================================
        # STOPWORDS
        # =====================================================
        self.stopwords = {
            "THE", "A", "AN", "AND", "OR", "WITH", "OF", "TO", "FOR", "IN",
            "ON", "AT", "YEARS", "YEAR", "EXPERIENCE", "REQUIRED", "MUST",
            "HAVE", "GOOD", "STRONG", "KNOWLEDGE", "PLUS", "ADVANTAGE",
            "PREFERRED", "SKILLS", "ABILITY"
        }

    # =====================================================
    # NORMALIZATION ENGINE
    # =====================================================
    def _normalize_skill(self, skill: str) -> str:
        clean = " ".join(skill.upper().strip().split())
        return self.synonym_map.get(clean, clean)

    def _normalize_skill_set(self, skills: List[str]) -> Set[str]:
        normalized = set()
        for skill in skills:
            if skill:
                normalized.add(self._normalize_skill(skill))
        return normalized

    # =====================================================
    # JOB DESCRIPTION PARSER
    # =====================================================
    def extract_jd_skills(self, jd_text: str) -> List[str]:
        """Converts raw Job Description into standardized skills."""
        if not jd_text:
            return []

        jd_upper = jd_text.upper()
        extracted = set()

        # First resolve aliases
        for alias, standard in self.synonym_map.items():
            if re.search(rf"\b{re.escape(alias)}\b", jd_upper):
                extracted.add(standard)

        # Extract tokens
        tokens = re.findall(r"[A-Z0-9\.\+\#-]{2,}", jd_upper)
        for token in tokens:
            if token not in self.stopwords:
                extracted.add(self._normalize_skill(token))

        return sorted(list(extracted))

    # =====================================================
    # 🎯 FULL INTEGRATION: ACTUAL SKILL MATCHING ENGINE
    # =====================================================
    def match_skills(self, resume_skills: List[str], jd_text: str) -> Dict[str, Any]:
        """
        Compares normalized Resume Skills against extracted Job Description Skills.
        Calculates exact mathematical match percentage and tracks missing items dynamically.
        """
        # 1. Extract and normalize JD skills
        jd_skills_list = self.extract_jd_skills(jd_text)
        jd_skills_set = set(self._normalize_skill_set(jd_skills_list))
        
        # 2. Normalize Resume skills
        resume_skills_set = set(self._normalize_skill_set(resume_skills))
        
        if not jd_skills_set:
            # Fallback agar JD me koi recognizable skill na mile
            return {
                "Match_Percentage_Value": 50.0,
                "Matched_Skills": sorted(list(resume_skills_set)),
                "Missing_Skills": [],
                "Additional_Skills": sorted(list(resume_skills_set))
            }
            
        # 3. Mathematical Set Operations
        matched_skills = jd_skills_set.intersection(resume_skills_set)
        missing_skills = jd_skills_set.difference(resume_skills_set)
        additional_skills = resume_skills_set.difference(jd_skills_set)
        
        # 4. Match Percentage Calculation
        match_ratio = len(matched_skills) / len(jd_skills_set)
        match_percentage = round(match_ratio * 100, 1)
        
        return {
            "Match_Percentage_Value": match_percentage,
            "Matched_Skills": sorted(list(matched_skills)),
            "Missing_Skills": sorted(list(missing_skills)),
            "Additional_Skills": sorted(list(additional_skills))
        }