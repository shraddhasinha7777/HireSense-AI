import re
import os
import time
import pdfplumber
from typing import Dict, Any, List, Tuple
from dotenv import load_dotenv

load_dotenv()

class ResumeParser:
    """
    🎯 The Master Resume Parser (Enterprise Version with Debugged Cloud OCR)
    """

    def __init__(self):
        # 🚀 100+ Categorized Skill Library
        self.skill_library = {
            # Languages
            "PYTHON", "JAVA", "C++", "C#", "C", "JAVASCRIPT", "TYPESCRIPT", "PHP", "RUBY", 
            "GO", "RUST", "SWIFT", "KOTLIN", "R", "MATLAB", "DART",
            # Web Frontend
            "HTML", "HTML5", "CSS", "CSS3", "REACT", "REACT.JS", "ANGULAR", "VUE", "VUE.JS", 
            "NEXT.JS", "TAILWIND", "TAILWIND CSS", "BOOTSTRAP", "JQUERY", "REDUX",
            # Web Backend & Frameworks
            "NODE.JS", "NODEJS", "EXPRESS", "EXPRESS.JS", "DJANGO", "FLASK", "FASTAPI", 
            "SPRING BOOT", "ASP.NET", "LARAVEL", "RUBY ON RAILS", "GRAPHQL", "REST API",
            # Databases & Storage
            "SQL", "MYSQL", "POSTGRESQL", "POSTGRES", "MONGODB", "SQLITE", "REDIS", 
            "ORACLE", "FIREBASE", "CASSANDRA", "DYNAMODB", "MARIADB", "SUPABASE",
            # Cloud, DevOps & Infrastructure
            "AWS", "AZURE", "GOOGLE CLOUD", "GCP", "DOCKER", "KUBERNETES", "GIT", "GITHUB", 
            "GITLAB", "CI/CD", "JENKINS", "TERRAFORM", "LINUX", "UBUNTU", "NGINX", "APACHE",
            # Data Science, AI & ML
            "MACHINE LEARNING", "DEEP LEARNING", "ARTIFICIAL INTELLIGENCE", "NLP", 
            "COMPUTER VISION", "TENSORFLOW", "PYTORCH", "SCIKIT-LEARN", "PANDAS", "NUMPY", 
            "MATPLOTLIB", "SEABORN", "POWER BI", "TABLEAU", "EXCEL", "BIG DATA", "SPARK", "HADOOP",
            # Methodologies & Architecture
            "AGILE", "SCRUM", "JIRA", "MICROSERVICES", "OOP", "DATA STRUCTURES", "ALGORITHMS"
        }
        
        self.education_levels = {
            "PH.D": 100, "M.TECH": 100, "M.SC": 100, "MBA": 95, "MCA": 95, 
            "B.TECH": 90, "BE": 90, "BCA": 85, "B.SC": 80, "BBA": 80, "B.COM": 75, "DIPLOMA": 70
        }
        
        self.name_noise_words = {"RESUME", "CV", "CURRICULUM VITAE", "BIO-DATA", "PROFILE", "CONTACT", "EMAIL", "PHONE", "ADDRESS", "PAGE", "OF"}

    # ==========================================
    # 🧹 TEXT CLEANER
    # ==========================================
    def _clean_text(self, text: str) -> str:
        if not text:
            return ""
        text = re.sub(r'\t+', ' ', text)
        text = re.sub(r'\r+', '', text)
        text = re.sub(r'\n+', '\n', text)
        text = re.sub(r' +', ' ', text)
        return text.strip()

    # ==========================================
    # ⭐ GRACEFUL OCR FALLBACK ENGINE (DEBUGGED)
    # ==========================================
    def _extract_via_ocr(self, pdf_path: str) -> str:
        print("\n" + "🔍 [OCR ENGINE] Starting Cloud OCR Process...")

        api_key = os.getenv("GEMINI_API_KEY")
        print(f"🔑 [OCR ENGINE] API Key Loaded: {bool(api_key)}")

        try:
            import google.generativeai as genai
            if not api_key:
                print("❌ [OCR ENGINE] No API Key found in .env")
                return "OCR_OPTIONAL_SKIP: No API Key found."
            
            genai.configure(api_key=api_key)
            uploaded_doc = genai.upload_file(path=pdf_path, display_name="Scanned_Resume_OCR")
            
            # Using stable gemini-1.5-flash model
            model = genai.GenerativeModel(model_name="gemini-1.5-flash")
            
            # Strict OCR prompt to prevent AI summarization/hallucination
            prompt = (
                "You are an expert OCR system. Read this scanned PDF resume image and transcriptor "
                "extract ALL written text line-by-line exactly as it appears. "
                "Include candidate name, email, phone number, education, work experience, and all skills. "
                "Do not summarize, do not generate fake candidate data, and do not add conversational notes."
            )
            
            response = model.generate_content([uploaded_doc, prompt])
            genai.delete_file(uploaded_doc.name)
            
            extracted_text = response.text if response.text else ""
            return extracted_text
            
        except Exception as e:
            print(f"❌ [OCR ENGINE] Exception Occurred: {str(e)}")
            return f"OCR_OPTIONAL_SKIP: {str(e)}"

    # ==========================================
    # 🧠 EXTRACTION HEURISTICS
    # ==========================================
    def _extract_email(self, text: str) -> str:
        emails = re.findall(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', text)
        return emails[0] if emails else "Not Found"

    def _extract_phone(self, text: str) -> str:
        phone_pattern = r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
        phones = re.findall(phone_pattern, text)
        if phones:
            match = re.search(phone_pattern, text)
            return match.group().strip() if match else "Not Found"
        return "Not Found"

    def _extract_name(self, text: str) -> str:
        lines = text.split('\n')
        for line in lines[:10]:
            cleaned = line.strip()
            words = cleaned.split()
            if 0 < len(words) <= 3 and re.match(r"^[A-Za-z\s\.]+$", cleaned):
                upper_line = cleaned.upper()
                if not any(noise in upper_line for noise in self.name_noise_words):
                    return cleaned.title()
        return "Unknown Candidate"

    def _extract_skills(self, text: str) -> List[str]:
        text_upper = text.upper()
        found_skills = []
        for skill in sorted(self.skill_library):
            pattern = rf"\b{re.escape(skill)}\b"
            if re.search(pattern, text_upper):
                found_skills.append(skill)
        return found_skills

    def _extract_education(self, text: str) -> Tuple[str, int]:
        text_upper = text.upper()
        for edu, score in sorted(self.education_levels.items(), key=lambda x: x[1], reverse=True):
            pattern = rf"\b{re.escape(edu)}\b"
            clean_pattern = rf"\b{re.escape(edu.replace('.', ''))}\b"
            if re.search(pattern, text_upper) or re.search(clean_pattern, text_upper):
                return edu, score
        return "Not Found", 0

    def _extract_experience(self, text: str) -> Tuple[str, int]:
        text_lower = text.lower()
        exp_match = re.search(r'(\d+)\+?\s*(years?|yrs?)\s*(of)?\s*(experience|exp)?', text_lower)
        if exp_match:
            years = int(exp_match.group(1))
            if years >= 5: return f"{years} Years", 100
            if years >= 3: return f"{years} Years", 85
            if years >= 1: return f"{years} Years", 75
            
        if any(w in text_lower for w in ["senior", "lead", "manager"]): return "5+ Years (Est.)", 90
        if any(w in text_lower for w in ["associate", "junior"]): return "1-2 Years (Est.)", 70
        if any(w in text_lower for w in ["internship", "intern", "trainee"]): return "Internship", 40
        if any(w in text_lower for w in ["fresher", "entry level", "graduate"]): return "Fresher", 20
        return "Not Found", 0

    def _assess_resume_quality(self, text: str, extracted_skills: List[str]) -> Tuple[int, str]:
        text_lower = text.lower()
        sections = ["education", "experience", "projects", "certifications", "achievements", "summary"]
        found = sum(1 for sec in sections if re.search(rf"\b{sec}\b", text_lower))
        if len(extracted_skills) > 0: found += 1 

        score = min(int((found / 6) * 100), 100)
        quality = "Excellent" if score >= 80 else "Good" if score >= 60 else "Average" if score >= 40 else "Poor"
        return score, quality

    def _generate_snapshot(self, edu: str, exp: str, skills: List[str]) -> str:
        skill_txt = f"{len(skills)} verified skills" if skills else "No skills parsed"
        return f"{edu if edu != 'Not Found' else 'Graduate'} | {exp if exp != 'Not Found' else 'Fresher'} | {skill_txt}"

    def _generate_summary(self, name: str, edu: str, exp: str, skills: List[str]) -> str:
        top_skills = ", ".join(skills[:4]) if skills else "General technical concepts"
        return f"{name} is a {edu if edu != 'Not Found' else 'candidate'} with {exp} of experience. Demonstrates foundational proficiency in {top_skills}."

    def _calculate_confidence(self, name: str, email: str, phone: str, edu: str, exp: str, skills: List[str], is_ocr: bool) -> float:
        score = 0.0
        if name != "Unknown Candidate": score += 20.0
        if email != "Not Found": score += 20.0
        if phone != "Not Found": score += 15.0
        if edu != "Not Found": score += 15.0
        if exp != "Not Found": score += 10.0
        if len(skills) >= 3: score += 20.0
        elif len(skills) > 0: score += 10.0
        
        if is_ocr: score = max(score - 5.0, 10.0)
        return min(round(score, 1), 100.0)

    # ==========================================
    # 🚀 MAIN PARSING PIPELINE
    # ==========================================
    def parse_resume(self, pdf_path: str, existing_db_records: List[Dict] = None) -> Dict[str, Any]:
        start_time = time.time()
        existing_db_records = existing_db_records or []
        
        raw_text = ""
        text_with_layout = ""
        is_scanned_ocr = False
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    txt = page.extract_text()
                    if txt: raw_text += txt + "\n"
                    lay = page.extract_text(layout=True)
                    if lay: text_with_layout += lay + "\n"
        except Exception as e:
            return {"resume_status": f"Parsing Failed: {str(e)}"} 

        # Force OCR if text is less than 50 words
        if len(raw_text.split()) < 50:
            print("⚠️ PDF Text count < 50 words. Triggering Cloud OCR Engine...")
            ocr_text = self._extract_via_ocr(pdf_path)
            
            # 📌 PRINT EXACT OCR OUTPUT TO TERMINAL
            print("=" * 60)
            print("RAW OCR OUTPUT RETURNED FROM GEMINI:")
            print(ocr_text)
            print("=" * 60)

            if not ocr_text.startswith("OCR_OPTIONAL_SKIP"):
                raw_text = ocr_text
                is_scanned_ocr = True

        clean_text = self._clean_text(raw_text)

        name = self._extract_name(clean_text)
        email = self._extract_email(clean_text)
        phone = self._extract_phone(clean_text)
        skills = self._extract_skills(clean_text)

        print(f"🎯 Extracted Name  : {name}")
        print(f"📧 Extracted Email : {email}")
        print(f"🛠️ Extracted Skills: {skills}")

        edu_title, edu_score = self._extract_education(clean_text)
        exp_title, exp_score = self._extract_experience(clean_text)
        res_score, res_quality = self._assess_resume_quality(clean_text, skills)
        is_modern = any(k in clean_text.lower() for k in ["linkedin.com", "github.com", "portfolio", "certifications"])
        is_dual_col = (len(re.findall(r'[a-zA-Z0-9][ ]{10,}[a-zA-Z0-9]', text_with_layout)) > 3) if not is_scanned_ocr else False

        clean_curr_email = email.lower().strip() if email != "Not Found" else ""
        clean_curr_phone = re.sub(r'\D', '', phone) if phone != "Not Found" else ""
        is_duplicate = any(
            (clean_curr_email and str(rec.get("email", "")).lower().strip() == clean_curr_email) or 
            (clean_curr_phone and re.sub(r'\D', '', str(rec.get("phone", ""))) == clean_curr_phone)
            for rec in existing_db_records
        )

        exec_time = round(time.time() - start_time, 2)
        confidence = self._calculate_confidence(name, email, phone, edu_title, exp_title, skills, is_scanned_ocr)
        snapshot = self._generate_snapshot(edu_title, exp_title, skills)
        summary = self._generate_summary(name, edu_title, exp_title, skills)

        return {
            "name": name,
            "email": email,
            "phone": phone,
            "education": edu_title,
            "education_score": edu_score,
            "experience": exp_title,
            "experience_score": exp_score,
            "skills": skills,
            "raw_text": clean_text,
            "resume_score": res_score,
            "resume_quality": res_quality,
            "modern_resume": is_modern,
            "dual_column": is_dual_col,
            "duplicate": is_duplicate,
            "ocr_used": is_scanned_ocr,
            "extraction_confidence": confidence,  
            "extraction_time": exec_time,         
            "snapshot": snapshot,
            "candidate_summary": summary,
            "resume_status": "Parsed Successfully (Cloud OCR Used)" if is_scanned_ocr else "Parsed Successfully"
        }
    # ==========================================
    # ⭐ GRACEFUL OCR FALLBACK ENGINE (DEBUGGED)
    # ==========================================
    def _extract_via_ocr(self, pdf_path: str) -> str:
        print("\n" + "🔍 [OCR ENGINE] Starting Cloud OCR Process...")
        try:
            import google.generativeai as genai
            api_key = os.getenv("GEMINI_API_KEY")
            
            if not api_key:
                print("❌ [OCR ENGINE] No API Key found.")
                return "OCR_OPTIONAL_SKIP: No API Key found."
            
            genai.configure(api_key=api_key)
            uploaded_doc = genai.upload_file(path=pdf_path, display_name="Scanned_Resume_OCR")
            
            # 🔥 FIX: Wait for Google to finish processing the PDF
            while uploaded_doc.state.name == 'PROCESSING':
                print("⏳ [OCR ENGINE] Waiting for Gemini File Processing to complete...")
                time.sleep(2)
                uploaded_doc = genai.get_file(uploaded_doc.name)
                
            if uploaded_doc.state.name == 'FAILED':
                print("❌ [OCR ENGINE] Gemini rejected the file processing.")
                return "OCR_OPTIONAL_SKIP: File processing failed on Google servers."

            model = genai.GenerativeModel(model_name="gemini-3.6-flash")
            prompt = (
                "Extract all readable text from this scanned resume verbatim. "
                "Do not summarize, do not generate fake candidate data."
            )
            
            print("🚀 [OCR ENGINE] Extracting text...")
            response = model.generate_content([uploaded_doc, prompt])
            
            genai.delete_file(uploaded_doc.name)
            
            # 🔥 Safety Check: Will prevent code from crashing if blocked
            try:
                extracted_text = response.text
                return extracted_text if extracted_text else ""
            except ValueError:
                print(f"❌ [OCR ENGINE SAFETY BLOCK]: {response.prompt_feedback}")
                return "OCR_OPTIONAL_SKIP: Response blocked by Safety Filters."
            
        except Exception as e:
            # 🚨 THIS WILL REVEAL THE HIDDEN ERROR IN TERMINAL
            print(f"❌ [OCR ENGINE CRASHED]: {str(e)}") 
            return f"OCR_OPTIONAL_SKIP: {str(e)}"
