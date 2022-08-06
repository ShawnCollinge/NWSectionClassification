import requests, time, re
from bs4 import BeautifulSoup
import pandas as pd


INPUT_FILE_NAME = "Book1.csv"
OUTPUT_FILE_NAME = "out.csv"
SLEEP_TIME = 10 # in s between member searches


StartingPrefix = ["A", "FY", "TY", "L", "B"]

DictFromCSV = pd.read_csv(INPUT_FILE_NAME).to_dict()

CompleteDict = {"firstName": {},
                "lastName": {},
                "uspsaNumber": {},
                "division": {},
                "classification": {}
                }

Index = 0

for i in DictFromCSV['firstName']:

    FoundUser = False
    id = DictFromCSV['uspsaNumber'][i]
    StrippedID = re.sub('\D', '', id)
    OriginalPrefix = id.strip(StrippedID)
    StartingIndex = 0

    while not FoundUser and StartingIndex < len(StartingPrefix):
        Response = requests.get(f"https://uspsa.org/classification/{id}")
        MySoup = BeautifulSoup(Response.text, "html.parser") 

        Error = MySoup.find(name="span", text="Error")    
        if Error is not None:
            print("Rate limited, sleeping")
            time.sleep(600)

        else:
            Error = MySoup.find(name="div", class_="alert")
            FoundUser = Error is None
            if not FoundUser:
                if StartingPrefix[StartingIndex] == OriginalPrefix:
                    StartingIndex += 1
                id = f"{StartingPrefix[StartingIndex]}{StrippedID}"
                StartingIndex += 1
        
    if FoundUser:
        Results = MySoup.find_all(name="th", scope="row")

        for j in range(9,15):
            RawDivision = Results[j].getText()
            Division = RawDivision.strip()
            RawClass = Results[j].find_next_sibling("td")
            RealClass = RawClass.getText()[-2:]
            Classification = RealClass.strip()
            if "U" not in RealClass:
                CompleteDict['firstName'][Index] = DictFromCSV['firstName'][i]
                CompleteDict['lastName'][Index] = DictFromCSV['lastName'][i]
                CompleteDict['uspsaNumber'][Index] = id
                CompleteDict['division'][Index] = Division
                CompleteDict['classification'][Index] = Classification
                Index += 1
        time.sleep(SLEEP_TIME)

df = pd.DataFrame(CompleteDict)
df.to_csv(OUTPUT_FILE_NAME, index=False)
print("Done!")