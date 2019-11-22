import requests
import time
import sqlite3
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
import pandas as pd
import matplotlib.pyplot as plt # use "pythonw" instead of "python" if there is ImportError
import sys

 # a command which is either "local" or "remote" should be entered in command-line for obtaining data locally of remotely
try:
    source = sys.argv[1]
except:
    print('Please enter "local" or "remote" in command-line')





# grab, store and manipulate data from source 1

print('*** Outputing Data Source 1 ***')
print('''This data source from API is the carbon intensity data between specified datetimes for London.
I grab the carbon inensity forecast and index between May and December in 2018, and store them in several text files.
Then I use these data to obtain monthly average carbon intensity, the forecast times of both high index and very high index.''')
print('\nAPI Endpoint: \nBase URL: https://api.carbonintensity.org.uk/regional/intensity/{from}/{to}/regionid/13 \nParameter {from}: Start datetime in in ISO8601 format YYYY-MM-DDThh:mmZ \nParameter {to}: End datetime in in ISO8601 format YYYY-MM-DDThh:mmZ \ne.g. https://api.carbonintensity.org.uk/regional/intensity/2018-05-01T00:00Z/2018-05-31T23:59Z/regionid/13')
print('\nAPI Documentation: \nhttps://carbon-intensity.github.io/api-definitions/?python#carbon-intensity-api-v2-0-0')
print('\nFile Names: \n{month}forecast.txt or {month}index.txt \nParameter{month}: from 05 to 12')
print('\nSample Result for May 2018:')

# a function to wirte items in a list into a txt file seperated by comma
def write_text(file_name, ls):
    with open(file_name,'w') as new_file:
        for item in ls:
            item = str(item)
            new_file.write(item)
            new_file.write(',')

# a function to obtain the average value of some forecast values in a list
def get_avg_forecast(ls):
    count = 0
    total = 0
    for forecast in ls:
        forecast_float = float(forecast)
        count += 1
        total += forecast_float
    if count != 0: return total/count
    else: return None

# a function to obtain the count of very_high or high index in a list
def get_index_count(ls):
    veryhigh_count = 0
    high_count = 0
    for index in ls:
        if index == 'very high':
            veryhigh_count += 1 
        if index == 'high':
            high_count += 1
    return (veryhigh_count, high_count) 

# a function to read the local txt file and store data into a list
def get_data_1_locally(file_name):
    fh = open(file_name, 'r')
    data_ls = []
    pre_data_ls = fh.readline().split(',')
    for data in pre_data_ls:
        if file_name.endswith('forecast.txt'):
            try: data_ls.append(int(data))
            except: pass
        else: 
            try: data_ls.append(data)
            except: pass
    return data_ls

# a function to grab data from source 1 remotely from API
def get_data_1_remotely(date):

    headers = {
      'Accept': 'application/json'
    }

    url = 'https://api.carbonintensity.org.uk/regional/intensity/2018-' + date[0] + 'T00:00Z/2018-' + date[1] + 'T23:59Z/regionid/13'
    r = requests.get(url, params={}, headers = headers)
    data = r.json()

    count = 0 # the count of forecast values
    total = 0 # the total value of every forecast
    high_count = 0 # the forecast times of high index
    veryhigh_count = 0 # the forecast times of veryhigh index
    forecast_ls = []
    index_ls = []

    # e30m means every 30 minutes, the carbon intensity will be given for every half hour
    for e30m in data['data']['data']:
        # get the forecast value for every half hour
        forecast = e30m['intensity']['forecast'] 
        forecast_ls.append(forecast)

        index = e30m['intensity']['index']
        index_ls.append(index)
    
    # check if the file for storing forecast data exist, create a new one if not
    try: open(file_name_forecast,'r')
    except: write_text(file_name_forecast, forecast_ls)
    # check if the file for storing index data exist, create a new one if not
    try: open(file_name_index,'r')
    except: write_text(file_name_index, index_ls)
    
    return (forecast_ls, index_ls)
    
    # the API cannot work too fast so need to sleep for 3 seconds in every loop and more time in every 3 loops
    # however it's not unstable please wait for a short period of time and try again if there is an error
    if int(date[0][0:2]) == 7 : time.sleep(15) 
    elif int(date[0][0:2]) == 10 : time.sleep(20)
    else: time.sleep(3)
    

