import re
from typing import Dict, Any, List, Set


class SkillMatcher:
    """
    Enterprise Skill Matcher
    - Multi-header dynamic JD skill extraction
    - Clean REST API variants mapping (Generic 'API' wildcard removed for safety)
    - Pure mathematical matching (Matched / Total JD Skills)
    """

    def __init__(self):
        self.synonym_map = {
            "JS": "JAVASCRIPT",
            "TS": "TYPESCRIPT",
            "PY": "PYTHON",
            "ML": "MACHINE LEARNING",
            "AI": "ARTIFICIAL INTELLIGENCE",
            "DL": "DEEP LEARNING",
            "TF": "TENSORFLOW",
            "TF2": "TENSORFLOW",
            "SKLEARN": "SCIKIT-LEARN",
            "SCIKIT LEARN": "SCIKIT-LEARN",
            "SCI-KIT LEARN": "SCIKIT-LEARN",
            "POWERBI": "POWER BI",
            "POWER-BI": "POWER BI",
            "POSTGRES": "POSTGRESQL",
            "PGSQL": "POSTGRESQL",
            "POSTGRESQL DATABASE": "POSTGRESQL",
            "MYSQL SERVER": "MYSQL",
            "MS EXCEL": "EXCEL",
            "MICROSOFT EXCEL": "EXCEL",
            "RESTFUL API": "REST API",
            "RESTFUL APIS": "REST API",
            "REST APIS": "REST API",
            # "API": "REST API" -> Removed safely to prevent false positives with GraphQL/SOAP
            "GITHUB": "GIT",
            "GITLAB": "GIT",
            "OPEN CV": "OPENCV",
            "AZUREAI": "AZURE AI",
            "NLP": "NATURAL LANGUAGE PROCESSING"
        }

        self.master_skill_library = {
            "PYTHON",
            "SQL",
            "JAVA",
            "C++",
            "C#",
            "R",
            "JAVASCRIPT",
            "TYPESCRIPT",
            "PANDAS",
            "NUMPY",
            "MATPLOTLIB",
            "SEABORN",
            "PLOTLY",
            "POWER BI",
            "TABLEAU",
            "EXCEL",
            "STATISTICS",
            "DATA VISUALIZATION",
            "MACHINE LEARNING",
            "DEEP LEARNING",
            "ARTIFICIAL INTELLIGENCE",
            "NATURAL LANGUAGE PROCESSING",
            "COMPUTER VISION",
            "SCIKIT-LEARN",
            "PYTORCH",
            "TENSORFLOW",
            "KERAS",
            "MYSQL",
            "POSTGRESQL",
            "MONGODB",
            "GIT",
            "DOCKER",
            "KUBERNETES",
            "AZURE",
            "AZURE AI",
            "REST API",
            "FLASK",
            "DJANGO",
            "FASTAPI",
            "STREAMLIT",
            "SPARK",
            "HADOOP",
            "BIG DATA",
            "AIRFLOW",
            "SELENIUM",
            "LINUX",
            "PHP",
            "ETL"
        }

    def _normalize(self, text: str) -> str:
        text = " ".join(text.upper().strip().split())
        return self.synonym_map.get(text, text)

    def _find_skill(self, skill: str, text: str) -> bool:
        pattern = rf"(?<!\w){re.escape(skill)}(?!\w)"
        return re.search(pattern, text) is not None

    def extract_jd_skills(self, jd_text: str) -> List[str]:
        if not jd_text:
            return []

        jd_upper = jd_text.upper()

        # -------- Dynamic Multi-Header Skill Section Extraction --------
        skill_headers = [
            "REQUIRED SKILLS",
            "SKILLS",
            "TECHNICAL SKILLS",
            "KEY SKILLS",
            "REQUIREMENTS",
            "QUALIFICATIONS"
        ]

        start = None
        for header in skill_headers:
            if header in jd_upper:
                start = jd_upper.find(header)
                break

        target_text = jd_upper
        if start is not None:
            end = len(jd_upper)
            for stop in [
                "RESPONSIBILITIES",
                "ABOUT US",
                "BENEFITS",
                "WHAT YOU WILL DO",
                "JOB DESCRIPTION"
            ]:
                pos = jd_upper.find(stop)
                if pos != -1 and pos > start:
                    end = pos
                    break
            target_text = jd_upper[start:end]

        skills = set()

        # Master Skill Library
        for skill in self.master_skill_library:
            if self._find_skill(skill, target_text):
                skills.add(self._normalize(skill))

        # Synonyms
        for alias, original in self.synonym_map.items():
            if self._find_skill(alias, target_text):
                skills.add(original)

        return sorted(skills)

    def match_skills(
        self,
        resume_skills: List[str],
        jd_text: str
    ) -> Dict[str, Any]:

        jd_skills = {
            self._normalize(x)
            for x in self.extract_jd_skills(jd_text)
        }

        resume = {
            self._normalize(x)
            for x in resume_skills
            if x
        }

        matched = jd_skills & resume
        missing = jd_skills - resume
        additional = resume - jd_skills

        if len(jd_skills) == 0:
            percent = 0.0
        else:
            percent = round((len(matched) / len(jd_skills)) * 100, 1)

        return {
            "Match_Percentage_Value": percent,
            "Matched_Skills": sorted(matched),
            "Missing_Skills": sorted(missing),
            "Additional_Skills": sorted(additional)
        }