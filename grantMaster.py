import json
import pandas as pd
import streamlit as st

# Full Streamlit doc:
# https://docs.streamlit.io/

# https://docs.streamlit.io/develop/api-reference/caching-and-state/st.cache_data
@st.cache_data
def loadSeedData():
    """
    Load student and grant JSON files into separate DataFrames.
    Returns DataFrames as a tuple.
    """

    with open("mock_data/seed_data.json", "r", encoding="UTF-8") as inFile:
        data = json.load(inFile)

    studentsData = pd.DataFrame(data["students"])
    grantsData = pd.DataFrame(data["grants"])

    return studentsData, grantsData

# def selectStudent(students_df):
#     """
#     Prompts user to select a student by index.
#     Counts the rows in the students_df to test user entry.
#     Returns a single-row DataFrame for the chosen student/index.
#     """

#     row_count = len(students_df)
#     print(f"There are {row_count} students available.")

#     while True:
#         try:
#             userInput = int(input(f"Enter a student index (0 to {row_count - 1}): "))
#             if 0 <= userInput <= row_count - 1:
#                 break
#             else:
#                 print(f"Please enter a number between 0 and {row_count - 1}.")
#         except ValueError:
#             print(f"Invalid input. Please enter a whole number between 0 and {row_count - 1}")
    
#     studentDict = students_df.iloc[[userInput]]

#     return studentDict

def constructQuery(grant):
    """
    Takes a single grant row from the grants_df and builds a pandas .query() string...
    by iterating through the criterionMap dictionary.
    Returns the query string, or None if no the grant has no criteria.
    """

    """
    Map of grants table's criterion fields to the students table with filtering logic.
    Used to dynamically construct a query for each grant.
    Any grant criterion that is null/false are not accumulated into the dynamic query.
    """
    criterionMap = {
        "minimum_gpa":              "gpa >= {value}",
        "required_academic_year":   "academic_year == '{value}'",
        "major_requirement":        "major == '{value}'",
        "residency":                "residency == '{value}'",
        "race":                     "race == '{value}'",
        "ethnicity":                "ethnicity == '{value}'",
        "gender":                   "gender == '{value}'",
        "first_gen":                "first_gen == True",
        "disability":               "disability == True",
        "military":                 "military == True",
    }

    conditions = []

    for grant_field, query_template in criterionMap.items():
        value = grant.get(grant_field)
        # Skip if null or False
        if value is None or value is False or pd.isna(value):
            continue
        # Boolean fields don't need variable substitution
        if isinstance(value, bool):
            conditions.append(query_template)
        else:
            conditions.append(query_template.format(value=value))
        
    if not conditions:
        return None
    
    return " and ".join(conditions)

def searchGrants(student, grants):
    """
    Loops through every grant in the grants dataframe.
    Obtains a query string from constructQuery() and applies it to the student_df.
    Returns a filtered DataFrame of grants containing only eligible grants.
    """
    
    qualified = []

    for index, grant in grants.iterrows():
        query = constructQuery(grant)
        # If no criteria, all students qualify
        if query is None:
            qualified.append(index)
            continue
        try:
            result = student.query(query)
            if not result.empty:
                qualified.append(index)
        except Exception as e:
            print(f"Query failed for grant '{grant.get('grant_name')}': {e}")

    return grants.loc[qualified]

# def main():
#     students_df, grants_df = loadSeedData()
#     student_df = selectStudent(students_df)
#     searchGrants(student_df, grants_df)

# main()

def showWelcomePage():
    # Display the "Welcome" page
    st.title("grantMaster")

    st.divider()

    st.write("Each year, millions of dollars in college grants go unclaimed. This isn't because students don't qualify, but because they never hear about the opportunities.")
    st.write("That's where grantMaster hopes to step in.")
    st.write("grantMaster will use student registration data to automatically search for grants that a student may be eligible for. When possible, it will apply on their behalf.")
    st.write("Nothing extra, aside from opting into the program when registering for classes, will be asked of students. The data used to determine eligibility is data they already provide to their college when registering.")
    st.write("grantMaster is designed to run automatically in the background. Grants will be searched for all students before the start of a new semester, when a new grant is added to the database, or when a student's registration data changes (such as declaring a new major).")
    st.write("What you'll see on the next page is a simulation of a student's academic profile being matched against available grants, a window into what grantMaster will do automatically, at scale, and without any manual involvement from the student.")
    st.divider()
    # button info: https://docs.streamlit.io/develop/api-reference/widgets/st.button
    if st.button("Get Started", width="content"):
        st.session_state.page = "form"
        st.rerun()

