
import time
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer

def text_to_pdf(base_text, chunk_size=4096):
    styles = getSampleStyleSheet()

    start_time = time.time()
    print("Cleaning text")

    # Initialize variables
    offset = 0
    text_length = len(base_text)
    pdf_data = None
    Story = []

    # Create a BytesIO object to hold the PDF data
    buffer = BytesIO()

    # Initialize PDF
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=18
    )

    try:
        while offset < text_length:
            print(f"Processing chunk starting at offset {offset}")
            # Get the next chunk
            chunk = base_text[offset:offset + chunk_size]
            chunk = chunk.replace("<", "&lt;")
            chunk = chunk.replace(">", "&gt;")
            chunk = chunk.replace("\n", "<br/>")
            chunk = chunk.replace("<br />", "<br/>")
            chunk = chunk.replace("<br>", "<br/>")
            
            # Create Paragraph and append to Story
            Story.append(Paragraph(chunk, styles['Normal']))
            Story.append(Spacer(1, 0.2 * 72))  # Add a small space between chunks
            offset += chunk_size

        print("Building pdf")
        build_start = time.time()
        doc.build(Story)
        build_end = time.time()
        print(f"Success: PDF generated in {build_end - build_start:.2f} seconds.")
        end_time = time.time()
        print(f"Total time taken: {end_time - start_time:.2f} seconds.")

        # Retrieve PDF data for further processing
        pdf_data = buffer.getvalue()
        return pdf_data
    except Exception as e:
        print(f"Failure: An error occurred during PDF generation: {e}")
        return None

    finally:
        
        buffer.close()

