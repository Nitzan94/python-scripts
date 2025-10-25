# ABOUTME: Claude Agent SDK integration for generating new utility scripts
# ABOUTME: Generates scripts following project patterns with CLI args, error handling, type hints

import asyncio
import os
import re
from pathlib import Path
from typing import Dict, List, Optional
from claude_agent_sdk import query, ClaudeAgentOptions


SYSTEM_PROMPT = """You are an expert Python developer creating utility scripts for a collection.

CRITICAL REQUIREMENTS:
1. **File Headers**: Every file starts with exactly 2 ABOUTME comments:
   ```python
   # ABOUTME: Brief description of what this file does
   # ABOUTME: Key responsibility or purpose
   ```

2. **Code Style**:
   - Type hints on ALL functions
   - Argparse for CLI arguments (never hardcoded values)
   - Comprehensive error handling (try/except with sys.exit(1))
   - ASCII-only output: [OK], [ERROR], [WARN], [INFO] (NO Unicode symbols)
   - Docstrings for public functions

3. **Structure**:
   ```python
   # ABOUTME: ...
   # ABOUTME: ...

   import argparse
   import sys
   from pathlib import Path
   from typing import Dict, List, Optional
   # ... other imports

   def main_function(param: str) -> ReturnType:
       \"\"\"Function docstring.\"\"\"
       try:
           # Implementation
           print("[OK] Success message")
       except SpecificError as e:
           print(f"[ERROR] {e}")
           sys.exit(1)

   def main() -> None:
       parser = argparse.ArgumentParser(description="...")
       parser.add_argument("required", help="...")
       parser.add_argument("-o", "--optional", help="...")
       args = parser.parse_args()
       main_function(args.required)

   if __name__ == "__main__":
       main()
   ```

4. **Output Standards**:
   - Windows-compatible (no emoji, no Unicode)
   - Clear progress indicators
   - Helpful error messages

Generate ONLY the complete Python code. No explanations, no markdown blocks.
Start with the ABOUTME comments."""


async def generate_script_async(description: str, example_scripts: List[str] = None) -> Dict:
    """
    Generate script using Claude Agent SDK.

    Args:
        description: User description of desired script
        example_scripts: Optional list of existing scripts to use as examples

    Returns:
        Dict with: code, filename, dependencies, usage
    """
    # Build prompt with examples
    prompt = f"""Create a Python utility script based on this description:

{description}

REQUIREMENTS:
- Follow the SYSTEM PROMPT structure exactly
- Use argparse for CLI arguments
- Include comprehensive error handling
- Type hints on all functions
- ASCII-only output ([OK], [ERROR], [WARN], [INFO])
- Two ABOUTME file headers at top

"""

    if example_scripts:
        prompt += "\nEXAMPLE SCRIPTS TO MATCH STYLE:\n"
        for script in example_scripts[:2]:  # Limit to 2 examples
            prompt += f"\n---\n{script[:500]}...\n"

    prompt += """

OUTPUT FORMAT:
Return ONLY valid Python code. No markdown, no explanations.
Start with # ABOUTME comments."""

    # Configure SDK options
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY not set")

    options = ClaudeAgentOptions(
        system_prompt={"type": "text", "text": SYSTEM_PROMPT},
        model="claude-sonnet-4-20250514",
        allowed_tools=["Read"],  # Allow reading example scripts
        permission_mode="acceptEdits",
        max_turns=5
    )

    # Query agent
    generated_code = ""
    async for message in query(prompt=prompt, options=options):
        if hasattr(message, 'text'):
            generated_code += message.text

    # Extract code (remove any markdown if present)
    code = extract_code(generated_code)

    # Analyze dependencies
    dependencies = extract_dependencies(code)

    # Generate filename
    filename = generate_filename(description, code)

    # Generate usage instructions
    usage = generate_usage_instructions(filename, code)

    return {
        "code": code,
        "filename": filename,
        "dependencies": dependencies,
        "usage": usage
    }


