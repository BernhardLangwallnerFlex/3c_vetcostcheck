import streamlit as st
import os
import json
from PIL import Image
import glob

def get_file_list(directory, extension):
    """Get list of files with specific extension from directory"""
    if not os.path.exists(directory):
        return []
    
    pattern = os.path.join(directory, f"*.{extension}")
    files = glob.glob(pattern)
    return [os.path.basename(f) for f in sorted(files)]

def load_json_file(json_path):
    """Load and return JSON content"""
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Error loading JSON file: {str(e)}")
        return None

def main():
    st.set_page_config(
        page_title="Info-Extraction Tierarzt-Rechnungen",
        page_icon="🐕",
        layout="wide"
    )
    
    # Header
    st.title("🐕 Info-Extraction Tierarzt-Rechnungen")
    st.markdown("---")
    
    # Create two columns for dropdowns
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📷 Select Image")
        image_dir = "3C_testdaten_jpg"
        image_files = get_file_list(image_dir, "jpg")
        
        if not image_files:
            st.warning(f"No JPG files found in {image_dir}")
            selected_image = None
        else:
            selected_image = st.selectbox(
                "Choose an image file:",
                options=image_files,
                index=0,
                key="image_selector"
            )
    
    with col2:
        st.subheader("📄 Select JSON")
        json_dir = "3C_testdaten_json"
        json_files = get_file_list(json_dir, "json")
        
        if not json_files:
            st.warning(f"No JSON files found in {json_dir}")
            selected_json = None
        else:
            selected_json = st.selectbox(
                "Choose a JSON file:",
                options=json_files,
                index=0,
                key="json_selector"
            )
    
    st.markdown("---")
    
    # Display content in two columns
    if selected_image or selected_json:
        col_left, col_right = st.columns(2)
        
        with col_left:
            st.subheader("📷 Input Image")
            if selected_image:
                image_path = os.path.join(image_dir, selected_image)
                try:
                    image = Image.open(image_path)
                    st.image(image, caption=selected_image, width='stretch')
                except Exception as e:
                    st.error(f"Error loading image: {str(e)}")
            else:
                st.info("No image selected")
        
        with col_right:
            st.subheader("📄 Extracted Data")
            if selected_json:
                json_path = os.path.join(json_dir, selected_json)
                json_data = load_json_file(json_path)
                if json_data:
                    st.json(json_data)
                else:
                    st.error("Failed to load JSON data")
            else:
                st.info("No JSON selected")
    
    else:
        st.info("Please select both an image and a JSON file to view the extraction results.")
    
    # Footer with file counts
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Images Available", len(image_files))
    
    with col2:
        st.metric("JSON Files Available", len(json_files))
    
    with col3:
        if selected_image and selected_json:
            st.success("✅ Both files selected")
        else:
            st.warning("⚠️ Select files to view")

if __name__ == "__main__":
    main()
