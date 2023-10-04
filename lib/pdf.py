from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph

def text_to_pdf(text):
    buffer = BytesIO()
    styles = getSampleStyleSheet()
    width, height = letter
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=18
    )
    text = text.replace("\n", "<br />")

    Story = [Paragraph(text, styles['Normal'])]
    doc.build(Story)
    pdf_bytes = buffer.getvalue()
    buffer.close()

    return pdf_bytes
