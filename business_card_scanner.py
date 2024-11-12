import pandas as pd
import streamlit as st
from streamlit_option_menu import option_menu
import easyocr
import psycopg2
from psycopg2 import pool
import cv2
import os
import matplotlib.pyplot as plt
import re
from contextlib import contextmanager
import time
from typing import Optional, Dict, Any
import numpy as np


def load_css():
    st.markdown(
        """
        <style>
        /* Main Theme */
        [data-testid="stSidebar"] {
            background-color: #f8f9fa;
        }
        
        /* Header Styles */
        .main-header {
            font-size: 2.5rem;
            color: black;
            text-align: center;
            padding: 1.5rem;
            background: linear-gradient(to right, #a8e6cf, #dcedc1);
            border-radius: 10px;
            margin-bottom: 2rem;
        }
        
        /* Button Styles */
        .stButton > button {
            width: 100%;
            padding: 0.5rem;
            border-radius: 5px;
            background-color: #4CAF50 !important;
        }

        .stButton > button {
            color: white !important;
        }

        .stButton > button span {
            color: white !important;
        }

        .stButton > button:hover {
            background-color: #45a049 !important;
            color: white !important;
        }

        /* Form Submit Button */
        .stForm [data-baseweb="button"] {
            background-color: #4CAF50 !important;
            color: white !important;
        }

        button[kind="primary"] {
            background-color: #4CAF50 !important;
            color: white !important;
        }

        button[type="submit"] {
            background-color: #4CAF50 !important;
            color: white !important;
        }
        
        /* Input Field Styles */
        .stTextInput > div > div > input {
            border-radius: 5px;
            border: 1px solid #ccc;
            padding: 0.5rem;
        }
        .stExpander {
            color: white;
        }
        
        /* Upload Section Styles */
        .upload-section {
            border: 2px dashed #cccccc;
            border-radius: 5px;
            padding: 2rem;
            text-align: center;
            margin: 1rem 0;
        }
        
        /* Message Styles */
        .success-message {
            padding: 1rem;
            background-color: #d4edda;
            color: black ;
            border-radius: 5px;
            margin: 1rem 0;
        }
        
        .error-message {
            padding: 1rem;
            background-color: #f8d7da;
            color: black !important;
            border-radius: 5px;
            margin: 1rem 0;
        }
        
        .info-box {
            padding: 1rem;
            background-color: #e2e3e5;
            border-radius: 5px;
            margin: 1rem 0;
        }
        
        /* Card Styles */
        .card {
            padding: 1rem;
            border-radius: 5px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin: 1rem 0;
        }
        .stFormSubmitButton {
        color: white !important;
        }

        /* Table Styles */
        .dataframe {
            border-collapse: collapse;
            margin: 1rem 0;
            font-size: 0.9em;
            border-radius: 5px;
            overflow: hidden;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
        }
        
        .dataframe thead tr {
            background-color: #009879;
            color: black;
            text-align: left;
        }
        
        .dataframe th,
        .dataframe td {
            padding: 12px 15px;
        }
        
        .dataframe tbody tr {
            border-bottom: 1px solid #dddddd;
        }
        
        .dataframe tbody tr:nth-of-type(even) {
            background-color: #f3f3f3;
        }
        
        /* Form Styles */
        .stForm {
            background-color: none;
            padding: 2rem;
            border-radius: 10px;
            color: black;
        }
        
        /* Expander Styles */
        .streamlit-expanderHeader {
            background-color: #f8f9fa;
            border-radius: 5px;
        }
        .stElementContainer {
            color: white !important;
        }
        /* Tabs Style */
        .stTabs [data-baseweb="tab-list"] {
            gap: 24px;
        }
        
        .stTabs [data-baseweb="tab"] {
            height: 50px;
            white-space: pre-wrap;
            border-radius: 5px;
            padding: 10px;
        }
        
        /* Search Box Style */
        .search-box {
            padding: 1rem;
            background-color: white;
            border-radius: 5px;
            margin: 1rem 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        /* Footer Style */
        .footer {
            position: fixed;
            bottom: 0;
            width: 100%;
            background-color: #f8f9fa;
            padding: 1rem;
            text-align: center;
            font-size: 0.8rem;
        }
        </style>
    """,
        unsafe_allow_html=True,
    )


