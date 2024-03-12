import streamlit as st
import pandas as pd

# Initialize or load existing patient data
if 'patients' not in st.session_state:
    st.session_state.patients = pd.DataFrame([
        {"id": 1, "name": "John Doe", "age": 30, "condition": "HIV", "gender": "Male", "ethnicity": "Asian", "records": pd.DataFrame(columns=['Viral Load', 'CD4 Count', 'Treatment Used'])},
        {"id": 2, "name": "Hannah", "age": 25, "condition": "HIV", "gender": "Female", "ethnicity": "Caucasian", "records": pd.DataFrame(columns=['Viral Load', 'CD4 Count', 'Treatment Used'])},
    ])

def recommend_treatment(viral_load):
    return "FTC+TDF, DTG, EFV, extra pk-En" if viral_load > 7000 else "FTC+TAF, DTG, RPV, ATV, extra pk-En"

def add_patient():
    with st.container():
        st.title("Add New Patient")
        with st.form(key='add_patient_form'):
            new_name = st.text_input("Name", key="new_name")
            new_age = st.number_input("Age", min_value=0, max_value=120, key="new_age")
            new_gender = st.text_input("Gender", key="new_gender")
            new_ethnicity = st.text_input("Ethnicity", key="new_ethnicity")
            new_condition = st.text_input("Condition", key="new_condition")
            submit_button = st.form_submit_button("Submit")

        if submit_button:
            new_id = max(st.session_state.patients['id']) + 1
            new_patient = pd.DataFrame([{"id": new_id, "name": new_name, "age": new_age, "gender": new_gender, "ethnicity": new_ethnicity, "condition": new_condition, 
                                         "records": pd.DataFrame(columns=['Viral Load', 'CD4 Count', 'Treatment Used'])}])
            st.session_state.patients = pd.concat([st.session_state.patients, new_patient], ignore_index=True)
            st.success(f"Patient {new_name} added successfully.")
            st.session_state['current_page'] = 'main'
            st.experimental_rerun()

def main_dashboard():
    st.title("Doctor's Dashboard")
    with st.container():
        # Use columns to centralize the patient list
        left, center, right = st.columns([1, 6, 1])
        with center:
            # st.write("## Patient List")
            st.write('')

            # Converting the patient table to HTML and removing the index
            patient_table = st.session_state.patients[['id', 'name', 'age', 'gender', 'ethnicity', 'condition']]
            patient_html = patient_table.to_html(index=False)
            st.markdown(patient_html, unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)  # Adding space between elements

            with st.container():
                # Centralize the select box and buttons using columns
                selected_patient = st.selectbox('Select a patient to view their chart:', st.session_state.patients['name'], key="patient_select")
                view_chart_button, add_patient_button = st.columns(2)
                with view_chart_button:
                    if st.button('View Selected Patient Chart'):
                        st.session_state['current_page'] = 'patient_chart'
                        st.session_state['selected_patient_name'] = selected_patient
                with add_patient_button:
                    if st.button("Add New Patient"):
                        st.session_state['current_page'] = 'add_patient'

def patient_chart():
    patient = st.session_state.patients.loc[st.session_state.patients['name'] == st.session_state['selected_patient_name']].iloc[0]
    st.title(f"{patient['name']}")
    st.write(f"Age: {patient['age']}, Gender: {patient['gender']}, Ethnicity: {patient['ethnicity']}")
    st.write(f"Condition: {patient['condition']}")

    if not patient['records'].empty:
        formatted_records = patient['records'].copy()
        formatted_records['Viral Load'] = formatted_records['Viral Load'].astype(int).astype(str)  # Convert to string to prevent scientific notation
        formatted_records['CD4 Count'] = formatted_records['CD4 Count'].astype(int).astype(str)
        # Convert records DataFrame to HTML for display
        records_html = formatted_records.to_html(index=False)
        st.markdown(records_html, unsafe_allow_html=True)
    else:
        st.write("No records available.")
    
    st.write("")

    if st.button("Add Record"):
        st.session_state['current_page'] = 'add_record'
        st.experimental_rerun()
    if st.button("Back to Dashboard"):
        st.session_state['current_page'] = 'main'
        st.experimental_rerun()

def add_record_page():
    st.title("Add a New Patient Record")
    viral_load = st.number_input("Viral Load", min_value=0)
    cd4_count = st.number_input("CD4 Count", min_value=0)
    submit_button_pressed = st.button("Submit")

    if submit_button_pressed:
        # Perform treatment recommendation and record addition logic
        treatment = recommend_treatment(viral_load)
        patient_idx = st.session_state.patients.index[st.session_state.patients['name'] == st.session_state['selected_patient_name']].tolist()[0]
        new_record = pd.DataFrame([[viral_load, cd4_count, treatment]], columns=['Viral Load', 'CD4 Count', 'Treatment Used'])
        st.session_state.patients.at[patient_idx, 'records'] = pd.concat([st.session_state.patients.at[patient_idx, 'records'], new_record], ignore_index=True)

        treatment_recommendations(viral_load, cd4_count)  # Assuming this function displays recommendations and updates records

    if 'show_recommendations' in st.session_state and st.session_state['show_recommendations']:
        # Display treatment recommendations directly without waiting for another button press
        display_treatment_recommendations(viral_load)

        # Button to acknowledge recommendations
        if st.button("Acknowledge Recommendations"):
            # Ensure no other state changes that could redirect elsewhere are triggered between these lines
            st.session_state['current_page'] = 'patient_chart'
            st.session_state['show_recommendations'] = False  # Reset this flag
            st.experimental_rerun()

# Example function that handles displaying treatment recommendations and updating patient records
def treatment_recommendations(vl, cd4):
    # Logic to add record and determine treatment recommendations
    st.session_state['show_recommendations'] = True

def display_treatment_recommendations(viral_load):
    # Actual treatment recommendation display logic
    st.write("### Treatment Recommendations")
    if viral_load > 7000:
        st.success("""
        - Base Drug Combo: FTC + TDF
        - Complementary INI: DTG
        - Complementary NNRTI: EFV
        - Extra PI: Not Applied
        - Extra pk-En: True
        """)
    elif viral_load < 7000:
        st.success("""
        - Base Drug Combo: FTC + TAF
        - Complementary INI: DTG
        - Complementary NNRTI: RPV
        - Extra PI: ATV
        - Extra pk-En: True
        """)


# Initialize session state for page navigation
if 'current_page' not in st.session_state:
    st.session_state['current_page'] = 'main'
if 'selected_patient_name' not in st.session_state:
    st.session_state['selected_patient_name'] = None

# Page routing
if st.session_state['current_page'] == 'main':
    main_dashboard()
elif st.session_state['current_page'] == 'patient_chart':
    patient_chart()
elif st.session_state['current_page'] == 'add_record':
    add_record_page()
elif st.session_state['current_page'] == 'add_patient':
    st.title("Add New Patient")
    add_patient()
