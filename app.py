
import streamlit as st
import sqlite3
import pandas as pd

# PAGE CONFIGURATION
st.set_page_config(
    page_title="Studora | Student Hub",
    page_icon="🎓",
    layout="wide"
)

# DATABASE CONNECTION
conn = sqlite3.connect("students.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS students (
    roll_no INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    age INTEGER,
    course TEXT
)
""")
conn.commit()

# CUSTOM CSS
st.markdown("""
<style>
.stApp {
    background-color: #0B1020;
    color: #F5F3FF;
}

[data-testid="stSidebar"] {
    background-color: #131A30;
    border-right: 1px solid #293250;
}

h1, h2, h3 {
    color: #F5F3FF !important;
}

p, label {
    color: #C5C8DD;
}

[data-testid="stMetric"] {
    background: linear-gradient(135deg, #1C2542, #25264A);
    border: 1px solid #393B67;
    padding: 20px;
    border-radius: 12px;
}

[data-testid="stMetricValue"] {
    color: #A99AFF;
}

.stButton > button {
    background-color: #7968E8;
    color: white;
    border-radius: 8px;
    border: none;
    padding: 8px 20px;
}

.stButton > button:hover {
    background-color: #9385FF;
    color: white;
}

hr {
    border-color: #303956;
}
</style>
""", unsafe_allow_html=True)


# SIDEBAR
with st.sidebar:
    st.markdown("# 🎓 Studora")
    st.caption("STUDENT MANAGEMENT HUB")
    st.divider()

    menu = st.radio(
        "NAVIGATION",
        ["Dashboard", "Add Student", "Student Directory",
         "Update Student", "Delete Student"]
    )

    st.divider()
    st.caption("Manage records. Simplify your work.")


# FETCH DATA
def get_students():
    return pd.read_sql_query("SELECT * FROM students", conn)


df = get_students()


# DASHBOARD
if menu == "Dashboard":

    st.title("Welcome to Studora 👋")
    st.write("Your student management dashboard.")

    st.divider()

    total = len(df)
    courses = df["course"].nunique() if total > 0 else 0
    avg_age = round(df["age"].mean(), 1) if total > 0 else 0

    col1, col2, col3 = st.columns(3)

    col1.metric("Total Students", total, "Registered")
    col2.metric("Total Courses", courses, "Available")
    col3.metric("Average Age", avg_age, "Years")

    st.divider()

    st.subheader("Recent Student Records")

    if not df.empty:
        st.dataframe(
            df.tail(5),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No student records yet. Start by adding a student!")


# CREATE
elif menu == "Add Student":

    st.title("Add New Student")
    st.caption("Register a new student in your database.")

    with st.form("add_form"):

        col1, col2 = st.columns(2)

        roll = col1.number_input(
            "Roll Number", min_value=1, step=1
        )

        name = col2.text_input("Full Name")

        age = col1.number_input(
            "Age", min_value=1, max_value=100
        )

        course = col2.text_input("Course")

        submit = st.form_submit_button("＋ Add Student")

        if submit:

            if not name.strip() or not course.strip():
                st.warning("Please fill all fields.")

            else:
                try:
                    cursor.execute(
                        "INSERT INTO students VALUES (?, ?, ?, ?)",
                        (roll, name, age, course)
                    )
                    conn.commit()
                    st.success("Student added successfully!")

                except sqlite3.IntegrityError:
                    st.error("Roll number already exists!")


# READ
elif menu == "Student Directory":

    st.title("Student Directory")
    st.caption("View and search all registered students.")

    df = get_students()

    if not df.empty:

        search = st.text_input("🔍 Search by student name or course")

        if search:
            df = df[
                df["name"].str.contains(search, case=False, na=False)
                | df["course"].str.contains(search, case=False, na=False)
            ]

        st.write(f"Showing {len(df)} student records")

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )

    else:
        st.info("No student records found.")


# UPDATE
elif menu == "Update Student":

    st.title("Update Student")
    st.caption("Modify existing student information.")

    df = get_students()

    if not df.empty:

        roll = st.selectbox(
            "Select Student Roll Number",
            df["roll_no"].tolist()
        )

        student = df[df["roll_no"] == roll].iloc[0]

        with st.form("update_form"):

            name = st.text_input("Student Name", value=student["name"])

            age = st.number_input(
                "Age", min_value=1, max_value=100,
                value=int(student["age"])
            )

            course = st.text_input("Course", value=student["course"])

            submit = st.form_submit_button("Update Record")

            if submit:

                if not name.strip() or not course.strip():
                    st.warning("Please fill all fields.")

                else:
                    cursor.execute("""
                        UPDATE students
                        SET name=?, age=?, course=?
                        WHERE roll_no=?
                    """, (name, age, course, roll))

                    conn.commit()
                    st.success("Student record updated!")

    else:
        st.info("No records available.")


# DELETE
elif menu == "Delete Student":

    st.title("Delete Student")
    st.caption("Remove a student record from the database.")

    df = get_students()

    if not df.empty:

        roll = st.selectbox(
            "Select Roll Number",
            df["roll_no"].tolist()
        )

        student = df[df["roll_no"] == roll].iloc[0]

        st.warning(
            f"You are about to delete {student['name']}'s record."
        )

        confirm = st.checkbox("I confirm that I want to delete this record")

        if st.button("Delete Record", disabled=not confirm):

            cursor.execute(
                "DELETE FROM students WHERE roll_no=?",
                (roll,)
            )

            conn.commit()
            st.success("Student record deleted successfully!")

    else:
        st.info("No records available.")

conn.close()
