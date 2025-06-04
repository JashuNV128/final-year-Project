import streamlit as st
import pandas as pd
import sqlite3
import hashlib
import plotly.express as px


df = pd.read_csv('drug_effectiveness_realistic_null_weight_data.csv')
conn=sqlite3.connect('drug_effectiveness_realistic_null_weight_data.db')
df.to_sql("drug_effectiveness_realistic_null_weight_data", conn, if_exists="replace", index=False)
cursor=conn.cursor()

# Load Data

# Data Cleaning (Handle Nulls)
df = df.dropna()

# Navbar and Page Selection
page = st.sidebar.radio("Navigation", ["Home", "Symptoms","Precautions"])

if page == "Home":
    # Main Page
    st.title('Drug Effectiveness Analysis Dashboard')

    # Sidebar Filters
    st.sidebar.header('Filters')
    age_filter = st.sidebar.slider('Age Range', min(df['Age']), max(df['Age']), (min(df['Age']), max(df['Age'])))
    gender_filter = st.sidebar.selectbox('Gender', df['Gender'].unique())
    condition_filter = st.sidebar.selectbox('Condition', df['Condition'].unique()) #Single select
    # Apply Filters
    filtered_df = df[
        (df['Age'] >= age_filter[0]) & (df['Age'] <= age_filter[1]) &
        (df['Gender']==gender_filter if gender_filter else True) &
        (df['Condition'] == condition_filter if condition_filter else True)
    ]

    # Calculate Average Recovery Rate by Drug
    drug_recovery = filtered_df.groupby('Drug')['Recovery Rate'].mean().reset_index()

    # Find the Most Effective Drug(s)
    if not drug_recovery.empty:
        max_recovery = drug_recovery['Recovery Rate'].max()
        effective_drugs = drug_recovery[drug_recovery['Recovery Rate'] == max_recovery]['Drug'].tolist()
        st.write(f"The most effective drug(s) for the selected conditions are: {', '.join(effective_drugs)}")
    else:
        st.write("No data available for the selected filters.")
    #Filtered patient data
    query=f"""
    SELECT PatientID,Drug,Age,Gender,Condition,[Blood Type]
    FROM drug_effectiveness_realistic_null_weight_data 
    WHERE Age BETWEEN ? AND ?
    AND Gender=?
    AND Condition=?
    AND PatientID IS NOT NULL
    AND Drug IS NOT NULL
    AND Age IS NOT NULL
    AND Gender IS NOT NULL
    AND Condition IS NOT NULL
    AND [Dosage (mg)] IS NOT NULL
    AND [Treatment Duration (days)] IS NOT NULL
    AND [Recovery Rate] IS NOT NULL
    AND [Side Effects] IS NOT NULL
    AND [Weight (kg)] IS NOT NULL
    AND [Blood Type] IS NOT NULL
    """
    #Get Data
    df=pd.read_sql_query(query,conn,params=(age_filter[0],age_filter[1],gender_filter,condition_filter))
    #Display
    st.subheader("Filtered Patient Data")
    st.dataframe(df)
    conn.close()
    # Summary Statistics
    st.header('Summary Statistics')
    col1, col2, col3, col4 = st.columns(4)
    if not filtered_df.empty:
        col1.metric("Average Recovery Rate", f"{filtered_df['Recovery Rate'].mean():.2f}")
        col2.metric("Average Treatment Duration", f"{filtered_df['Treatment Duration (days)'].mean():.1f} Days")
        col3.metric("Average Dosage", f"{filtered_df['Dosage (mg)'].mean():.1f} mg")
        col4.metric("Total Patients", f"{len(filtered_df)}")
    else:
        st.write("No data to show summary statistics.")

    # Visualizations
    st.header('Visualizations')

    # Recovery Rate by Drug
    if not drug_recovery.empty:
        fig_recovery = px.bar(drug_recovery, x='Drug', y='Recovery Rate', title='Average Recovery Rate by Drug')
        st.plotly_chart(fig_recovery)
    else:
        st.write("No data to show recovery rate graph.")

    # Side Effect Distribution
    if not filtered_df.empty:
        fig_side_effects = px.pie(filtered_df['Side Effects'].value_counts().reset_index(), names='Side Effects', values='count', title='Side Effect Distribution')
        st.plotly_chart(fig_side_effects)
    else:
        st.write("No data to show side effect graph.")

    # Age vs. Recovery Rate
    if not filtered_df.empty:
        fig_age_recovery = px.scatter(filtered_df, x='Age', y='Recovery Rate', color='Drug', title='Age vs. Recovery Rate')
        st.plotly_chart(fig_age_recovery)
    else:
        st.write("No data to show Age vs Recovery graph.")
    #------------------------------------------------------
    df = pd.read_csv('credential_database.csv')  # Make sure this file exists
    conn = sqlite3.connect('credential_database.db')
    df.to_sql("credential_database", conn, if_exists="replace", index=False)
    conn.commit()
    

    # --- Initialize Session State ---
    if 'show_login' not in st.session_state:
        st.session_state.show_login = False
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False

    # --- UI: Start Download Flow ---
    st.subheader("Download Filtered Data")

    if st.button("Download Filtered Data"):
        st.session_state.show_login = True

    # --- UI: Login Form ---
    if st.session_state.show_login and not st.session_state.authenticated:
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Submit"):
            if username == "" or password == "":
                st.warning("Please enter credentials and press submit.")
            else:
                # --- Connect to the SQLite DB ---
                conn = sqlite3.connect('credential_database.db')
                cursor = conn.cursor()

                # --- SQL Query to Validate Credentials ---
                query = "SELECT * FROM credential_database WHERE username=? AND password=?"
                cursor.execute(query, (username, password))
                user = cursor.fetchone()
                conn.close()

                if user:
                    st.success("Login successful.")
                    st.session_state.authenticated = True
                else:
                    st.error("Invalid credentials. Please try again.")

    # --- UI: Download Button After Login ---
    if st.session_state.authenticated:
        st.download_button(
            label="Download CSV",
            data=filtered_df.to_csv(index=False).encode('utf-8'),
            file_name='filtered_data.csv',
            mime='text/csv',
        )
