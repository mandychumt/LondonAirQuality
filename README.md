# LondonAirQuality

Introduction:

This project scraps weather information from a tourist website, retrieves carbon intensity data from a National Grid’s API and life quality data from a Teleport API of London. By using this data, this project aims to help people, who are planning to visit London, predict the air quality and weather in the future months.

1. How to run your code?

When running the project file "London.py", there is a “local” or “remote” command line parameter. When invoked, my code would grab the data either locally or remotely.

If “remote” is entered, my code would grab data from three data sources remotely from two APIs and one website, show some description and sample results of each source respectively. At the same time, my code would store them into text and SQL files if these files don’t exist.

If “local” is entered, my code would grab data from the local text and SQL files, show some description and sample results. My code would grab data remotely and store them at first if these files don’t exist. 

After grabbing the data, either remotely or locally, my code would manipulate the data and combine then into a SQL file with three tables. Two data frames would be built and printed by using these tables. By selecting some data from one of the data frames, a graph would also be created, stored and printed. Finally, a conclusion would be printed.


2. Any major “gotchas” to the code?

The speed to grab data from the first API (carbon intensity in London) is low. If the code goes too fast, the API would go wrong. The way I solve this problem is using the sleep method to let the code stop for several seconds in each loop. I selected the sleep time just according to my feeling and several tests by using different numbers. There may be a better method to obtain the exact speed the API can run and calculate how long the code should wait between each API call. In this way, the code may be running in a higher efficiency.

In addition, grabbing data from the website (weather information in London) is also slow. However, it doesn’t give an error to the code. One way to improve this problem may be finding another weather website that runs more quickly. 

Regarding the data model, it will be better if the two data frames can be combined into one data frame in some ways. It will make my model clearer and easier to understand. 


3. Anything else you feel is relevant to your project.

Please use “pythonw” instead of “python” if there is an ImportError in the line “import matplotlib.pyplot as plt”
