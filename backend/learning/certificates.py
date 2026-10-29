import io
import hashlib
from datetime import datetime
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

def generate_completion_certificate(learning_path):
    """
    Generates a PDF Certificate of Completion for a LearningPath.
    Returns a BytesIO buffer containing the PDF bytes.
    """
    buffer = io.BytesIO()
    user = learning_path.user
    skill = learning_path.skill

    # 11 x 8.5 inches in points
    width, height = landscape(letter)
    p = canvas.Canvas(buffer, pagesize=landscape(letter))

    # Certificate ID
    cert_id = hashlib.sha256(
        f"{user.username}-{skill.name}-{learning_path.id}".encode()
    ).hexdigest()[:12].upper()

    # Background fill
    p.setFillColor(colors.HexColor("#FCFDFD"))
    p.rect(0, 0, width, height, fill=True, stroke=False)

    # Outer decorative border (Indigo)
    p.setStrokeColor(colors.HexColor("#312E81"))
    p.setLineWidth(5)
    p.rect(30, 30, width - 60, height - 60)

    # Inner decorative border (Golden/Amber)
    p.setStrokeColor(colors.HexColor("#D97706"))
    p.setLineWidth(1.5)
    p.rect(38, 38, width - 76, height - 76)

    # Top Brand / Crest
    p.setFillColor(colors.HexColor("#4F46E5"))
    p.setFont("Helvetica-Bold", 14)
    p.drawCentredString(width / 2.0, height - 85, "LEARNINGPATH.AI ACADEMY")

    # Main Title
    p.setFillColor(colors.HexColor("#0F172A"))
    p.setFont("Helvetica-Bold", 34)
    p.drawCentredString(width / 2.0, height - 130, "Certificate of Completion")

    # Subtitle
    p.setFillColor(colors.HexColor("#64748B"))
    p.setFont("Helvetica", 13)
    p.drawCentredString(width / 2.0, height - 165, "THIS IS PROUDLY PRESENTED TO")

    # Learner Name
    learner_name = user.get_full_name() or user.username
    p.setFillColor(colors.HexColor("#1E1B4B"))
    p.setFont("Helvetica-Bold", 30)
    p.drawCentredString(width / 2.0, height - 215, learner_name)

    # Underline for name
    p.setStrokeColor(colors.HexColor("#CBD5E1"))
    p.setLineWidth(1)
    p.line(width / 2.0 - 180, height - 225, width / 2.0 + 180, height - 225)

    # Statement of Achievement
    p.setFillColor(colors.HexColor("#475467"))
    p.setFont("Helvetica", 13)
    p.drawCentredString(
        width / 2.0,
        height - 260,
        "for successfully fulfilling all curriculum requirements and demonstrating mastery in",
    )

    # Skill / Course Name
    p.setFillColor(colors.HexColor("#4F46E5"))
    p.setFont("Helvetica-Bold", 24)
    p.drawCentredString(width / 2.0, height - 295, skill.name)

    # Metrics summary
    total_hours = round(learning_path.total_duration_minutes / 60.0, 1)
    p.setFillColor(colors.HexColor("#64748B"))
    p.setFont("Helvetica-Oblique", 11)
    p.drawCentredString(
        width / 2.0,
        height - 330,
        f"Completed {learning_path.total_items} difficulty-ranked modules ({total_hours} study hours total)",
    )

    # Bottom Signatures & Verification
    issue_date = datetime.now().strftime("%B %d, %Y")

    # Left: Date Issued
    p.setFont("Helvetica", 10)
    p.setFillColor(colors.HexColor("#475467"))
    p.drawString(90, 95, f"Date Issued: {issue_date}")
    p.drawString(90, 80, f"Certificate ID: LP-{cert_id}")
    p.setStrokeColor(colors.HexColor("#94A3B8"))
    p.line(90, 110, 260, 110)

    # Right: Academic Director Signature
    p.drawString(width - 270, 95, "Dr. Sarah Chen, Academic Director")
    p.drawString(width - 270, 80, "LearningPath Certification Authority")
    p.setStrokeColor(colors.HexColor("#94A3B8"))
    p.line(width - 270, 110, width - 90, 110)

    # Seal in center
    p.setFillColor(colors.HexColor("#FEF3C7"))
    p.setStrokeColor(colors.HexColor("#D97706"))
    p.setLineWidth(2)
    p.circle(width / 2.0, 95, 30, fill=True, stroke=True)
    p.setFillColor(colors.HexColor("#B45309"))
    p.setFont("Helvetica-Bold", 8)
    p.drawCentredString(width / 2.0, 98, "VERIFIED")
    p.drawCentredString(width / 2.0, 88, "EXCELLENCE")

    p.showPage()
    p.save()

    buffer.seek(0)
    return buffer
