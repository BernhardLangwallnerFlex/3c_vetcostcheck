import os
import fitz  # PyMuPDF
from PIL import Image
import glob

def pdf_to_jpg(pdf_path, output_dir="converted_images", dpi=300):
    """
    Convert PDF to JPG image(s), concatenating multiple pages into one image.
    
    Args:
        pdf_path: Path to the PDF file
        output_dir: Directory to save the JPG files
        dpi: DPI for rendering (higher = better quality, larger file)
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Open the PDF
    pdf_document = fitz.open(pdf_path)
    
    # Get PDF filename without extension
    pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]
    
    print(f"Processing {pdf_name}.pdf with {len(pdf_document)} page(s)...")
    
    # Convert each page to image
    page_images = []
    for page_num in range(len(pdf_document)):
        page = pdf_document[page_num]
        
        # Render page to image
        mat = fitz.Matrix(dpi/72, dpi/72)  # 72 is default DPI
        pix = page.get_pixmap(matrix=mat)
        
        # Convert to PIL Image
        img_data = pix.tobytes("png")
        img = Image.open(io.BytesIO(img_data))
        page_images.append(img)
        
        print(f"  Converted page {page_num + 1}")
    
    # Concatenate all pages vertically
    if len(page_images) == 1:
        # Single page - just save it
        final_image = page_images[0]
    else:
        # Multiple pages - concatenate vertically
        # Calculate total height
        total_height = sum(img.height for img in page_images)
        max_width = max(img.width for img in page_images)
        
        # Create new image with total dimensions
        final_image = Image.new('RGB', (max_width, total_height), 'white')
        
        # Paste each page image
        y_offset = 0
        for img in page_images:
            # Center the image horizontally if it's narrower than the max width
            x_offset = (max_width - img.width) // 2
            final_image.paste(img, (x_offset, y_offset))
            y_offset += img.height
    
    # Save the final image
    output_path = os.path.join(output_dir, f"{pdf_name}.jpg")
    final_image.save(output_path, 'JPEG', quality=95)
    
    print(f"  Saved: {output_path}")
    print(f"  Final image size: {final_image.width}x{final_image.height}")
    
    # Close the PDF
    pdf_document.close()
    
    return output_path

def convert_all_pdfs(input_dir="3C_testdaten", output_dir="converted_images"):
    """
    Convert all PDFs in the input directory to JPG images.
    
    Args:
        input_dir: Directory containing PDF files
        output_dir: Directory to save JPG files
    """
    # Find all PDF files
    pdf_pattern = os.path.join(input_dir, "*.pdf")
    pdf_files = glob.glob(pdf_pattern)
    
    if not pdf_files:
        print(f"No PDF files found in {input_dir}")
        return
    
    print(f"Found {len(pdf_files)} PDF file(s) to convert:")
    for pdf_file in pdf_files:
        print(f"  - {os.path.basename(pdf_file)}")
    
    print("\nStarting conversion...")
    print("=" * 50)
    
    converted_files = []
    for pdf_file in pdf_files:
        try:
            output_path = pdf_to_jpg(pdf_file, output_dir)
            converted_files.append(output_path)
            print()  # Empty line for readability
        except Exception as e:
            print(f"Error converting {pdf_file}: {str(e)}")
            print()
    
    print("=" * 50)
    print(f"Conversion complete! {len(converted_files)} file(s) converted.")
    print(f"Output directory: {output_dir}")

if __name__ == "__main__":
    import io  # Import here to avoid issues if not needed
    
    # Convert all PDFs in the 3C_testdaten folder
    convert_all_pdfs("3C_testdaten_pdf", "3C_testdaten_jpg")
