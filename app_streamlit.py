import streamlit as st
import requests
from PIL import Image
import io

# --- Configuration ---
BACKEND_URL = "https://decades-million-yourself-executive.trycloudflare.com"  # Change if your backend runs elsewhere
ENHANCE_ENDPOINT = f"{BACKEND_URL}/enhance/"
REMOVE_ENHANCE_ENDPOINT = f"{BACKEND_URL}/remove-and-enhance/"

st.set_page_config(layout="wide") # Use wide layout for better image comparison
st.title("Image Enhancement App")

# --- Helper Function to call API ---
def call_api(endpoint_url, image_bytes, filename="image.png"):
    """Sends image bytes to the specified API endpoint and returns the result image."""
    files = {'file': (filename, image_bytes, 'image/png')} # Use filename for consistency
    try:
        response = requests.post(endpoint_url, files=files, timeout=180) # Increased timeout for potentially long processes
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)

        # Check if the response content type is an image
        if 'image' in response.headers.get('content-type', '').lower():
            result_image = Image.open(io.BytesIO(response.content))
            return result_image
        else:
            # Handle potential JSON error messages from FastAPI
            try:
                error_details = response.json()
                st.error(f"API Error: {error_details.get('detail') or error_details.get('error', 'Unknown error')}")
            except requests.exceptions.JSONDecodeError:
                st.error(f"API Error: Received non-image response. Status code: {response.status_code}")
            return None

    except requests.exceptions.RequestException as e:
        st.error(f"Network or API Error: {e}")
        return None
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
        return None


# --- Main Application Logic ---
uploaded_file = st.file_uploader("Choose an image...", type=["png", "jpg", "jpeg"])

if uploaded_file is not None:
    # Read image bytes
    image_bytes = uploaded_file.getvalue()
    original_image = Image.open(io.BytesIO(image_bytes))

    st.write("### Original Image")
    st.image(original_image, caption='Original Uploaded Image', use_column_width=True)

    st.divider() # Visual separator

    # --- Step 1: Enhance Only ---
    st.write("### Processing: Enhance Only")
    enhanced_image = None
    with st.spinner("Enhancing image... (this may take a moment)"):
        # Pass the original image bytes
        enhanced_image = call_api(ENHANCE_ENDPOINT, image_bytes, uploaded_file.name)

    # --- Step 2: Remove Background and Enhance ---
    st.write("### Processing: Remove Background & Enhance")
    remove_enhanced_image = None
    if enhanced_image: # Only proceed if first step was successful conceptually (or just proceed anyway)
         with st.spinner("Removing background and enhancing... (this may take longer)"):
            # Pass the original image bytes again
            # Make sure the uploaded_file object's internal pointer is reset if needed,
            # but getvalue() reads it all, so using image_bytes is safe.
            remove_enhanced_image = call_api(REMOVE_ENHANCE_ENDPOINT, image_bytes, uploaded_file.name)
    else:
         st.warning("Skipping 'Remove & Enhance' because the 'Enhance Only' step failed or returned no image.")


    st.divider() # Visual separator

    # --- Display Results ---
    st.write("## Results")
    col1, col2 = st.columns(2)

    with col1:
        st.write("### Enhanced Only")
        if enhanced_image:
            st.image(enhanced_image, caption='Enhanced Image', use_column_width=True)
        else:
            st.warning("Could not generate enhanced image.")

    with col2:
        st.write("### Background Removed & Enhanced")
        if remove_enhanced_image:
            st.image(remove_enhanced_image, caption='Background Removed & Enhanced Image', use_column_width=True)
        else:
            st.warning("Could not generate background removed & enhanced image.")

else:
    st.info("Please upload an image file to start processing.")