def main():
    load_css()

    st.markdown(
        '<h1 class="main-header">Smart Business Card Scanner</h1>',
        unsafe_allow_html=True,
    )

    # Initialize OCR
    @st.cache_resource
    def load_ocr():
        try:
            return easyocr.Reader(["en"], gpu=True)
        except:
            return easyocr.Reader(["en"], gpu=False)

    scanner = load_ocr()

    # Menu
    menu_choice = option_menu(
        None,
        ["Scan Card", "View & Manage Contacts"],
        icons=["camera", "person-rolodex"],
        default_index=0,
        orientation="horizontal",
        styles={
            "nav-link": {
                "font-size": "1.2rem",
                "text-align": "center",
                "margin": "0.5rem",
                "--hover-color": "#eaf4f4",
            },
            "icon": {"font-size": "1.2rem"},
            "container": {"max-width": "800px"},
            "nav-link-selected": {"background-color": "#83c5be"},
        },
    )

    if menu_choice == "Scan Card":
        st.markdown('<div class="upload-section">', unsafe_allow_html=True)
        uploaded_file = st.file_uploader(
            "Upload Business Card Image",
            type=["png", "jpg", "jpeg"],
            help="Supported formats: PNG, JPG, JPEG",
        )
        st.markdown("</div>", unsafe_allow_html=True)

        if uploaded_file:
            try:
                # Create directory for uploads
                upload_dir = os.path.join(os.getcwd(), "scanned_cards")
                os.makedirs(upload_dir, exist_ok=True)

                # Save and process image
                file_path = os.path.join(upload_dir, uploaded_file.name)
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())

                with st.spinner("Processing image..."):
                    # Process image and show it
                    image = cv2.imread(file_path)
                    detected_text = scanner.readtext(file_path)
                    fig = process_card_image(image, detected_text)
                    st.pyplot(fig)

                text_only = scanner.readtext(file_path, detail=0)
                contact_df = extract_card_info(text_only)

                # Store raw text for display
                raw_text = "\n".join(text_only)

                # Allow manual editing of extracted information
                st.subheader("Review and Edit Information")
                with st.form("edit_info"):
                    edited_info = {}
                    cols = st.columns(2)

                    fields = {
                        "full_name": "Full Name",
                        "job_title": "Job Title",
                        "organization": "Organization",
                        "business_email": "Email",
                        "contact_number": "Phone",
                        "business_url": "Website",
                        "street_address": "Address",
                        "location_city": "City",
                        "location_state": "State",
                        "postal_code": "Postal Code",
                    }

                    for idx, (field, label) in enumerate(fields.items()):
                        with cols[idx % 2]:
                            edited_info[field] = st.text_input(
                                label,
                                value=contact_df.iloc[0][field],
                                key=f"edit_{field}",
                            )

                    submit = st.form_submit_button("Save Contact")

                    if submit:
                        edited_df = pd.DataFrame([edited_info])
                        if save_to_database(edited_df):
                            st.success("Contact saved successfully!")
                            # Clean up uploaded file
                            if os.path.exists(file_path):
                                os.remove(file_path)

                        # Show raw OCR text in an expander
                        with st.expander("View Raw OCR Text", expanded=False):
                            st.text(raw_text)

            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
                if os.path.exists(file_path):
                    os.remove(file_path)

    else:  # View & Manage Contacts section
        st.subheader("View & Manage Contacts")

        # Search functionality
        col1, col2 = st.columns([3, 1])
        with col1:
            search_term = st.text_input("🔍 Search contacts", "")

        contacts_df = get_all_contacts()

        if not contacts_df.empty:
            # Filter contacts based on search
            if search_term:
                mask = contacts_df.apply(
                    lambda x: x.astype(str).str.contains(search_term, case=False).any(),
                    axis=1,
                )
                filtered_df = contacts_df[mask]
            else:
                filtered_df = contacts_df

            st.markdown('<div class="dataframe-container">', unsafe_allow_html=True)
            st.dataframe(
                filtered_df,
                use_container_width=True,
                height=450,
                hide_index=True,
            )
            st.markdown("</div>", unsafe_allow_html=True)
            st.subheader("Contact Management")

            selected_contact = st.selectbox(
                "Select a contact to manage:",
                options=[""] + filtered_df["Name"].tolist(),
                index=0,
            )

            if selected_contact:
                col1, col2 = st.columns(2)

                with col1:
                    if st.button("✏️ Edit Contact", use_container_width=True):
                        st.session_state.show_edit = True
                        st.session_state.show_delete = False

                with col2:
                    if st.button("🗑️ Delete Contact", use_container_width=True):
                        st.session_state.show_delete = True
                        st.session_state.show_edit = False

                # Edit Contact Form
                if getattr(st.session_state, "show_edit", False):
                    st.markdown("### Edit Contact Information")
                    with st.form("edit_contact_form"):
                        contact_data = filtered_df[
                            filtered_df["Name"] == selected_contact
                        ].iloc[0]
                        updated_data = {}
                        cols = st.columns(2)

                        for idx, (column, value) in enumerate(contact_data.items()):
                            if column != "Name":
                                with cols[idx % 2]:
                                    updated_data[column] = st.text_input(
                                        column, value=value, key=f"update_{column}"
                                    )

                        if st.form_submit_button("Update Contact"):
                            if update_contact(selected_contact, updated_data):
                                st.success("Contact updated successfully!")
                                st.session_state.show_edit = False
                                time.sleep(1)
                                st.rerun()

                # Delete Confirmation
                if getattr(st.session_state, "show_delete", False):
                    st.warning(
                        f"⚠️ Are you sure you want to delete {selected_contact}'s contact?"
                    )
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("Yes, Delete", use_container_width=True):
                            if delete_contact(selected_contact):
                                st.success("Contact deleted successfully!")
                                st.session_state.show_delete = False
                                time.sleep(1)
                                st.rerun()
                    with col2:
                        if st.button("No, Cancel", use_container_width=True):
                            st.session_state.show_delete = False
                            st.rerun()

        else:
            st.info("No contacts saved yet. Start by scanning some business cards!")

    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center'>
            <p>Business Card Scanner v1.0</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