# the carbon intensity will be obtained monthly, from 2018 May to December
date_ls = [('05-01','05-31','may'), ('06-01','06-30','june'), ('07-01','07-31','july'), ('08-01','08-31','august'), ('09-01','09-30','september'), ('10-01','10-31','october'), ('11-01','11-30','november'), ('12-01','12-31','december')]
carbon_intensity_ls = []

for date in date_ls:
    
    file_name_forecast = date[0][0:2] + 'forecast.txt'  
    file_name_index = date[0][0:2] + 'index.txt'
    
    # if the command is 'remote', get the data from API directly
    if source == 'remote':
        result = get_data_1_remotely(date)
        forecast_ls = result[0]
        index_ls = result[1]

    # if the command is "local", get the data from local files
    elif source == 'local':
        try: 
            open(file_name_forecast,'r')
            open(file_name_index,'r')
        # if the files do not exist, get the data from API and store it at first
        except:
            get_data_1_remotely(date)
        forecast_ls = get_data_1_locally(file_name_forecast)
        index_ls = get_data_1_locally(file_name_index)
    
    # obtain the monthly average forecast, the forecast times of both high index and very high index from functions and store them in a list as a tuple for each month
    carbon_intensity_ls.append((date[2],get_avg_forecast(forecast_ls),get_index_count(index_ls)[0],get_index_count(index_ls)[1]))

# print the sample result for May
print('Average:', carbon_intensity_ls[0][1], ' Very_high index:', carbon_intensity_ls[0][2], 'times   High index:', carbon_intensity_ls[0][3], 'times')




# grab, store and manipulate data from source 2

print('\n\n\n\n*** Outputing Data Source 2 ***')
print('''This data source from API is life quality scores for London including housing, cost of living, startups, venture capital and other 13 scores.
I grab London's scores, which are related to tourism, including the cost of living, travel connectivity, safety, environmental quality, economy and internet access, and store them into a sqlite file.
Then I use these scores to obtain a ranking from the highest score to the lowest score.''')
print('\nAPI Endpoint: \nhttps://api.teleport.org/api/urban_areas/slug:london/scores/')
print('\nAPI Documentation: \nhttps://developers.teleport.org/api/getting_started/#life_quality_ua')
print('\nFile Name: \nlife_quality_scores.sqlite')
print('\nSample Result for Top 3 scores:')

# a function to get data from source 2 remotely from API
def get_data_2_remotely():

    headers = {
      'Accept': 'application/vnd.teleport.v1+json'
    }

    url = 'https://api.teleport.org/api/urban_areas/slug:london/scores/'
    r = requests.get(url, params={}, headers = headers)
    data = r.json()

    score_ls = [] # a list with all scores obtained from API
    score_ls_short = [] # a list with scores that are related to tourism

    # obtain all scores from API
    for score in data['categories']:
        score_ls.append((score['score_out_of_10'],score['name']))

    # selected scores needed
    for i in [1,4,7,10,11,13]:
        score_ls_short.append(score_ls[i])
    
    # check if the data is stored locally, store the data into a sqlite file if not
    try: open('life_quality_scores.sqlite','r')
    except:
        conn = sqlite3.connect('life_quality_scores.sqlite')
        cur = conn.cursor()
        for score in score_ls_short:
            cur.execute('''
                        CREATE TABLE IF NOT EXISTS Life_Quality_Scores
                        (score REAL, title TEXT UNIQUE)''')

            cur.execute('INSERT OR IGNORE INTO Life_Quality_Scores (title,score) VALUES (?, ?)', (score[1],score[0]))

            conn.commit()
    return score_ls_short

# get the data remotely if command is "remote"
if source == 'remote' :
    score_ls_short = get_data_2_remotely()

# get the data locally if command is "local"
elif source == 'local' : 
    try: open('life_quality_scores.sqlite','r')
    # if the local file does not exist, get the data from API and store the data locally before getting local data
    except: get_data_2_remotely()     
    conn = sqlite3.connect('life_quality_scores.sqlite')
    cur = conn.cursor()
    score_ls_short = cur.execute('SELECT * FROM Life_Quality_Scores').fetchall()

# rank the short score list from the highest to the lowest
score_ls_short.sort(reverse=True)

