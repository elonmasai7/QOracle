import io
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


def generate_compliance_pdf(report: dict) -> bytes:
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    y = height - 50
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, y, "QuantumRisk Oracle - Compliance Report")
    y -= 25

    c.setFont("Helvetica", 10)
    c.drawString(50, y, f"Generated UTC: {report.get('generated_at_utc', 'N/A')}")
    y -= 18
    c.drawString(50, y, f"Tenant: {report.get('tenant', 'N/A')}")
    y -= 18
    c.drawString(50, y, f"Portfolio: {report.get('portfolio', 'N/A')}")
    y -= 25

    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Risk Summary")
    y -= 18

    c.setFont("Helvetica", 10)
    for key, value in report.get("risk_summary", {}).items():
        c.drawString(60, y, f"{key}: {value}")
        y -= 15
        if y < 80:
            c.showPage()
            y = height - 50
            c.setFont("Helvetica", 10)

    y -= 10
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Control Mapping")
    y -= 18
    c.setFont("Helvetica", 10)
    for key, value in report.get("controls", {}).items():
        c.drawString(60, y, f"{key}: {value}")
        y -= 15

    c.showPage()
    c.save()
    pdf_data = buffer.getvalue()
    buffer.close()
    return pdf_data
