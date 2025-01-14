import gradio as gr
from main import extract_content_and_summarize_text
import tempfile
import os
import re

def process_pdf(file):
    """Process the uploaded PDF file and stream the summary."""
    if file is None:
        return "Please upload a PDF file to begin."
    
    try:
        # Create a temporary file to store the uploaded PDF
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            tmp_file.write(file)
            tmp_file_path = tmp_file.name
        
        # Start with markdown headers
        summary = "# Research Paper Summary\n\n"
        
        # Stream the content with markdown formatting
        for chunk in extract_content_and_summarize_text(tmp_file_path):
            if chunk:
                # Format any line that looks like a section header
                # This matches lines that start with optional numbers followed by text and a colon
                formatted_chunk = re.sub(
                    r'(?:^|\n)(?:\d+\.\s*)?([A-Z][^:]+):',
                    r'\n## \1',
                    chunk
                )
                
                summary += formatted_chunk
                yield summary
        
        # Clean up
        os.unlink(tmp_file_path)
        
    except Exception as e:
        yield f"An error occurred while processing the PDF: {str(e)}"

# Create Gradio interface
demo = gr.Interface(
    fn=process_pdf,
    inputs=gr.File(
        label="Upload Research Paper (PDF)",
        file_types=[".pdf"],
        type="binary"
    ),
    outputs=gr.Markdown(),
    title="Research Paper Summarizer",
    description="📄 Upload your research paper PDF to generate an AI-powered summary including key findings, methods, and conclusions.",
    flagging_mode='never'
)

if __name__ == "__main__":
    demo.launch(
        inbrowser = True
    )