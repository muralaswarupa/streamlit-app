import streamlit as st
import pandas as pd
import psycopg2
import base64

# Streamlit app settings (must be the first Streamlit command)
st.set_page_config(
    page_title="Diabetes Database App",
    page_icon="🩺",
    layout="wide"
)


def get_connection():
    return psycopg2.connect(
        database="diabetes_db",  # Replace with your database name
        user="postgres",         # Replace with your PostgreSQL username
        password="swarupa",      # Replace with your PostgreSQL password
        host="4.tcp.ngrok.io",   # Use the ngrok public host
        port="10031"             # Use the ngrok public port
    )



def run_query(query):
    conn = get_connection()
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

# Function to add background images using CSS
def add_background(image_file):
    with open(image_file, "rb") as img_file:
        encoded_string = base64.b64encode(img_file.read()).decode()
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/jpeg;base64,{encoded_string}");
            background-size: cover;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# Function to add sidebar image
def add_sidebar_image(image_file):
    st.sidebar.image(image_file, use_container_width=True)

# Add background and sidebar images
add_background("image1.jpg")  # Replace with the path to your background image
add_sidebar_image("image2.jpg")  # Replace with the path to your sidebar image

# App title
st.title("📊 Diabetes Database Management System")
st.markdown("<h4 style='text-align: center; color: darkblue;'>Manage and Visualize Patient Data with Ease</h4>", unsafe_allow_html=True)

# Sidebar menu
menu = ["Insert", "Update", "Delete", "Select", "Visualize"]
choice = st.sidebar.selectbox("Menu", menu)

# Insert Operation
if choice == "Insert":
    st.subheader("Insert Patient Data")
    st.markdown("Add new patient records to the database.")
    patient_id = st.number_input("Patient ID", step=1)
    gender = st.selectbox("Gender", ["Male", "Female", "Other"])
    age = st.number_input("Age", step=1)
    if st.button("Insert Patient"):
        try:
            conn = get_connection()
            cursor = conn.cursor()
            query = f"INSERT INTO patients (patient_id, gender, age) VALUES ({patient_id}, '{gender}', {age});"
            cursor.execute(query)
            conn.commit()
            conn.close()
            st.success(f"✅ Patient ID {patient_id} inserted successfully!")
        except Exception as e:
            st.error(f"❌ Error: {e}")

# Update Operation
elif choice == "Update":
    st.subheader("Update Patient Data")
    st.markdown("Modify existing patient records.")
    patient_id = st.number_input("Enter Patient ID to Update", step=1)
    new_age = st.number_input("New Age", step=1)
    if st.button("Update Age"):
        try:
            conn = get_connection()
            cursor = conn.cursor()
            query = f"UPDATE patients SET age = {new_age} WHERE patient_id = {patient_id};"
            cursor.execute(query)
            conn.commit()
            conn.close()
            st.success(f"✅ Patient ID {patient_id} updated successfully!")
        except Exception as e:
            st.error(f"❌ Error: {e}")

# Delete Operation
elif choice == "Delete":
    st.subheader("Delete Patient Data")
    st.markdown("Remove patient records from the database.")
    patient_id = st.number_input("Enter Patient ID to Delete", step=1)
    if st.button("Delete Patient"):
        try:
            conn = get_connection()
            cursor = conn.cursor()
            query = f"DELETE FROM patients WHERE patient_id = {patient_id};"
            cursor.execute(query)
            conn.commit()
            conn.close()
            st.success(f"✅ Patient ID {patient_id} deleted successfully!")
        except Exception as e:
            st.error(f"❌ Error: {e}")

# Select Operation
elif choice == "Select":
    st.subheader("Retrieve Patient Data")
    query = st.text_area("Enter your SELECT query:")
    if st.button("Run Query"):
        if query.strip():
            try:
                df = run_query(query)
                if not df.empty:
                    st.dataframe(df)
                else:
                    st.warning("⚠️ No results found!")
            except Exception as e:
                st.error(f"❌ Error executing query: {e}")
        else:
            st.warning("⚠️ Please enter a valid SQL query.")

# Visualize Data
# Visualize Data
elif choice == "Visualize":
    st.subheader("Visualize Patient Data")
    st.markdown("Create interactive visualizations of the data.")

    # Let the user choose a visualization type
    viz_type = st.selectbox("Select Visualization Type", ["Bar Chart", "Line Chart", "Pie Chart"])
    
    # Let the user specify a query for visualization
    st.markdown("### Custom SQL Query for Visualization")
    query = st.text_area(
        "Enter your query for visualization:",
        """
SELECT 
    CASE 
        WHEN age BETWEEN 0 AND 18 THEN '0-18'
        WHEN age BETWEEN 19 AND 35 THEN '19-35'
        WHEN age BETWEEN 36 AND 50 THEN '36-50'
        WHEN age BETWEEN 51 AND 65 THEN '51-65'
        ELSE '66+' 
    END AS age_group,
    COUNT(*) AS patient_count
FROM patients
GROUP BY age_group
ORDER BY age_group;

        """
    )

    if st.button("Generate Visualization"):
        try:
            # Run the user-provided query
            data = run_query(query)
            
            if data.empty:
                st.warning("⚠️ No data available for visualization.")
            else:
                # Visualization based on user selection
                if viz_type == "Bar Chart":
                    st.bar_chart(data.set_index(data.columns[0]))
                elif viz_type == "Line Chart":
                    st.line_chart(data.set_index(data.columns[0]))
                elif viz_type == "Pie Chart":
                    # Pie chart requires specific handling
                    import plotly.express as px
                    st.markdown("### Pie Chart")
                    pie_chart = px.pie(data, names=data.columns[0], values=data.columns[1])
                    st.plotly_chart(pie_chart)
        except Exception as e:
            st.error(f"❌ Error generating visualization: {e}")
