# ABOUTME: Extracts structured data from resume PDFs and DOCX files
# ABOUTME: Parses contact info, skills, experience, education into JSON format

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional
import PyPDF2
from docx import Document


def extract_text_from_pdf(pdf_file: str) -> str:
    """Extract text from PDF file."""
    try:
        text = ""
        with open(pdf_file, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text += page.extract_text() + "\n"
        return text
    except Exception as e:
        print(f"[ERROR] Failed to read PDF: {e}")
        sys.exit(1)


def extract_text_from_docx(docx_file: str) -> str:
    """Extract text from DOCX file."""
    try:
        doc = Document(docx_file)
        text = "\n".join([para.text for para in doc.paragraphs])
        return text
    except Exception as e:
        print(f"[ERROR] Failed to read DOCX: {e}")
        sys.exit(1)


def extract_email(text: str) -> Optional[str]:
    """Extract email address from text."""
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    matches = re.findall(email_pattern, text)
    return matches[0] if matches else None


def extract_phone(text: str) -> Optional[str]:
    """Extract phone number from text."""
    # Various phone formats
    phone_patterns = [
        r'\+?\d{1,3}[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
        r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
        r'\d{3}[-.\s]?\d{3}[-.\s]?\d{4}'
    ]
    for pattern in phone_patterns:
        matches = re.findall(pattern, text)
        if matches:
            return matches[0]
    return None


def extract_urls(text: str) -> List[str]:
    """Extract URLs from text."""
    url_pattern = r'https?://(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&/=]*)'
    return re.findall(url_pattern, text)


def extract_name(text: str) -> Optional[str]:
    """Extract name (first line typically)."""
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    if lines:
        # Assume first non-empty line is name
        first_line = lines[0]
        # Filter out lines that look like job titles
        if len(first_line.split()) <= 4 and not any(keyword in first_line.lower() for keyword in ["engineer", "developer", "manager", "specialist"]):
            return first_line
    return None


def extract_skills(text: str) -> List[str]:
    """Extract skills from text."""
    # Common skill keywords
    skill_keywords = [
        "python", "javascript", "java", "c++", "c#", "ruby", "php", "swift", "kotlin",
        "react", "angular", "vue", "node", "django", "flask", "spring",
        "sql", "mongodb", "postgresql", "mysql", "redis",
        "aws", "azure", "gcp", "docker", "kubernetes",
        "git", "agile", "scrum", "jira",
        "machine learning", "ai", "data analysis", "statistics"
    ]

    found_skills = []
    text_lower = text.lower()

    for skill in skill_keywords:
        if skill in text_lower:
            found_skills.append(skill.title())

    return list(set(found_skills))  # Remove duplicates


def extract_education(text: str) -> List[str]:
    """Extract education information."""
    education_keywords = ["university", "college", "bachelor", "master", "phd", "degree", "b.s.", "m.s.", "b.a.", "m.a."]
    education = []

    lines = text.split("\n")
    for i, line in enumerate(lines):
        if any(keyword in line.lower() for keyword in education_keywords):
            education.append(line.strip())

    return education


def parse_resume(file_path: str) -> Dict:
    """
    Parse resume and extract structured data.

    Args:
        file_path: Path to resume file (PDF or DOCX)

    Returns:
        Dictionary with parsed resume data
    """
    path = Path(file_path)

    if not path.exists():
        print(f"[ERROR] File not found: {file_path}")
        sys.exit(1)

    print(f"[INFO] Parsing resume: {file_path}")

    # Extract text
    if path.suffix.lower() == ".pdf":
        text = extract_text_from_pdf(file_path)
    elif path.suffix.lower() == ".docx":
        text = extract_text_from_docx(file_path)
    else:
        print("[ERROR] File must be .pdf or .docx")
        sys.exit(1)

    # Extract data
    resume_data = {
        "name": extract_name(text),
        "email": extract_email(text),
        "phone": extract_phone(text),
        "urls": extract_urls(text),
        "skills": extract_skills(text),
        "education": extract_education(text),
        "raw_text": text[:500] + "..." if len(text) > 500 else text  # First 500 chars
    }

    return resume_data


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Parse resumes and extract structured data"
    )
    parser.add_argument(
        "resume",
        help="Resume file (PDF or DOCX)"
    )
    parser.add_argument(
        "-o", "--output",
        help="Output JSON file (prints to console if not specified)"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Include raw text in output"
    )

    args = parser.parse_args()

    resume_data = parse_resume(args.resume)

    if not args.verbose:
        resume_data.pop("raw_text", None)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(resume_data, f, indent=2)
        print(f"[OK] Resume data saved to {args.output}")
    else:
        print("\n[INFO] Parsed Resume Data:")
        print(json.dumps(resume_data, indent=2))


if __name__ == "__main__":
    main()
