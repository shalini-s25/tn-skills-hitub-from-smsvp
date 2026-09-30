import os
import html
from datetime import date

import requests
import streamlit as st

from dotenv import load_dotenv

from utils.exporters import (
    format_docx,
    format_pdf,
    safe_filename,
)

from utils.sanitize import sanitize_text


# =========================================================
# Environment
# =========================================================

load_dotenv()


BACKEND_URL = os.getenv(
    "BACKEND_URL",
    "http://127.0.0.1:8000",
).rstrip("/")


# =========================================================
# Page Configuration
# =========================================================

st.set_page_config(
    page_title="LegalEase",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =========================================================
# CSS
# =========================================================

st.markdown(
    """
    <style>

    .main-title {
        text-align: center;
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.2rem;
    }

    .subtitle {
        text-align: center;
        color: #6b7280;
        margin-bottom: 1.5rem;
    }

    .document-card {
        background: #111827;
        color: #f9fafb;
        border-radius: 12px;
        padding: 30px;
        max-height: 650px;
        overflow-y: auto;
        border: 1px solid #374151;
    }

    .document-content {
        font-family: Georgia, "Times New Roman", serif;
        line-height: 1.75;
        font-size: 1rem;
    }

    .warning {
        padding: 12px;
        border-radius: 8px;
        background: #fff7ed;
        border: 1px solid #fed7aa;
        color: #7c2d12;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# Header
# =========================================================

st.markdown(
    '<div class="main-title">⚖️ LegalEase</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="subtitle">'
    'AI-Powered Legal Document Generator'
    '</div>',
    unsafe_allow_html=True,
)


# =========================================================
# Legal Notice
# =========================================================

st.markdown(
    '<div class="warning">'
    'AI-generated legal drafts are for informational purposes. '
    'Review the final document with a qualified legal professional '
    'before signing or relying on it.'
    '</div>',
    unsafe_allow_html=True,
)

st.write("")


# =========================================================
# Session State
# =========================================================

if "document" not in st.session_state:

    st.session_state.document = ""


if "generated_type" not in st.session_state:

    st.session_state.generated_type = "Legal Document"


# =========================================================
# Sidebar
# =========================================================

with st.sidebar:

    st.header(
        "Document Details"
    )


    # -----------------------------------------------------
    # Document Type
    # -----------------------------------------------------

    document_type = st.text_input(
        "Document Type",
        placeholder=(
            "e.g. Non-Disclosure Agreement"
        ),
    )


    # -----------------------------------------------------
    # Parties
    # -----------------------------------------------------

    parties = st.text_area(
        "Parties Involved",
        placeholder=(
            "Jane Doe (Service Provider), "
            "TechNova Inc. (Client)"
        ),
        height=110,
    )


    # -----------------------------------------------------
    # Terms
    # -----------------------------------------------------

    terms = st.text_area(
        "Terms & Conditions",
        placeholder=(
            "Payment within 30 days; "
            "Confidentiality must be maintained; "
            "Either party may terminate with 15 days notice"
        ),
        height=170,
        help=(
            "Separate multiple terms with semicolons."
        ),
    )


    # -----------------------------------------------------
    # Date
    # -----------------------------------------------------

    effective_date = st.text_input(
        "Effective Date",
        value=date.today().strftime(
            "%B %d, %Y"
        ),
    )


    # -----------------------------------------------------
    # Generate Button
    # -----------------------------------------------------

    generate = st.button(
        "✨ Generate Document",
        type="primary",
        use_container_width=True,
    )


# =========================================================
# Generate
# =========================================================

if generate:

    missing = []


    if not document_type.strip():

        missing.append(
            "Document Type"
        )


    if not parties.strip():

        missing.append(
            "Parties Involved"
        )


    if not terms.strip():

        missing.append(
            "Terms & Conditions"
        )


    if not effective_date.strip():

        missing.append(
            "Effective Date"
        )


    if missing:

        st.error(
            "Please complete: "
            + ", ".join(missing)
        )

    else:

        payload = {

            "document_type":
                document_type.strip(),

            "parties":
                parties.strip(),

            "terms":
                terms.strip(),

            "dates":
                effective_date.strip(),
        }


        with st.spinner(
            "Generating your legal draft with Gemini..."
        ):

            try:

                response = requests.post(

                    f"{BACKEND_URL}/generate",

                    json=payload,

                    timeout=120,
                )


                if response.ok:

                    data = response.json()


                    st.session_state.document = (
                        sanitize_text(
                            data["content"]
                        )
                    )


                    st.session_state.generated_type = (
                        data["document_type"]
                    )


                    st.success(
                        "Document generated successfully."
                    )


                else:

                    try:

                        detail = response.json().get(
                            "detail",
                            response.text,
                        )

                    except Exception:

                        detail = response.text


                    st.error(
                        f"Backend error: {detail}"
                    )


            except requests.RequestException as exc:

                st.error(
                    "Could not connect to the FastAPI backend.\n\n"
                    "Make sure the backend is running with:\n\n"
                    "uvicorn backend.main:app --reload\n\n"
                    f"Details: {exc}"
                )


# =========================================================
# Display Generated Document
# =========================================================

if st.session_state.document:

    st.subheader(
        "Document Preview"
    )


    escaped_document = html.escape(
        st.session_state.document
    ).replace(
        "\n",
        "<br>",
    )


    st.markdown(
        f"""
        <div class="document-card">
            <div class="document-content">
                {escaped_document}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


    st.write("")


    # =====================================================
    # Editing
    # =====================================================

    st.subheader(
        "Edit Document"
    )


    edited_document = st.text_area(

        "Modify the generated document "
        "before exporting.",

        value=st.session_state.document,

        height=500,

        label_visibility="collapsed",
    )


    st.session_state.document = (
        edited_document
    )


    current_text = (
        st.session_state.document
    )


    base_name = safe_filename(
        st.session_state.generated_type
    )


    # =====================================================
    # Downloads
    # =====================================================

    col1, col2, col3 = st.columns(3)


    # -----------------------------------------------------
    # TXT
    # -----------------------------------------------------

    with col1:

        st.download_button(

            "⬇️ Download TXT",

            data=current_text.encode(
                "utf-8"
            ),

            file_name=f"{base_name}.txt",

            mime="text/plain",

            use_container_width=True,
        )


    # -----------------------------------------------------
    # DOCX
    # -----------------------------------------------------

    with col2:

        docx_bytes = format_docx(

            current_text,

            st.session_state.generated_type,

            terms=terms,
        )


        st.download_button(

            "⬇️ Download DOCX",

            data=docx_bytes,

            file_name=f"{base_name}.docx",

            mime=(
                "application/vnd.openxmlformats-officedocument."
                "wordprocessingml.document"
            ),

            use_container_width=True,
        )


    # -----------------------------------------------------
    # PDF
    # -----------------------------------------------------

    with col3:

        try:

            pdf_bytes = format_pdf(

                current_text,

                st.session_state.generated_type,
            )


            st.download_button(

                "⬇️ Download PDF",

                data=pdf_bytes,

                file_name=f"{base_name}.pdf",

                mime="application/pdf",

                use_container_width=True,
            )


        except Exception as exc:

            st.error(
                f"PDF export failed: {exc}"
            )


else:

    st.info(
        "Enter the document details in the sidebar "
        "and click **Generate Document** to create "
        "your first draft."
    )


# =========================================================
# Footer
# =========================================================

st.divider()

st.caption(
    "LegalEase • FastAPI + Streamlit + Google Gemini • "
    "AI-generated documents require human legal review."
)