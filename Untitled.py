#!/usr/bin/env python2


import requests
from bs4 import BeautifulSoup
import pandas as pd
from tabulate import tabulate
from slack_client import slacker

slacker()("Im running!!!")

url = 'https://www.mohfw.gov.in/'
response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')
rows = soup.findAll('tr')

slacker()("Got result from website")

df = pd.DataFrame(columns=[
                  'S.No.', 'State/UT', 'ConfirmedIndia', 'ConfirmedForeign', 'Recovered', 'Died'])
i = 0
for row in rows[1:-1]:
    columns = row.find_all('td')
    df_row = [col.text for col in columns]
    df.loc[i] = df_row
    i = i+1

slacker()("DF ready")

oldDF = pd.read_json(
    '/home/sanchit/Desktop/Sanchit/slack-bot/Data.json', orient='split')

slacker()("Old DF ready")

mergedStuff = pd.merge(df, oldDF, on=['State/UT'], how='outer')

slacker()("Merged DF ready")


def isSame(row):
    result = float(row['ConfirmedIndia_x']) == row['ConfirmedIndia_y'] and float(row['ConfirmedForeign_x']) == row['ConfirmedForeign_y'] and float(
        row['Recovered_x']) == row['Recovered_y'] and float(row['Died_x']) == row['Died_y']
    return result


indexes = []
for index, row in mergedStuff.iterrows():
    if isSame(row):
        indexes.append(index)

mergedStuff = mergedStuff.drop(indexes)

slacker()("Duplicate stuff dumped")

if not mergedStuff.empty:

    heading = ["State", "CI(now)", "CI(earlier)", "CF(now)", "CF(earlier)",
               "Rec(now)", "Rec(earlier)", "Deaths(now)", "Deaths(earlier)"]
    stats = []
    for index, row in mergedStuff.iterrows():
        stats.append([row["State/UT"], row["ConfirmedIndia_x"], row["ConfirmedIndia_y"], row["ConfirmedForeign_x"],
                      row["ConfirmedForeign_y"], row["Recovered_x"], row["Recovered_y"], row["Died_x"], row["Died_y"]])

    text = tabulate(stats, headers=heading, tablefmt="orgtbl")
    slacker()("Text ready")
    slacker()(text)
    slacker()(tabulate(df, headers=df.columns, tablefmt="psql"))
    slacker()("Send to slack")

    df.to_json(r'/home/sanchit/Desktop/Sanchit/slack-bot/Data.json',
               orient='split')
    slacker()("Updated the JSON")

slacker()("Script ends")
