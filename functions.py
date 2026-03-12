# david 03/10/2026
import json


def loadGrantInformation(): 
  """
    Generator function that yields each row of grants
    with all None values removed.
  """

  with open("mock_data/seed_data.json", "r", encoding="UTF-8") as grantFile:
    data = json.load(grantFile)
  
  for row in data["grants"]:
    clean_row = {k: v for k, v in row.items() if v is not None}
    yield clean_row



def establishForm():
  """
    Prepares the grant table for a dynamic form.
    Collects all headers once, and keeps row data ready.
  """

  all_columns = set()
  rows_data = []

  # Collect all columns across all rows and store cleaned rows
  for row in loadGrantInformation():
    all_columns.update(row.keys())
    rows_data.append(row)

  # Convert set to list for ordered headers
  headers = list(all_columns)

  # Debug print: show all headers
  print("\nAll headers for the form:", headers, "\n")

  # Now rows_data contains all cleaned rows
  for i, row in enumerate(rows_data):
    print(f"Row {i} data:")
    for col in headers:
      # Use empty string if column missing in this row
      value = row.get(col, "")
      print(f"  {col}: {value}")
      print("-" * 30)

  return headers, rows_data


#def searchQualifiedStudents():
  
    


'''
def fillUpForm():




def checkFormEmptiness():



def notitifyMonitoring():



def emailRemainder():
'''

def main():
  loadGrantInformation()
  establishForm()


main()