# print the top 3 as sample result
print(score_ls_short[0][1], score_ls_short[0][0])
print(score_ls_short[1][1], score_ls_short[1][0])
print(score_ls_short[2][1], score_ls_short[2][0])




# grab, store and manipulate data from source 3

print('\n\n\n\n*** Outputing Data Source 3 ***')
print('''This data source from a website is the weather information for London in each month in 2019.
I grab the average, high and low temperatures, average sunshine hours, average rainfall, rainfall days from May to December and store them into a splite file.''')
print('\nURL: \nBase URL: https://www.holiday-weather.com/london/averages/{MONTH}/ \nParameter {MONTH}: from "May" to "December" \ne.g. https://www.holiday-weather.com/london/averages/may/')
print('\nFile Name: \nweather.sqlite' )
print('\nSample Result for May 2019:')

# a function to get data from source 3 remotely from a website
def get_data_3_remotely():
    weather_ls = []
    for month in ['may', 'june', 'july', 'august', 'september', 'october', 'november', 'december']:
        # only grab the data of May 2019 for sample output
        url= "https://www.holiday-weather.com/london/averages/" + month + '/'

        # Ignore the HTTP Error 403: Forbidden
        hdr = {'User-Agent': 'Mozilla/5.0'}
        req = Request(url,headers=hdr)

        html = urlopen(req)
        soup = BeautifulSoup(html, 'lxml')

        # only grab the average, high and low temperatures, average sunshine hours, average rainfall, rainfall days in May for sample output
        all_data = soup.find_all('li')
        avg_temp = int(all_data[0].find_all('span')[3].find('span').get_text())
        high_temp = int(all_data[1].find_all('span')[2].find('span').get_text())
        low_temp = int(all_data[2].find_all('span')[2].find('span').get_text())
        sun_hour = int(all_data[3].find_all('span')[2].find('span').get_text())
        rainfall = int(all_data[4].find_all('span')[2].find('span').get_text())
        raindays = int(all_data[5].find_all('span')[2].find('span').get_text())
        weather_ls.append((month, avg_temp, high_temp, low_temp, sun_hour, rainfall, raindays))
    
    # check if the data is stored locally, store the data into a SQL file if not
    try: open('weather.sqlite','r')
    except:
        conn = sqlite3.connect('weather.sqlite')
        cur = conn.cursor()
        for weather in weather_ls:
            cur.execute('''
                        CREATE TABLE IF NOT EXISTS Weather
                        (month TEXT UNIQUE, average_temperature_°C INTEGER, high_temperature_°C INTEGER, low_temperature_°C INTEGER, 
                        sunshine_hours INTEGER, rainfall_mm INTEGER, rainfall_days INTEGER)''')

            cur.execute('INSERT OR IGNORE INTO Weather (month, average_temperature_°C, high_temperature_°C, low_temperature_°C, sunshine_hours, rainfall_mm, rainfall_days) VALUES (?, ?, ?, ?, ?, ?, ?)', (weather[0], weather[1], weather[2], weather[3], weather[4], weather[5], weather[6]))

            conn.commit()
    
    return weather_ls
            
# get the data remotely if command is "remote"
if source == 'remote' :
    weather_ls = get_data_3_remotely()

# get the data locally if command is "local"
elif source == 'local' :
    try: open('weather.sqlite','r')
    # if the local file does not exist, get the data remotely, store the data locally before getting local data
    except: get_data_3_remotely() 
    conn = sqlite3.connect('weather.sqlite')
    cur = conn.cursor()
    weather_ls = cur.execute('SELECT * FROM Weather').fetchall()

# print the sample result for May
print('Average temperature:', weather_ls[0][1], '°C  High temperature:', weather_ls[0][2], '°C  Low temperature:', weather_ls[0][3], '°C')
print('Sunshine hours:', weather_ls[0][4], ' Rainfall:', weather_ls[0][5], 'mm  Rainfall days:', weather_ls[0][6])




# combine all data from 3 sources in one sqlite file

print('\n\n\n\n*** Integrating 3 Sources ***')

conn = sqlite3.connect('weather.sqlite')
cur = conn.cursor()

# create a new table in weather.sqlite named CarbonIntensity to store culculated result from source 1
cur.execute('''
            CREATE TABLE IF NOT EXISTS CarbonIntensity
            (month TEXT UNIQUE, average_carbon_intensity REAL, times_of_veryhigh_index INTEGER, times_of_high_index INTEGER)''')
