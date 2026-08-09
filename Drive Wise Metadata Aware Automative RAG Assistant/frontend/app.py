import streamlit as st

from api_client import ask_question


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Drive Wise",
    page_icon="🚗",
    layout="wide"
)


# ============================================================
# VEHICLE DATA
# ============================================================

VEHICLES = {

    "Hyundai": [
        "Creta",
        "Exter",
        "Venue",
        "Verna"
    ],

    "Kia": [
        "Carens",
        "Seltos",
        "Sonet",
        "Syros"
    ],

    "Mahindra": [
        "Scorpio N",
        "Thar",
        "XUV 3XO",
        "XUV700"
    ],

    "Maruti": [
        "Baleno",
        "Brezza",
        "Fronx",
        "Swift"
    ],

    "Tata": [
        "Altroz",
        "Curvv",
        "Nexon",
        "Punch"
    ]
}


# ============================================================
# BRAND / MODEL NORMALIZATION
# ============================================================

BRAND_MAPPING = {
    "Hyundai": "hyundai",
    "Kia": "kia",
    "Mahindra": "mahindra",
    "Maruti": "maruti",
    "Tata": "tata"
}


MODEL_MAPPING = {

    "Creta": "creta",
    "Exter": "exter",
    "Venue": "venue",
    "Verna": "verna",

    "Carens": "carens",
    "Seltos": "seltos",
    "Sonet": "sonet",
    "Syros": "syros",

    "Scorpio N": "scorpio_n",
    "Thar": "thar",
    "XUV 3XO": "xuv3xo",
    "XUV700": "xuv700",

    "Baleno": "baleno",
    "Brezza": "brezza",
    "Fronx": "fronx",
    "Swift": "swift",

    "Altroz": "altroz",
    "Curvv": "curvv",
    "Nexon": "nexon",
    "Punch": "punch"
}


# ============================================================
# HEADER
# ============================================================

st.title("🚗 Drive Wise")

st.markdown(
    """
    ### Metadata-Aware Automotive RAG Assistant

    Ask questions about vehicle specifications, features,
    performance, safety, dimensions and more using the
    official brochure information.
    """
)

st.divider()


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.header("Vehicle Selection")

    brand_display = st.selectbox(
        "Select Brand",
        list(VEHICLES.keys())
    )

    model_display = st.selectbox(
        "Select Model",
        VEHICLES[brand_display]
    )

    brand = BRAND_MAPPING[
        brand_display
    ]

    model = MODEL_MAPPING[
        model_display
    ]

    st.divider()

    st.markdown(
        f"""
        **Selected Vehicle**

        Brand: `{brand_display}`

        Model: `{model_display}`
        """
    )


# ============================================================
# QUESTION INPUT
# ============================================================

st.subheader(
    f"Ask about {brand_display} {model_display}"
)

question = st.text_area(
    "Your Question",
    placeholder=(
        "Example: What is the maximum power?"
    ),
    height=120
)


# ============================================================
# ASK BUTTON
# ============================================================

ask_button = st.button(
    "🔍 Ask Question",
    type="primary",
    use_container_width=True
)


# ============================================================
# ASK QUESTION
# ============================================================

if ask_button:

    if not question.strip():

        st.warning(
            "Please enter a question."
        )

    else:

        with st.spinner(
            "Searching brochure and generating answer..."
        ):

            result = ask_question(
                brand=brand,
                model=model,
                question=question
            )


        # ====================================================
        # SUCCESS
        # ====================================================

        if result.get("success"):

            st.divider()

            st.subheader("Answer")

            st.markdown(
                result.get(
                    "answer",
                    "No answer returned."
                )
            )


            # =================================================
            # SOURCES
            # =================================================

            sources = result.get(
                "sources",
                []
            )

            if sources:

                st.divider()

                st.subheader(
                    "📚 Sources"
                )

                for source in sources:

                    with st.expander(
                        f"Source {source.get('source', '')} — "
                        f"Page {source.get('page', '')}"
                    ):

                        col1, col2 = st.columns(2)

                        with col1:

                            st.write(
                                f"**Brand:** "
                                f"{source.get('brand', '')}"
                            )

                            st.write(
                                f"**Model:** "
                                f"{source.get('model', '')}"
                            )

                        with col2:

                            st.write(
                                f"**Section:** "
                                f"{source.get('section', '')}"
                            )

                            st.write(
                                f"**Page:** "
                                f"{source.get('page', '')}"
                            )

                        st.write(
                            f"**Brochure:** "
                            f"{source.get('brochure', '')}"
                        )


        # ====================================================
        # ERROR
        # ====================================================

        else:

            st.error(
                result.get(
                    "error",
                    "Something went wrong."
                )
            )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "Drive Wise — Metadata-Aware Automotive RAG Assistant"
)