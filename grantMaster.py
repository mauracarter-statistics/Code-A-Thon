import json
import pandas as pd

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

def selectStudent(students_df):
    """
    Prompts user to select a student by index.
    Counts the rows in the students_df to test user entry.
    Returns a single-row DataFrame for the chosen student/index.
    """

    row_count = len(students_df)
    print(f"There are {row_count} students available.")

    while True:
        try:
            userInput = int(input(f"Enter a student index (0 to {row_count - 1}): "))
            if 0 <= userInput <= row_count - 1:
                break
            else:
                print(f"Please enter a number between 0 and {row_count - 1}.")
        except ValueError:
            print(f"Invalid input. Please enter a whole number between 0 and {row_count - 1}")
    
    studentData = students_df.iloc[[userInput]]

    # # Preview the selected student
    # print("\nSelected student:")
    # print(studentData)

    return studentData

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
    student_df = selectStudent(students_df)
    searchGrants(student_df, grants_df)

main()