# Configuration and Constants
DB_CONFIG = {
    "host": "localhost", 
    "port": "5432",
    "database": "business_cards",
    "user": "postgres",
    "password": "postgres",
}

# Create a connection pool
try:
    connection_pool = psycopg2.pool.SimpleConnectionPool(
        minconn=1, maxconn=10, **DB_CONFIG
    )
except Exception as e:
    st.error(f"Failed to create connection pool: {str(e)}")
    connection_pool = None


@contextmanager
def get_db_connection():
    """Context manager for database connections"""
    conn = connection_pool.getconn() if connection_pool else None
    try:
        if conn:
            yield conn.cursor()
            conn.commit()
        else:
            raise Exception("No database connection available")
    except Exception as e:
        if conn:
            conn.rollback()
        raise e
    finally:
        if conn:
            connection_pool.putconn(conn)


def init_database():
    """Initialize database tables"""
    try:
        with get_db_connection() as cursor:
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS contact_info
                (id SERIAL PRIMARY KEY,
                 full_name TEXT,
                 organization TEXT,
                 job_title TEXT,
                 contact_number VARCHAR(50),
                 business_email TEXT,
                 business_url TEXT,
                 street_address TEXT,
                 location_city TEXT,
                 location_state TEXT,
                 postal_code VARCHAR(10),
                 created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                 last_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP)
            """
            )
    except Exception as e:
        st.error(f"Database initialization failed: {str(e)}")


# Helper functions for text extraction
def extract_email(text: str) -> Optional[str]:
    """Extract email address from text"""
    email_pattern = (
        r"[a-zA-Z0-9._%+-]+[-.]*@[a-zA-Z0-9.-]+[-.]*[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
    )
    email_match = re.search(email_pattern, text)
    if email_match:
        email = email_match.group(0)
        # Clean up and reconstruct the email if needed
        parts = email.split("@")
        if len(parts) == 2:
            username, domain = parts
            # Ensure dots are preserved in domain
            domain = domain.replace(" ", ".")
            return f"{username}@{domain}"
    return None


def extract_phone(text: str) -> Optional[str]:
    """Extract phone number from text"""
    phone_pattern = r"(?:\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}"
    phone_match = re.search(phone_pattern, text)
    if phone_match:
        phone = phone_match.group(0)
        return re.sub(r"[^\d+]", "", phone)
    return None


def extract_website(text: str) -> Optional[str]:
    """Extract website from text"""
    if "@" in text:  # Skip email addresses
        return None
    website_pattern = (
        r"(?:www\.)?[a-zA-Z0-9][a-zA-Z0-9-]+\.[a-zA-Z]{2,}(?:\.[a-zA-Z]{2,})?"
    )
    website_match = re.search(website_pattern, text.lower())
    if website_match:
        website = website_match.group(0)
        return f"www.{website}" if not website.startswith("www.") else website
    return None


def extract_address(text: str) -> Optional[str]:
    """Extract street address from text"""
    address_pattern = r"\d+\s+[A-Za-z\s,]+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Lane|Ln|Drive|Dr)\b"
    address_match = re.search(address_pattern, text)
    return address_match.group(0) if address_match else None


def process_card_image(image: np.ndarray, text_boxes: list) -> plt.Figure:
    """Process and display card image with detected text boxes"""
    fig = plt.figure(figsize=(15, 15))
    ax = fig.add_subplot(111)

    for coords, text, prob in text_boxes:
        top_left = tuple(map(int, coords[0]))
        bottom_right = tuple(map(int, coords[2]))
        cv2.rectangle(image, top_left, bottom_right, (0, 255, 0), 2)

    ax.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    ax.axis("off")
    return fig


def extract_card_info(ocr_result: list) -> pd.DataFrame:
    """Extract information from OCR result"""
    info = {
        "full_name": "",
        "organization": "",
        "job_title": "",
        "contact_number": "",
        "business_email": "",
        "business_url": "",
        "street_address": "",
        "location_city": "",
        "location_state": "",
        "postal_code": "",
        "raw_text": "\n".join(ocr_result),
    }

    for idx, text in enumerate(ocr_result):
        text = text.strip()
        if not text:
            continue

        # Extract information using helper functions
        email = extract_email(text)
        if email:
            info["business_email"] = email
            continue

        phone = extract_phone(text)
        if phone:
            info["contact_number"] = phone
            continue

        website = extract_website(text)
        if website:
            info["business_url"] = website
            continue

        address = extract_address(text)
        if address:
            info["street_address"] = address
            continue

        # Handle name and title
        if idx == 0 and not any(char.isdigit() for char in text):
            info["full_name"] = text
        elif idx == 1 and not any(
            domain in text.lower() for domain in [".com", ".org", ".net"]
        ):
            info["job_title"] = text

    return pd.DataFrame([info])


def save_to_database(df: pd.DataFrame) -> bool:
    """Save contact information to database"""
    try:
        with get_db_connection() as cursor:
            insert_query = """
                INSERT INTO contact_info 
                (full_name, organization, job_title, contact_number, business_email, 
                 business_url, street_address, location_city, location_state, postal_code)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            # Extract only the needed columns in the correct order
            values = (
                df.iloc[0]["full_name"],
                df.iloc[0]["organization"],
                df.iloc[0]["job_title"],
                df.iloc[0]["contact_number"],
                df.iloc[0]["business_email"],
                df.iloc[0]["business_url"],
                df.iloc[0]["street_address"],
                df.iloc[0]["location_city"],
                df.iloc[0]["location_state"],
                df.iloc[0]["postal_code"],
            )

            # Log the values for debugging
            print("Inserting values:", values)

            cursor.execute(insert_query, values)
        return True
    except Exception as e:
        st.error(f"Failed to save to database: {str(e)}")
        print(f"Database error details: {str(e)}")  # Detailed error logging
        return False


