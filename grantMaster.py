
import json
import pandas as pd
import smtplib
import streamlit as st

###########
# FUNCTIONS
###########


# Full Streamlit doc:
# https://docs.streamlit.io/

###########
# FUNCTIONS
###########

# https://docs.streamlit.io/develop/api-reference/caching-and-state/st.cache_data
@st.cache_data
def loadStudentData():
    with open("mock_data/mockData.json", "r", encoding="UTF-8") as inFile:
        data = json.load(inFile)
    studentsData = pd.DataFrame(data["students"])
    return studentsData
# f
@st.cache_data
def loadGrantData():
    with open("mock_data/mockData.json", "r", encoding="UTF-8") as inFile:
        data = json.load(inFile)
    grantsData = pd.DataFrame(data["grants"])
    return grantsData

def constructQuery(grant):
    # Takes a single grant row from the grants_df and builds a pandas .query() string...
    # by iterating through the criterionMap dictionary.
    # Returns the query string, or None if no the grant has no criteria.

    # Map of grants table's criterion fields to the students table with filtering logic.
    # Used to dynamically construct a query for each grant.
    # Any grant criterion that is null/false are not accumulated into the dynamic query.
    criterionMap = {
        "minimum_gpa":              "gpa >= {value}",
        "required_academic_year":   "academic_year == '{value}'",
        "major_requirement":        "major == '{value}'",
        "financial_need":           "financial_need == True",
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
    # Loops through every grant in the grants dataframe.
    # Obtains a query string from constructQuery() and applies it to the student_df.
    # Returns a filtered DataFrame of grants containing only eligible grants.
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

def addWelcomeButton(label):
    if st.button(
        label=label,
        width="content"
        ):
        st.session_state.page = "welcome"
        st.rerun()

def addFormButton(label):
    if st.button(
        label=label,
        width="content"
        ):
        st.session_state.page = "form"
        st.rerun()

def addResultsButton(student):
    if st.button(
        label="Search for Grants",
        width="content"
        ):
        st.session_state.student = student
        st.session_state.page = "results"
        st.rerun()

def addOptedOutButton(student):
    if st.button(
        label="Search for Grants",
        width="content"):
        st.session_state.student_name = student
        st.session_state.page = "optedOut"
        st.rerun()

def addTeamButton():
    if st.button(
        label="Meet the Team",
        width="content"
        ):
        st.session_state.page = "about"
        st.rerun()

def showWelcomePage():
    # Title info: https://docs.streamlit.io/develop/api-reference/text/st.title
    st.title(
        body="grantMaster",
        anchor=None,
        width="content",
        text_alignment="left"
        )
    st.divider()
    st.write("Each year, billions of dollars in college grants go unclaimed. This isn't because students don't qualify, but because they never hear about the opportunities.")
    st.write("That's where grantMaster hopes to step in.")
    st.write("grantMaster will use student registration data to automatically search for grants that a student may be eligible for. When possible, it will apply on their behalf.")
    st.write("To use grantMaster, a college signs a data sharing agreement that details how student data is handled. The college also sets up a connection between their existing registration system and grantMaster so that data can be shared.")
    st.write("Nothing extra, aside from opting into the program when registering for classes, will be asked of students. The data used to determine eligibility is data they already provide to their college when registering.")
    st.write("grantMaster is designed to run automatically in the background. Grants will be searched for all students before the start of a new semester, when a new grant is added to the database, or when a student's registration data changes (such as declaring a new major).")
    st.write("What you'll see on the following pages is a simulation of a student's academic profile being matched against available grants, a look into what grantMaster will do automatically, at scale, and without any manual involvement from the student.")
    st.divider()
    addFormButton("Get Started")
    addTeamButton()

def showFormPage():
    students = loadStudentData()
    st.title(
        body="Student Profiles",
        anchor=None,
        width="content",
        text_alignment="left"
        )
    # Create a drop-down list of students in the database
    studentOptions = (students["first_name"] + " " + students["last_name"]).tolist()
    # selectbox info: https://docs.streamlit.io/develop/api-reference/widgets/st.selectbox
    selectedStudent = st.selectbox(
        label="Select a Student",
        options=studentOptions,
        index=None,
        placeholder="",
        accept_new_options=False,
        width="stretch",
        )
    # Due to how I've set up the selectbox object, with "" being...
    # the placeholder string in the dropdown box, "Select a student" will result...
    # in an IndexError as it's not in the studentOptions list and is therefore...
    # out of bounds. I'm wrapping the code in a try/except block to avoid displaying...
    # an exception on the screen.
    try:
        student = students[(students["first_name"] + " " + students["last_name"]) == selectedStudent].iloc[[0]]
        # Loading the student data into a dictionary to avoid needing to write iloc[0]; get() is less
        studentDict = student.iloc[0].to_dict()
        st.divider()
        st.subheader(
            body="Personal Information",
            width="content",
            text_alignment="left"
            )
        st.write(f"**Name:** {studentDict.get('first_name')} {studentDict.get('middle_name') if studentDict.get('middle_name')  else ''} {studentDict.get('last_name')}")
        st.write(f"**Email:** {studentDict.get('email', '—')}")
        st.write(f"**Phone:** {studentDict.get('phone_number', '—')}")
        st.write(f"**Address:** {studentDict.get('street_address', '—')}, {studentDict.get('city', '—')}, {studentDict.get('state', '—')} {studentDict.get('zip_code', '—')}")
        st.subheader(
            body="Academic Information",
            width="content",
            text_alignment="left"
            )
        st.write(f"**Major:** {studentDict.get('major', '—')}")
        st.write(f"**Concentration:** {studentDict.get('concentration', '—')}")
        st.write(f"**Year:** {studentDict.get('academic_year', '—')}")
        st.write(f"**GPA:** {studentDict.get('gpa', '—')}")
        st.write(f"**Enrollment:** {studentDict.get('enrollment_status', '—')}")
        st.write(f"**Residency:** {studentDict.get('residency', '—')}")
        st.subheader(
            body="Demographic Information",
            width="content",
            text_alignment="left"
            )
        st.write(f"**Financial Need:** {studentDict.get('financial_need', '—')}")
        st.write(f"**Race:** {studentDict.get('race', '—')}")
        st.write(f"**Ethnicity:** {studentDict.get('ethnicity', '—')}")
        st.write(f"**Gender:** {studentDict.get('gender', '—')}")
        st.write(f"**First Gen:** {'Yes' if studentDict.get('first_gen') else 'No'}")
        st.write(f"**Disability:** {'Yes' if studentDict.get('disability') else 'No'}")
        st.write(f"**Military:** {'Yes' if studentDict.get('military') else 'No'}")
        st.subheader(
            body="grantMaster Consent",
            width="content",
            text_alignment="left"
            )
        opted_in = studentDict.get("opted_in")
        st.write(f"**Opted In:** {'Yes' if opted_in else 'No'}")
        st.divider()
        if opted_in:
            addResultsButton(student)
        else:
            studentName = student["first_name"].iloc[0] + " " + student["last_name"].iloc[0]
            addOptedOutButton(studentName)

        addWelcomeButton("Return Home")
    except IndexError:
        st.divider()
        addWelcomeButton("Return Home")

def showOptedOutPage():
    name = st.session_state.student_name
    st.title(
        body=f"Results for {name}",
        anchor=None,
        width="content",
        text_alignment="left"
        )
    st.write("You have not opted into grantMaster. If you'd like to receive grant eligibility information, please contact your college's Registrar to opt-in.")
    addFormButton("Check a Different Student")
    addWelcomeButton("Return Home")

def showResultsPage():
    student = st.session_state.student
    name = student["first_name"].iloc[0] + " " + student["last_name"].iloc[0]

    # Email tutorial: https://www.youtube.com/watch?v=ueqZ7RL8zxM
    senderEmail = "codeminers4tw@gmail.com"
    appPassword = st.secrets["GMAIL_PASSWORD"]
    recipientEmail = "grantMaster_Test@guerrillamail.com"
    defaultText = f"Good news from grantMaster, {name}!\n\n"
    text = defaultText
    inbox = "https://www.guerrillamail.com/inbox/grantMaster_Test"

    grants = loadGrantData()
    results = searchGrants(student, grants)
    st.title(
        body=f"Results for {name}",
        anchor=None,
        width="content",
        text_alignment="left"
        )
    st.divider()
    if results.empty:
        st.write("Unfortunately, no grants were found that matched to your profile. But don't worry, we'll keep an eye out for you.")
    else:
        grantCount = len(results)
        autoApply = results[results["auto_apply"] == True]
        manualApply = results[results["auto_apply"] == False]
        if grantCount == 1:
            st.write(f"{grantCount} grant has matched your profile.")
        else:
            st.write(f"{grantCount} grants have matched your profile.")
        if not autoApply.empty:
            counter = 0
            header = "Auto-Applied Grants"
            st.subheader(
                body=header,
                width="content",
                text_alignment="left"
                )
            text += f"{header}\n"
            for index, grant in autoApply.iterrows():
                counter += 1
                message = f"{counter}. {grant['grant_name']} from the {grant['grantor']} for ${grant['amount']:,.0f}" 
                st.write(message)
                text += f"{message}\n"
            text += "\n"
        if not manualApply.empty:
            counter = 0
            header = "Grant Opportunities"
            st.subheader(
                body=header,
                width="content",
                text_alignment="left"
                )
            text += f"{header}\n"
            for index, grant in manualApply.iterrows():
                counter += 1
                message = (
                    f"{counter}. {grant['grant_name']} from the {grant['grantor']} for ${grant['amount']:,.0f}"
                    + "\n\n\t"
                    + f"Requires from you: {grant['manual_component']}"
                    + "\n\n\n\t"+ f"Apply at: {grant['app_url']}"
                    + f"\n\n\n"
                    )
                st.write(message)
                text += f"{message}"
    st.divider()
    # Send email
    try:
        if text != defaultText:
            text += "\nGood luck!\n\nSigned,\nThe grantMaster Team"
            with smtplib.SMTP("smtp.gmail.com", 587) as server:
                server.starttls()
                server.login(senderEmail, appPassword)
                server.sendmail(senderEmail, recipientEmail, text)
            # link button: https://docs.streamlit.io/develop/api-reference/widgets/st.link_button
            st.link_button(
            label="View Demo Inbox*",
            url=inbox,
            width="content"
            )
    except smtplib.SMTPException:
        st.warning("Email notification could not be sent, an email server error was encountered.")
    addFormButton("Check a Different Student")
    addWelcomeButton("Return Home")
    if text != defaultText:
        st.caption(
        body="*Emails may take a moment to arrive in inbox; inbox is provided by a free third-party service.",
        width="content",
        text_alignment="left"
        )
        st.caption(
            body="*For best experience, close the inbox tab after viewing email.",
            width="content",
            text_alignment="left"
            )

def showTeamPage():
    st.title(
        body="Meet the Team",
        anchor=None,
        width="content",
        text_alignment="left"
    )
    st.divider()
    st.subheader(
        body="Maura Carter",
        width="content",
        text_alignment="left"
        )
    st.markdown("[Maura](https://www.linkedin.com/in/mauracarter/) is completing an Artificial Intelligence Fundamentals Certificate, and has a background in statistics and data science. Maura was responsible for refining the concept of grantMaster and leading the presentation.")
    st.subheader(
        body="Jaime Delgado-Guzman",
        width="content",
        text_alignment="left"
    )
    st.markdown("[Jaime](https://www.linkedin.com/in/poliscianalyst/) is obtaining an IT Certificate in Python, getting his start with programming through data analysis and engineering. Jaime was the lead developer for grantMaster.")
    st.subheader(
        body="David Diza",
        width="content",
        text_alignment="left"
    )
    st.markdown("[David](https://www.linkedin.com/in/daviddiza/) is a CPCC Computer Software Developer student, with a background in Java and other programming languages. David was the code reviewer and tester for grantMaster.")
    st.subheader(
        body="Zoe Ramirez",
        width="content",
        text_alignment="left"
    )
    st.markdown("[Zoe](https://www.linkedin.com/in/zoe-ramirez-21724424b/) is working towards CPCC's Cyber Security IT Certificate. Zoe organized the team communication and workflow logistics for Code Miners.")
    st.divider()
    addFormButton("Get Started")
    addWelcomeButton("Return Home")

#########
# WEB APP
#########

# https://docs.streamlit.io/develop/api-reference/configuration/st.set_page_config
st.set_page_config(
    page_title="grantMaster",
    # page_icon=":dollar:",
    page_icon=":martial_arts_uniform:",
    layout="wide",
    initial_sidebar_state="auto",
    menu_items=None
    )

# Caption: https://docs.streamlit.io/develop/api-reference/text/st.caption
st.caption(
    body="Rhodes Deep by Ronald Jenkees (w/ permission from artist)",
    width="stretch",
    text_alignment="right"
)
# Play music: https://docs.streamlit.io/develop/api-reference/media/st.audio
st.audio(
    data="audio/Ronald Jenkees - Rhodes Deep - 01 Rhodes Deep.wav",
    format="audio/wav",
    start_time=0,
    loop=True,
    autoplay=False,
    width="stretch"
)

if "page" not in st.session_state:
    st.session_state["page"] = "welcome"

# https://docs.streamlit.io/develop/api-reference/caching-and-state/st.session_state
page = st.session_state.page
if page == "welcome":
    showWelcomePage()
elif page == "about":
    showTeamPage()
elif page == "form":
    showFormPage()
elif page == "optedOut":
    showOptedOutPage()
elif page == "results":
    showResultsPage()
