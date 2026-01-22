import streamlit as st
import csv
import zipfile
import io
from PyPDF2 import PdfReader

st.set_page_config(page_title="PDF Address Extractor", layout="centered")
st.title("PDF → Address CSV Extractor")
st.markdown('''
Common find and replace (case sensitive):  
"r ," → "r,"  
"W a" → "Wa"  
"V i" → "Vi"  
"f f" → "ff"  
"1 1" → "11"  
''')

def extract_addresses_from_pdf(file_like):
    """Extract text from each page of a PDF file-like object."""
    addresses = []
    reader = PdfReader(file_like)

    for page in reader.pages:
        text = page.extract_text()
        if text:
            cleaned = "\n".join(
                line.strip() for line in text.splitlines() if line.strip()
            )
            addresses.append(cleaned)

    return addresses


uploaded_files = st.file_uploader(
    "Select one or more PDF files",
    type="pdf",
    accept_multiple_files=True
)

if uploaded_files:
    if st.button("Process PDFs"):
        zip_buffer = io.BytesIO()

        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            for pdf in uploaded_files:
                st.write(f"Processing **{pdf.name}**")

                addresses = extract_addresses_from_pdf(pdf)

                # Create CSV in memory
                csv_buffer = io.StringIO()
                writer = csv.writer(csv_buffer)
                writer.writerow(["Address"])
                for addr in addresses:
                    writer.writerow([addr])

                base_name = pdf.name.rsplit(".", 1)[0]
                zip_file.writestr(
                    f"{base_name}.csv",
                    csv_buffer.getvalue()
                )

        zip_buffer.seek(0)

        st.success("Processing complete!")

        st.download_button(
            label="Download all CSVs (ZIP)",
            data=zip_buffer,
            file_name="address_csvs.zip",
            mime="application/zip"
        )