#------------------------------------------------------------------------------------------             
elif page == "Precautions":
    # Precautions Page
    st.title('Drug Effectiveness Analysis Dashboard')
    st.title('Precautions for Condition')

    # Condition Selection for Precautions Page
    condition_filter_precautions = st.selectbox('Select Condition', df['Condition'].unique()) #Single select

    if condition_filter_precautions:
        condition = condition_filter_precautions
        if condition == 'Hypertension':
            st.image("hypertension.png", caption="Hypertension Precautions", use_container_width=True)
            st.write("Precautions for Hypertension:")
            st.markdown("""
                        •	Eat a healthy diet. Choose healthy meal and snack options to help you avoid high blood pressure and its complications.<br>
                        •	Keep yourself at a healthy weight.<br>
                        •	Be physically active.<br>
                        •	Do not smoke.<br>
                        •	Limit how much alcohol you drink.<br> 
                        •	Get enough sleep.<br> 
                        •	Manage stress.""",unsafe_allow_html=True)
                        
            st.write("[Learn more](https://www.heart.org/en/health-topics/high-blood-pressure/changes-you-can-make-to-manage-high-blood-pressure)")
        elif condition == 'Diabetes':
            st.image("diabetes.png", caption="Diabetes Precautions", use_container_width=True)
            st.write("Precautions for Diabetes: ")
            st.markdown(""" •	Choose drinks without added sugar. <br>
                            •	Choose higher fibre carbs. <br>
                            •	Cut down on red and processed meat. <br>
                            •	Eat plenty of fruits and vegetables. <br>
                            •	Be sensible with alcohol.<br> 
                            •	Monitor blood sugar.<br>
                            •	Eat balanced meals.<br>
                            •	Exercise.<br>
                            •	Take prescribed medications.""",unsafe_allow_html=True)
            st.write("[Learn more](https://www.diabetes.org/diabetes)")
        elif condition == 'Depression':
            st.image("depression.png", caption="Depression Precautions", use_container_width=True)
            st.write("Precautions for Depression: ")
            st.markdown(""" 
                           •	Seek professional help.<br>
                           •	Engage in therapy. <br>
                           •	Maintain a healthy lifestyle.<br>
                           •	Get enough sleep.<br>
                           •	Avoid alcohol and drug use.<br>
                           •	Exercise regularly.<br>
                           •	Build strong relationships.<br>
                           •	Reduce stress.""",unsafe_allow_html=True)
            st.write("[Learn more](https://www.nimh.gov/health/topics/depression)")
        elif condition == 'Asthma':
            st.image("asthma.png", caption="Asthma Precautions", use_container_width=True)
            st.write("Precautions for Asthma: ")
            st.markdown(""" 
                        •	Follow your asthma action plan.<br>
                        •	Get vaccinated for influenza and pneumonia. <br>
                        •	Identify and avoid asthma triggers. <br>
                        •	Monitor your breathing.<br>
                        •	Identify and treat attacks early. <br>
                        •	Take your medication as prescribed. <br>
                        •	Pay attention to increasing quick-relief inhaler use.""",unsafe_allow_html=True)
            st.write("[Learn more](https://www.cdc.gov/asthma/default.htm)")
        elif condition == 'GERD':
            st.image("gerd.png", caption="GERD Precautions", use_container_width=True)
            st.write("Precautions for GERD: ")
            st.markdown("""
                            •	Maintain a healthy weight. <br>
                            •	Stop smoking.<br>
                            •	Elevate the head of your bed. <br>
                            •	Start on your left side. <br>
                            •	Don't lie down after a meal.<br> 
                            •	Eat food slowly and chew thoroughly. <br>
                            •	Don't consume foods and drinks that trigger reflux. <br>
                            •	Don't wear tight-fitting clothing""",unsafe_allow_html=True)
            st.write("[Learn more](https://www.niddk.nih.gov/health-information/digestive-diseases/acid-reflux-ger-gerd)")
        elif condition == 'High Cholesterol':
            st.image("cholesterol.png", caption="High Cholesterol Precautions", use_container_width=True)
            st.write("Precautions for High Cholesterol: ")
            st.markdown(""" 
                           •	Eat a diet that focuses on lean protein, fruits, vegetables and whole grains. <br>
                           •	Also limit the amount of saturated and trans fats you eat. <br>
                           •	Lose extra weight and keep it off.<br>
                           •	If you smoke, ask your care team to help you quit.<br>
                           •	Exercise on most days of the week for at least 30 minutes.<br>
                           •	Take prescribed medication.<br>
                           •	Quit smoking.""",unsafe_allow_html=True)
            st.write("[Learn more](https://www.heart.org/en/health-topics/cholesterol)")
        elif condition == 'Infection':
            st.image("infection.png", caption="Infection Precautions", use_container_width=True)
            st.write("Precautions for Infection: ")
            st.markdown("""  
                           •	Hand hygiene.<br>
                           •	Use of personal protective equipment (e.g., gloves, masks, eyewear)<br>
                           •	Respiratory hygiene / cough etiquette.<br>
                           •	Use hand sanitizer when needed.<br>
                           •	Wear a mask in crowded places.<br>
                           •	Eat a balanced diet.<br>
                           •	Stay hydrated.<br>
                           •	Exercise regularly.<br>
                           •	Get enough sleep.""",unsafe_allow_html=True)
            st.write("[Learn more](https://www.cdc.gov/infections/index.html)")
        elif condition == 'Thyroid Disorder':
            st.image("thyroid.png", caption="Thyroid Precautions", use_container_width=True)
            st.write("Precautions for Thyroid Disorder: ")
            st.markdown("""  
                           •	Eat a balanced diet. <br>
                           •	Avoid processed foods.<br>
                           •	Monitor your iodine intake. <br>
                           •	Manage stress.<br>
                           •	Exercise regularly.<br> 
                           •	Get sufficient sleep.<br>
                           •	Limit environmental toxins.<br>
                           •	Take prescribed medication.""",unsafe_allow_html=True)
            st.write("[Learn more](https://www.niddk.nih.gov/health-information/endocrine-diseases/thyroid-disease)")
        elif condition == 'Pain':
            st.image("pain.png", caption="Pain Precautions", use_container_width=True)
            st.write("Precautions for Pain: Manage pain with medications, physical therapy, rest, use heat or cold packs, and practice relaxation techniques.")
            st.markdown("""  
                           •	Proper Medication Use.<br>
                           •	Rest and Relaxation.<br>
                           •	Physical Therapy & Exercise.<br>
                           •	Maintain a Healthy Diet.<br>
                           •	Maintain a healthy weight.""",unsafe_allow_html=True)
            st.write("[Learn more](https://www.mayoclinic.org/symptom-checker/pain-in-adults-adults/related-factors/itt-20072044)")
        elif condition == 'Allergies':
            st.image("allergies.png", caption="Allergies Precautions", use_container_width=True)
            st.write("Precautions for Allergies: Avoid allergens, take prescribed medications, carry an epinephrine auto-injector, monitor symptoms, and inform others about your allergies.")
            st.markdown("""  
                           •	Avoid your allergens. This is very important but not always easy. <br>
                           •	Take your medicines as prescribed. <br>
                           •	If you are at risk for anaphylaxis, keep your epinephrine auto-injectors with you at all times. <br>
                           •	Keep a diary. <br>
                           •	Wear a medical alert bracelet (or necklace). <br>
                           •	Know what to do during an allergic reaction.""",unsafe_allow_html=True)
            st.write("[Learn more](https://www.cdc.gov/nchs/fastats/allergies.htm)")
        else:
            st.write("Precautions for this condition are not yet available.")
    else:
        st.write("Please select a condition to view precautions.")