def get_all_contacts() -> pd.DataFrame:
    """Retrieve all contacts from database"""
    try:
        with get_db_connection() as cursor:
            cursor.execute(
                """
                SELECT full_name, organization, job_title, contact_number, 
                       business_email, business_url, street_address, location_city, 
                       location_state, postal_code
                FROM contact_info 
                ORDER BY created_at DESC
            """
            )
            records = cursor.fetchall()
            columns = [
                "Name",
                "Organization",
                "Title",
                "Phone",
                "Email",
                "Website",
                "Address",
                "City",
                "State",
                "Postal Code",
            ]
            return pd.DataFrame(records, columns=columns)
    except Exception as e:
        st.error(f"Failed to fetch contacts: {str(e)}")
        return pd.DataFrame()


def update_contact(name: str, updated_data: Dict[str, Any]) -> bool:
    """Update contact information"""
    try:
        with get_db_connection() as cursor:
            update_query = """
                UPDATE contact_info 
                SET organization = %s,
                    job_title = %s,
                    contact_number = %s,
                    business_email = %s,
                    business_url = %s,
                    street_address = %s,
                    location_city = %s,
                    location_state = %s,
                    postal_code = %s,
                    last_modified = CURRENT_TIMESTAMP
                WHERE full_name = %s
            """
            values = (
                updated_data["Organization"],
                updated_data["Title"],
                updated_data["Phone"],
                updated_data["Email"],
                updated_data["Website"],
                updated_data["Address"],
                updated_data["City"],
                updated_data["State"],
                updated_data["Postal Code"],
                name,
            )
            cursor.execute(update_query, values)
        return True
    except Exception as e:
        st.error(f"Failed to update contact: {str(e)}")
        return False


def delete_contact(name: str) -> bool:
    """Delete contact from database"""
    try:
        with get_db_connection() as cursor:
            delete_query = "DELETE FROM contact_info WHERE full_name = %s"
            cursor.execute(delete_query, (name,))
        return True
    except Exception as e:
        st.error(f"Failed to delete contact: {str(e)}")
        return False


# Initialize database
init_database()

if __name__ == "__main__":
    main()