try:    
    for carbon_intensity in carbon_intensity_ls:
        cur.execute('INSERT INTO CarbonIntensity (month, average_carbon_intensity, times_of_veryhigh_index, times_of_high_index) VALUES (?, ?, ?, ?)', (carbon_intensity[0], carbon_intensity[1], carbon_intensity[2], carbon_intensity[3]))
        conn.commit()
except: pass

# create a new table in weather.sqlite named ScoreRanking to store culculated result from source 2
cur.execute('''
            CREATE TABLE IF NOT EXISTS ScoreRanking
            (title TEXT UNIQUE, score REAL)''')
try:
    for score in score_ls_short:
        cur.execute('INSERT INTO ScoreRanking (title, score) VALUES (?, ?)',(score[1], score[0]))
        conn.commit()
except: pass
print('Integrating 3 sources into "weather.sqlite" completed!')




# combine manipulated data from source 1 and 3 into one dataframe
# also create a dataframe for manipulated data from source 2

print('\n\n\n\n*** Building Dataframes ***')
conn = sqlite3.connect('weather.sqlite')
weather_df = pd.read_sql('''SELECT Weather.month, Weather.average_temperature_°C, Weather.high_temperature_°C, Weather.low_temperature_°C,
                    Weather.sunshine_hours, Weather.rainfall_mm, Weather.rainfall_days,
                    CarbonIntensity.average_carbon_intensity, CarbonIntensity.times_of_veryhigh_index, CarbonIntensity.times_of_high_index
                    FROM Weather JOIN CarbonIntensity ON Weather.month=CarbonIntensity.month''', con=conn)
# make the index start from 5 so each index number can represent the corresponding month
weather_df.index = weather_df.index + 5

score_ranking_df = pd.read_sql('SELECT * FROM ScoreRanking', con=conn)
# make the index start from 1 so each index number can represent the ranking of corresponding score
score_ranking_df.index = score_ranking_df.index + 1

print("A Dataframe of London's Predicted Temperature from May to December in 2019 & Corresponding Carbon Intensity in 2018")
print(weather_df)

print("\nA Dataframe of London's Ranked Life Quality Scores of London")
print(score_ranking_df)




# use temperature and carbon intensity data to plot a graph to predict the trend from May to December in 2018

print('\n\n\n\n*** Plotting A Graph ***')
fig = plt.figure(figsize=(10.0,7.0))
fig.suptitle("A Graph of London's Predicted Temperature from May to December in 2019 & Corresponding Carbon Intensity in 2018", fontsize=15)
ax1 = fig.add_subplot(111)
ax1.plot(weather_df[['high_temperature_°C', 'average_temperature_°C', 'low_temperature_°C']])
ax1.set_ylabel('Temperature(°C)')

ax2 = ax1.twinx()
ax2.plot(weather_df[['average_carbon_intensity']], color='red')
ax2.set_ylabel('Carbon Intensity', color='r')
for tl in ax2.get_yticklabels():
    tl.set_color('r')

ax1.legend(['Predicted High Temperature', 'Predicted Average Temperature', 'Predicted Low Temperature'])
ax2.legend(['Average Carbon Intensity'])
plt.savefig('weather_and_carbon_intensity_graph.png')
plt.show()
print('Plotting a graph completed! \nThe graph is saved as a png file called weather_and_carbon_intensity_graph.png')




# conclusion of results

print('''\n\nConclusion: \nFrom the data frames and graph, we can see that August may have the lowest possibility to have air pollution related to high carbon intensity while December may have the highest possibility. 
Besides, in August, the average temperature will be 19°C, the predicted average sunshine hours (6 hours) will be the second most and the number of rainfall days (13 days) will be the least. 
Therefore, August will be the best month for people to visit London this year for a comfortable environment and weather.
Although 19°C is comfortable enough but it’s still the highest among the average temperatures of all months. People can choose May which average temperature will be 14°C with more rainfall days (15 days), and had the second least carbon intensity last year if they want a cooler trip with higher humidity.
\nRegarding the life quality in London, it has the best Travel Connectivity. The scores of Safety and Internet Access rank the second and the third respectively. Cost of Living has the lowest score.
It can be seen that London is a nice tourism city and safe. Tourists don't need to worry about the internet but they may need more budget to travel in London.
''')