elif page == "Symptoms":
    # Precautions Page
    st.title('Drug Effectiveness Analysis Dashboard')
    st.title('Symptoms for Condition')

    # Condition Selection for Precautions Page
    condition_filter_symptoms = st.selectbox('Select Condition', df['Condition'].unique()) #Single select

    if condition_filter_symptoms:
        condition = condition_filter_symptoms
        if condition == 'High Cholesterol':
            st.image("cholesterol2.jpg", caption="High Cholesterol Symptoms", use_container_width=True)
            st.write("High cholesterol has no symptoms. A blood test is the only way to find out if you have it.")
            st.write("A very few people with High Cholesterol may have:")
            st.markdown("""
                        • Fatty Deposits on Skin.<br>
                        • Unusual Chest Pain.<br>
                        • Shortness of Breath.<br>
                        • Frequent Headaches.""",unsafe_allow_html=True)
        
        elif condition == 'Diabetes':
            st.image("diabetes2.jpg", caption="Diabetes Symptoms", use_container_width=True)
            st.write(" Some of the symptoms of diabetes are:")
            st.markdown(""" 
                        •	Feeling more thirsty than usual.<br>
                        •	Urinating often.<br>
                        •	Losing weight without trying.<br>
                        •	Presence of ketones in the urine. Ketones are a byproduct of the breakdown of muscle and fat that happens when there's not enough available insulin.<br>
                        •	Feeling tired and weak.<br>
                        •	Feeling irritable or having other mood changes.<br>
                        •	Having blurry vision.<br>
                        •	Having slow-healing sores.<br>
                        •	Getting a lot of infections, such as gum, skin and vaginal infections. """,unsafe_allow_html=True)
        elif condition == 'Depression':
            st.image("depression2.jpg", caption="Depression Symptoms", use_container_width=True)
            st.write("The symptoms of depression vary from person to person, but they commonly include:")
            st.markdown(""" 
                    •	sadness<br>
                    •	hopelessness<br>
                    •	loss of pleasure in activities<br>
                    •	irritability<br>
                    •	tiredness<br>
                    •	appetite changes<br>
                    •	thoughts of death or suicide """,unsafe_allow_html=True)
            
        elif condition == 'Asthma':
            st.image("asthma2.jpg", caption="Asthma Symptoms", use_container_width=True)
            st.write("Asthma signs and symptoms include:")
            st.markdown(""" 
                        •	Shortness of breath.<br>
                        •	Chest tightness or pain.<br>
                        •	Wheezing when exhaling, which is a common sign of asthma in children.<br>
                        •	Trouble sleeping caused by shortness of breath, coughing or wheezing.<br>
                        •	Coughing or wheezing attacks that are worsened by a respiratory virus, such as a cold or the flu.""",unsafe_allow_html=True)
        elif condition == 'GERD':
            st.image("GERD2.jpg", caption="GERD symptoms", use_container_width=True)
            st.write("Common symptoms of GERD include:")
            st.markdown("""
                        •	A burning sensation in the chest, often called heartburn. Heartburn usually happens after eating and might be worse at night or while lying down.<br>
                        •	Backwash of food or sour liquid in the throat.<br>
                        •	Upper belly or chest pain.<br>
                        •	Trouble swallowing, called dysphagia.<br>
                        •	Sensation of a lump in the throat.  """,unsafe_allow_html=True)
        elif condition == 'Hypertension':
            st.image("hypertension2.jpeg", caption="Hypertension Symptoms", use_container_width=True)
            st.write("Most people with high blood pressure have no symptoms, even if blood pressure readings reach dangerously high levels. You can have high blood pressure for years without any symptoms.")
            st.write("A few people with high blood pressure may have:")
            st.markdown("""  
                       •	Headaches<br>
                       •	Shortness of breath<br>
                       •	Nosebleeds<br>
                       •	Dizziness<br>
                       •	Weakness """,unsafe_allow_html=True)
            st.write("However, these symptoms aren't specific. They usually don't occur until high blood pressure has reached a severe or life-threatening stage.")
        elif condition == 'Infection':
            st.image("infection3.jpg", caption="Infection Symptoms", use_container_width=True)
            st.write("Signs and symptoms of a bacterial infection may vary depending on the location of the infection and the type of bacteria that’s causing it.")
            st.write("However, some general symptoms of a bacterial infection include:")
            st.markdown(""" 
                        •	fever<br>
                        •	feeling tired or fatigued<br>
                        •	swollen lymph nodes in the neck, armpits, or groin<br>
                        •	headache<br>
                        •	nausea or vomiting """,unsafe_allow_html=True)

        elif condition == 'Thyroid Disorder':
            st.image("thyroid2.jpg", caption="Thyroid Symptoms", use_container_width=True)
            st.write("Symptoms and signs of hyperthyroidism:")
            st.markdown("""
                        •	Nervousness, tremor, agitation<br>
                        •	Irritability<br>
                        •	Poor concentration<br>
                        •	Reduced menstrual blood flow in women<br>
                        •	Racing heartbeat<br>
                        •	Heat intolerance<br>
                        •	Changes in bowel habits, such as more frequent bowel movements<br>
                        •	Enlargement of the thyroid gland<br>
                        •	Skin thinning<br>
                        •	Brittle hair<br>
                        •	Increase in appetite, feeling hungry<br>
                        •	Sweating  """,unsafe_allow_html=True)
        elif condition == 'Pain':
            st.image("pain2.jpg", caption="Pain symptoms", use_container_width=True)
            st.write("Pain can manifest in different ways depending on its cause, location, and severity. Common symptoms of pain include:")
            st.markdown("""
                        •	Sharp, stabbing pain<br>
                        •	Dull, aching pain<br>
                        •	Burning sensation<br>
                        •	Stiffness or restricted movement<br>
                        •	Swelling or inflammation<br>
                        •	Increased sensitivity to touch<br>
                        •	Irritability or mood changes<br>
                        •	Fatigue or trouble sleeping<br>
                        •	Loss of appetite""",unsafe_allow_html=True)
        elif condition == 'Allergies':
            st.image("allergies2.jpg", caption="Allergies symptoms", use_container_width=True)
            st.write("No matter what you're allergic to, the symptoms can be similar.")
            st.write("Common symptoms of skin allergies include:")
            st.markdown(""" 
                        •	Rash<br>
                        •	Itch<br>
                        •	Redness<br>
                        •	Swelling<br>
                        •	Bumps<br>
                        •	Flaky skin<br>
                        •	Cracked skin""",unsafe_allow_html=True)
        else:
            st.write("Precautions for this condition are not yet available.")
    else:
        st.write("Please select a condition to view precautions.")