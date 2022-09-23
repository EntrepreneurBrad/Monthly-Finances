# **Monthly Finance Analysis**

## **Video Demo:**
You can view a demo of this project [HERE](https://youtu.be/cn-pkiCH0KI).
<br><br>

## **Description:**
This project allows the user to analyse their financial performance and outputs a infographic.

User's input csv files from their bank account, which are then able to be manually sorted (with automatic recognition of repeated transactions), while also accounting for any extra chores and/or cash.

This information is stored to a database and an infographic is genereated containing:
- A comparision between savings and expenses for the month
- A comparision between each category
- General statistics
- These are compared with the previous month to analyse a positive or negative performance
<br><br>

**Possible Future Feature Additions:**
- Long Term Financial Performance Figure
- More Financial Statistics
<br><br>

## **How It Works:**
1. *python3 main.py [MONTH DIGIT]*
2. The relevant CSV files are checked to be in the folder
3. Each file is read into memory
4. Each row (transaction) of the file is combined to a single list
5. Using the keys provided the transactions are sorted:
    - By the user (manually) --> using input()
    - By the program (automatically) --> using a list of known descriptions
6. The user is asked for any extra money to account for (i.e. cash) --> using input()
7. Using simple math, the opening, closing and change in balance is calculated
8. Each category (i.e. "Work Income") is summed
9. All relevant transactions are added to a database
10. The change in of each financial type from current to previous month is calculated and represented using (▬, ↑, ↓)
11. Using matplotlib, an infographic with many relevant financial details is generated and saved inside the folder as a PNG

<br><br>

## **Usage:**
1. Ensure the relevant CSV files are in the folder
2. *python3 main.py [MONTH DIGIT]* <-- input month digit (i.e. June --> 6)
3. Using the keys provided the user (manually) and program (automatically) sorts each transaction
4. The user is asked for any extra money to account for (i.e. cash)
5. An infographic (PNG) is generated inside the folder

![Example Infographic Image](https://i.ibb.co/1n18Wgd/example.png)

<br><br>

## **Config:**
**Required to install:**
- CSV
- SYS
- Sqlite3
- Matplotlib
- Datetime
<br><br>

**Additional Commands:**
- *$ pip install matplotlib*
<br><br>

## **Credits:**
- Harvard University
    - Introduction to Computer Science ([CS50x](https://www.edx.org/course/introduction-computer-science-harvardx-cs50x)).
    - Introduction to Computer Science with Python ([CS50P](https://www.edx.org/course/cs50s-introduction-to-programming-with-python)).
    - David Malan (Lecturer)
<br><br>
- *[w3schools](https://www.w3schools.com)* documentation
- *[matplotlib](https://matplotlib.org)* documentation
<br><br>

## **License:**
*MIT License*

*Copyright (c) [2022] [EntrepreneurBrad]*

*Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:*

*The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.*

*THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.*