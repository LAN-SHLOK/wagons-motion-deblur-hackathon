import os
from html2docx import html2docx
from bs4 import BeautifulSoup

# ============================
# CONFIGURATION
# ============================

HTML_FILE = "Untitled 2e05af9383af806089f0d66cbbbbe603.html"   # Your HTML file
OUTPUT_DOCX = "Converted_Document.docx"                    # Output Word file

# ============================
# MAIN LOGIC
# ============================

def convert_html_to_docx(html_file, output_docx):
    if not os.path.exists(html_file):
        print(f"❌ HTML file not found: {html_file}")
        return

    # Read HTML content
    with open(html_file, "r", encoding="utf-8") as file:
        html_content = file.read()

    # Parse HTML for debugging and validation
    soup = BeautifulSoup(html_content, "html.parser")

    # Check for images
    images = soup.find_all("img")
    if images:
        print(f"🖼 Found {len(images)} image(s) in the HTML:")
        for img in images:
            print("   →", img.get("src"))
    else:
        print("⚠ No images found in HTML.")

    # Convert HTML to DOCX
    try:
        docx = html2docx(html_content)
        with open(output_docx, "wb") as f:
            f.write(docx)

        print("\n✅ Conversion successful!")
        print(f"📄 Word file created: {output_docx}")

    except Exception as e:
        print("\n❌ Conversion failed.")
        print("Error:", e)


# ============================
# RUN SCRIPT
# ============================

if __name__ == "__main__":
    convert_html_to_docx(HTML_FILE, OUTPUT_DOCX)