def extract_code(text: str) -> str:
    """Extract Python code from response, removing markdown if present."""
    # Remove markdown code blocks if present
    if "```python" in text:
        match = re.search(r'```python\n(.*?)```', text, re.DOTALL)
        if match:
            return match.group(1).strip()
    elif "```" in text:
        match = re.search(r'```\n(.*?)```', text, re.DOTALL)
        if match:
            return match.group(1).strip()

    # Return as-is if no markdown
    return text.strip()


def extract_dependencies(code: str) -> List[str]:
    """Extract third-party dependencies from import statements."""
    # Standard library modules to exclude
    stdlib = {
        'abc', 'argparse', 'asyncio', 'base64', 'collections', 'csv',
        'datetime', 'email', 'functools', 'hashlib', 'http', 'io', 'itertools',
        'json', 'logging', 'math', 'os', 'pathlib', 'random', 're', 'shutil',
        'socket', 'sqlite3', 'string', 'subprocess', 'sys', 'tempfile',
        'threading', 'time', 'typing', 'urllib', 'uuid', 'warnings', 'xml'
    }

    dependencies = set()

    # Find all imports
    import_pattern = r'(?:from|import)\s+([a-zA-Z0-9_]+)'
    matches = re.findall(import_pattern, code)

    for module in matches:
        # Skip standard library
        if module not in stdlib:
            # Map common module names to package names
            package_map = {
                'PIL': 'Pillow',
                'cv2': 'opencv-python',
                'bs4': 'beautifulsoup4',
                'docx': 'python-docx'
            }
            package = package_map.get(module, module)
            dependencies.add(package)

    return sorted(list(dependencies))


def generate_filename(description: str, code: str) -> str:
    """Generate appropriate filename from description."""
    # Try to extract from code if it has a clear name pattern
    aboutme_match = re.search(r'# ABOUTME: ([^\n]+)', code)
    if aboutme_match:
        desc = aboutme_match.group(1).strip()
    else:
        desc = description

    # Clean and title case
    words = re.findall(r'\w+', desc)
    filename = ' '.join(words[:4]).title()  # Max 4 words

    return f"{filename}.py"


def generate_usage_instructions(filename: str, code: str) -> str:
    """Generate CLI usage instructions from argparse definition."""
    # Try to extract from argparse
    usage_lines = [f"python \"{filename}\""]

    # Find required arguments
    required_pattern = r'add_argument\(["\']([^"\']+)["\'](?!.*(?:action|--)).*help=["\']([^"\']+)'
    required_args = re.findall(required_pattern, code)

    for arg, help_text in required_args:
        if not arg.startswith('-'):
            usage_lines[0] += f" <{arg}>"

    # Find optional arguments
    optional_pattern = r'add_argument\(["\'](-[^"\']+)["\'].*help=["\']([^"\']+)'
    optional_args = re.findall(optional_pattern, code)

    usage = usage_lines[0]

    if optional_args:
        usage += "\n\nOptions:"
        for flag, help_text in optional_args[:5]:  # Limit to 5
            usage += f"\n  {flag}: {help_text}"

    return usage


def generate_script(description: str, example_scripts: List[str] = None) -> Dict:
    """
    Synchronous wrapper for generate_script_async.

    Args:
        description: User description of desired script
        example_scripts: Optional list of existing scripts

    Returns:
        Dict with: code, filename, dependencies, usage
    """
    return asyncio.run(generate_script_async(description, example_scripts))


def get_example_scripts(limit: int = 2) -> List[str]:
    """Read existing scripts as examples."""
    scripts_dir = Path(__file__).parent
    examples = []

    # Get a few existing scripts
    script_files = [
        "QR Code Tool.py",
        "Weather Alert.py",
        "EXIF Editor.py"
    ]

    for filename in script_files[:limit]:
        filepath = scripts_dir / filename
        if filepath.exists():
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    examples.append(f.read())
            except:
                continue

    return examples
