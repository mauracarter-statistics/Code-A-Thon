import json
import pandas as pd
import hashlib
import random


# Define CONSTANT(S) and variable(s)

"""
Map of grants table's criterion fields to the students table with filtering logic.
Used to dynamically construct a query for each grant.
Any grant criterion that is null/false are not accumulated into the dynamic query.
"""
CRITERION_MAPPING = {
    "minimum_gpa": "gpa >= {value}",
    "required_academic_year": "academic_year == '{value}'",
    "major_requirement":      "major == '{value}'",
    "residency":              "residency == '{value}'",
    "race":                   "race == '{value}'",
    "ethnicity":              "ethnicity == '{value}'",
    "gender":                 "gender == '{value}'",
    "first_gen":              "first_gen == True",
    "disability":             "disability == True",
    "military":               "military == True",
}

def hashPassword(password):
    return hashlib.sha256(password.encode()).hexdigest()

def sendMFACode(phone):

    code = random.randint(100000, 999999)

    print(f"MFA code sent to {phone}")
    print(f"(Simulation code: {code})")

    return str(code)


def loadSeedData():
    """
    Load student and grant JSON files into separate DataFrames.
    Returns DataFrames as a tuple.
    """

    with open("mock_data/seed_data.json", "r", encoding="UTF-8") as inFile:
        data = json.load(inFile)
    
    studentsData = pd.DataFrame(data["students"])
    grantsData = pd.DataFrame(data["grants"])

    # # Preview the data; update the 'previewNum' variable to preview more/less
    # previewNum = 3
    # print("'Students' table preview:")
    # print(studentsData.head(previewNum))
    # print("'Grants' table preview:")
    # print(grantsData.head(previewNum))
    
    return studentsData, grantsData


def loginStudent(students_df):

    email = input("Enter your school email: ")

    student = students_df[students_df["email"] == email]

    if student.empty:
        print("Email not found in school records.")
        return None

    student_index = student.index[0]

    stored_password = students_df.loc[student_index, "password"]

    # First time login
    if pd.isna(stored_password):

        print("First time login detected.")

        phone = students_df.loc[student_index, "phone_number"]

        code = sendMFACode(phone)

        user_code = input("Enter MFA code: ")

        if user_code != code:
            print("MFA verification failed.")
            return None

        new_password = input("Create your password: ")

        students_df.loc[student_index, "password"] = hashPassword(new_password)

        print("Account activated successfully.")

    # Normal login
    else:

        password = input("Enter password: ")

        if hashPassword(password) != stored_password:
            print("Incorrect password.")
            return None

    return students_df.iloc[[student_index]]

def constructQuery(grant):
    """
    Takes a single grant row from the grants_df and builds a pandas .query() string...
    by iterating through the CRITERION_MAPPING dictionary.
    Returns the query string, or None if no the grant has no criteria.
    """

    conditions = []

    for grant_field, query_template in CRITERION_MAPPING.items():
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
    
    # Preview qualified grants
    previewNum = 3
    print("Qualified grants preview:")
    print(grants.loc[qualified].head(previewNum))

    return grants.loc[qualified]

def main():

    students_df, grants_df = loadSeedData()

    student_df = loginStudent(students_df)

    if student_df is None:
        print("Login failed.")
        return

    searchGrants(student_df, grants_df)

main()
