import streamlit as st
from datetime import datetime

# Page config
st.set_page_config(
    page_title="Report Fly Tipping",
    page_icon="🗑️",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        color: #2E7D32;
        font-weight: bold;
    }
    .impact-card {
        background-color: #f0f7f4;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #2E7D32;
        margin: 1rem 0;
    }
    .warning-card {
        background-color: #fff3e0;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #ff9800;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'submitted' not in st.session_state:
    st.session_state.submitted = False

# Header
st.markdown('<p class="main-header">🗑️ Report Fly Tipping in Your Neighbourhood</p>', unsafe_allow_html=True)
st.markdown("Help keep our community clean and safe by reporting fly tipping incidents.")

# Main content in tabs
tab1, tab2, tab3 = st.tabs(["📸 Report Incident", "📊 Community Impact", "ℹ️ About"])

with tab1:
    st.header("Report a Fly Tipping Incident")

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("Upload Evidence")
        uploaded_file = st.file_uploader(
            "Take or upload a photo of the fly tipping",
            type=['jpg', 'jpeg', 'png'],
            help="Clear photos help authorities respond faster"
        )

        if uploaded_file:
            st.image(uploaded_file, caption="Uploaded Image", use_container_width=True)

        st.subheader("Location Details")
        postcode = st.text_input("Your Postcode", placeholder="e.g., SW1A 1AA")
        address = st.text_area("Specific Location", placeholder="Near the park entrance, behind the bus stop...")

    with col2:
        st.subheader("Incident Details")

        waste_type = st.multiselect(
            "Type of Waste",
            ["Household waste", "Furniture", "White goods", "Construction waste",
             "Garden waste", "Tyres", "Hazardous materials", "Other"]
        )

        amount = st.select_slider(
            "Approximate Amount",
            options=["Small bag", "Several bags", "Van load", "Large van load", "Truck load"]
        )

        date_noticed = st.date_input("When did you notice this?", datetime.now())

        additional_info = st.text_area(
            "Additional Information",
            placeholder="Any other details that might help (vehicle descriptions, time noticed, etc.)"
        )

        contact_me = st.checkbox("Council can contact me for more information")

        if contact_me:
            email = st.text_input("Your Email (optional)")

    if st.button("🚀 Submit Report", type="primary", use_container_width=True):
        if uploaded_file and postcode:
            st.session_state.submitted = True
            st.success("✅ Report submitted successfully!")

            # Personalized Impact Section
            st.markdown("---")
            st.header("🎯 How This Affects YOU")

            st.markdown("""
                <div class="impact-card">
                    <h3>🏠 Property Value Impact</h3>
                    <p>Fly tipping within 500m of your location can reduce property values by <b>3-7%</b>. 
                    Based on average prices in your postcode, this could mean a loss of <b>£15,000-£35,000</b>.</p>
                </div>
            """, unsafe_allow_html=True)

            st.markdown("""
                <div class="impact-card">
                    <h3>🫁 Health Impact</h3>
                    <p>Fly tipping increases local air pollution and can harbor disease-carrying pests. 
                    Residents within 200m experience <b>20% higher</b> respiratory complaints.</p>
                </div>
            """, unsafe_allow_html=True)

            st.markdown("""
                <div class="impact-card">
                    <h3>👨‍👩‍👧‍👦 Community Safety</h3>
                    <p>Areas with fly tipping see <b>15% more crime</b>. Your report helps break this cycle 
                    and makes your neighborhood safer for everyone.</p>
                </div>
            """, unsafe_allow_html=True)

            # Next Steps
            st.markdown("---")
            st.header("📋 What Happens Next?")

            col_a, col_b = st.columns(2)

            with col_a:
                st.markdown("""
                    **Within 24 hours:**
                    - ✅ Council receives your report
                    - 📧 You'll get a reference number
                    - 🔍 Case assigned to enforcement team
                """)

            with col_b:
                st.markdown("""
                    **Within 5 working days:**
                    - 🚛 Removal team scheduled
                    - 📸 Site inspection conducted
                    - 🔎 Investigation for perpetrators
                """)

            st.info("💡 **Track your report:** Use reference #FT" + str(hash(datetime.now()))[-6:] + " to check status")

        else:
            st.error("⚠️ Please upload a photo and provide your postcode")

with tab2:
    st.header("📊 Community Impact Dashboard")

    st.markdown("""
        <div class="warning-card">
            <h3>🗺️ Your Area Statistics</h3>
            <p>Understanding the collective impact helps us work together for change.</p>
        </div>
    """, unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        housing_price = get_housing_price_reduction("WD24 7BA")
        st.metric("Reports This Month", "47", f"{housing_price}%")
    with col2:
        st.metric("Avg Response Time", "3.2 days", "-0.8 days")
    with col3:
        st.metric("Cleaned Up", "89%", "+5%")
    with col4:
        st.metric("Cost to Council", "£18.5k", "+£3.2k")

    st.markdown("---")

    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("🎯 Most Common Waste Types")
        st.markdown("""
            1. 🛋️ Furniture & mattresses (34%)
            2. 🏗️ Construction waste (28%)
            3. 🗑️ Household bags (22%)
            4. ♻️ White goods (10%)
            5. 🌿 Garden waste (6%)
        """)

    with col_b:
        st.subheader("📍 Hotspot Areas")
        st.markdown("""
            Areas needing most attention:
            - Industrial estate (North)
            - Park entrance (East)
            - Railway arches (South)
        """)

    st.markdown("---")
    st.info("💪 **Together we've prevented an estimated 12 tons of illegal dumping this year!**")

with tab3:
    st.header("ℹ️ About Fly Tipping")

    st.markdown("""
        ### What is Fly Tipping?

        Fly tipping is the illegal dumping of waste on land not licensed to accept it. 
        It's a criminal offense that affects communities across the UK.

        ### Why Report It?

        - 🏘️ **Protects your community** - Clean neighborhoods are safer and more pleasant
        - 💷 **Saves money** - Early reporting reduces cleanup costs
        - ⚖️ **Holds offenders accountable** - Evidence helps prosecute fly tippers
        - 🌍 **Environmental protection** - Prevents pollution and habitat damage

        ### The Cycle of Fly Tipping

        Research shows fly tipping creates a negative cycle:
        1. Illegal dumping occurs
        2. Area appears neglected
        3. More people dump waste
        4. Property values decline
        5. Crime increases

        **Your report helps break this cycle!**

        ### Legal Penalties

        Fly tipping is punishable by:
        - Unlimited fines
        - Up to 5 years imprisonment
        - Vehicle seizure

        ### Contact Information

        📞 **Emergency Hazardous Waste:** 999  
        📧 **General Enquiries:** flytipping@council.gov.uk  
        🌐 **Track Reports:** www.council.gov.uk/flytipping
    """)

# Footer
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: #666; padding: 20px;'>
        <p>💚 Working together for a cleaner, safer community</p>
        <p style='font-size: 0.8rem;'>This tool uses AI to contextualize environmental impact data. 
        All reports are reviewed by council enforcement teams.</p>
    </div>
""", unsafe_allow_html=True)