def showFormPage():
    # Display the "Form" page
    st.title("Student Profiles")
    # Create a drop-down list of students in the database
    studentOptions = (students["first_name"] + " " + students["last_name"]).tolist()
    # selectbox info: https://docs.streamlit.io/develop/api-reference/widgets/st.selectbox
    selectedStudent = st.selectbox(
        label="Select a Student",
        options=studentOptions,
        index=None,
        placeholder="Select a student",
        accept_new_options=False,
        width="stretch",
        )

    # Due to how I've set up the selectbox object, with "Select a student" being...
    # the placeholder string in the dropdown box, "Select a student" will result...
    # in an IndexError as it's not in the studentOptions list and is therefore...
    # out of bounds. I'm wrapping the code in a try/except block to avoid displaying...
    # an exception on the screen.
    try:
        student = students[(students["first_name"] + " " + students["last_name"]) == selectedStudent].iloc[[0]]
        # Loading the student data into a dictionary to avoid needing to write iloc[0]; get() is less
        studentDict = student.iloc[0].to_dict()

        st.divider()
        
        st.subheader(body="Personal Information",
                     width="content",
                     text_alignment="left")
        st.write(f"**Name:** {studentDict.get('first_name')} {studentDict.get('middle_name', '') if not 'None' else ""} {studentDict.get('last_name')}")
        st.write(f"**Email:** {studentDict.get('email', '—')}")
        st.write(f"**Phone:** {studentDict.get('phone_number', '—')}")
        st.write(f"**Address:** {studentDict.get('street_address', '—')}, {studentDict.get('city', '—')}, {studentDict.get('state', '—')} {studentDict.get('zip_code', '—')}")

        st.subheader(body="Academic Information",
                     width="content",
                     text_alignment="left")
        st.write(f"**Major:** {studentDict.get('major', '—')}")
        st.write(f"**Concentration:** {studentDict.get('concentration', '—')}")
        st.write(f"**Year:** {studentDict.get('academic_year', '—')}")
        st.write(f"**GPA:** {studentDict.get('gpa', '—')}")
        st.write(f"**Enrollment:** {studentDict.get('enrollment_status', '—')}")
        st.write(f"**Residency:** {studentDict.get('residency', '—')}")

        st.subheader(body="Demographic Information",
                     width="content",
                     text_alignment="left")
        st.write(f"**Financial Class:** {studentDict.get('financial_class', '—')}")
        st.write(f"**Race:** {studentDict.get('race', '—')}")
        st.write(f"**Ethnicity:** {studentDict.get('ethnicity', '—')}")
        st.write(f"**Gender:** {studentDict.get('gender', '—')}")
        st.write(f"**First Gen:** {'Yes' if studentDict.get('first_gen') else 'No'}")
        st.write(f"**Disability:** {'Yes' if studentDict.get('disability') else 'No'}")
        st.write(f"**Military:** {'Yes' if studentDict.get('military') else 'No'}")

        st.subheader(body="grantMaster Consent")
        # Consent needs to be stored in a variable, I need to test it so it so I can...
        # display the right messages to the screen depending on what's in the variable
        opted_in = studentDict.get("opted_in")
        st.write(f"**Opted In:** {'Yes' if opted_in else 'No'}")

        st.divider()

        # button info: https://docs.streamlit.io/develop/api-reference/widgets/st.button
        if st.button("Search for Grants", width="content"):
            results = searchGrants(student, grants)
            st.session_state.match_results = results
            st.session_state.opted_in = opted_in
            st.session_state.student_name = selectedStudent
            st.session_state.page = "results"
            st.rerun()
    except IndexError:
        pass

def showResultsPage():
    opted_in = st.session_state.opted_in
    results = st.session_state.match_results
    name = st.session_state.student_name

    # I'll work on this tomorrow...
    # the variables above are what I should need to display the grant search results...

students, grants = loadSeedData()

# https://docs.streamlit.io/develop/api-reference/configuration/st.set_page_config
st.set_page_config(
    page_title="grantMaster",
    # page_icon=":dollar:",
    page_icon=":martial_arts_uniform:",
    layout="wide",
    initial_sidebar_state="auto",
    menu_items=None
    )

# https://youtu.be/92jUAXBmZyU?list=TLGGYqrRVqMdT0wxNDAzMjAyNg
if "page" not in st.session_state:
    st.session_state["page"] = "welcome"

# https://docs.streamlit.io/develop/api-reference/caching-and-state/st.session_state
page = st.session_state.page
if page == "welcome":
    showWelcomePage()
elif page == "form":
    showFormPage()
elif page == "results":
    showResultsPage()
