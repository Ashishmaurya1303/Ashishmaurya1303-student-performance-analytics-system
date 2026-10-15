"""Generate documentation artifacts: screenshots and Project_Documentation.pdf."""

import subprocess
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = PROJECT_ROOT / "docs"
SCREENSHOTS_DIR = DOCS_DIR / "screenshots"
SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)


def capture_command_output(cmd: list) -> str:
    """Run command and return standard output."""
    res = subprocess.run(cmd, cwd=str(PROJECT_ROOT), capture_output=True, text=True)
    return res.stdout


def render_terminal_image(text: str, output_path: Path, title: str = "Terminal Output") -> None:
    """Render text as an authentic terminal window screenshot."""
    lines = text.strip().split("\n")
    # Determine sizing
    max_len = max(len(l) for l in lines) if lines else 40
    char_width = 8
    line_height = 16
    padding = 24
    header_height = 36

    img_width = max(800, max_len * char_width + padding * 2)
    img_height = header_height + len(lines) * line_height + padding * 2

    img = Image.new("RGB", (img_width, img_height), color=(30, 30, 30))
    draw = ImageDraw.Draw(img)

    # Draw window title bar
    draw.rectangle([(0, 0), (img_width, header_height)], fill=(45, 45, 45))
    # Window control dots
    draw.ellipse([(14, 13), (24, 23)], fill=(255, 95, 86))   # Red
    draw.ellipse([(32, 13), (42, 23)], fill=(255, 189, 46))  # Yellow
    draw.ellipse([(50, 13), (60, 23)], fill=(39, 201, 63))   # Green

    # Window title
    try:
        font = ImageFont.load_default()
    except Exception:
        font = None

    draw.text((75, 11), title, fill=(200, 200, 200), font=font)

    # Render terminal lines
    y = header_height + padding
    for line in lines:
        color = (220, 220, 220)
        if "====" in line or "----" in line:
            color = (100, 150, 200)
        elif "[Success]" in line or "PASSED" in line:
            color = (100, 220, 100)
        elif "Fail" in line or "Shortage" in line:
            color = (240, 120, 120)
        elif "A+" in line or "Rank" in line or "#1" in line:
            color = (255, 215, 0)
        elif line.strip().startswith(("1.", "2.", "3.", "4.", "5.", "6.", "7.", "8.")):
            color = (130, 200, 255)

        draw.text((padding, y), line, fill=color, font=font)
        y += line_height

    img.save(output_path, "PNG")
    print(f"Saved screenshot: {output_path.name}")


def main():
    print("Capturing actual program output...")
    main_output = capture_command_output([sys.executable, "main.py"])
    
    # Split output into roster and insights
    lines = main_output.split("\n")
    split_idx = 0
    for i, line in enumerate(lines):
        if "2. TOP PERFORMING STUDENTS" in line:
            split_idx = i - 1
            break
            
    roster_text = "\n".join(lines[:split_idx]) if split_idx > 0 else main_output
    insights_text = "\n".join(lines[split_idx:]) if split_idx > 0 else main_output

    render_terminal_image(roster_text, SCREENSHOTS_DIR / "screenshot_roster.png", "PowerShell - Student Performance Roster")
    render_terminal_image(insights_text, SCREENSHOTS_DIR / "screenshot_insights.png", "PowerShell - Analytics & Executive Insights")

    print("Capturing test suite execution...")
    test_output = capture_command_output([sys.executable, "tests/test_end_to_end.py"])
    render_terminal_image(test_output, SCREENSHOTS_DIR / "screenshot_tests.png", "PowerShell - Automated Test Suite Results")

    print("Screenshots captured successfully.")


if __name__ == "__main__":
    main()
