import csv, sys, sqlite3
import matplotlib.pyplot as plt
from datetime import date

year = date.today().year  # assumes current year

# Number of simluations to run
debit_transactions = []
savings_transactions = []

transaction_keys_expense = {
    "Mountain Biking": "mt",
    "Tennis": "tn",
    "Technology": "tc",
    "Food/Social Gatherings": "fo",
    "Community Donations": "do",
    "Miscellaneous Expenses": "me",
    "Covered by Parents": "cp"
}

list_of_expense_keys = []

for dict_title in transaction_keys_expense: # means the user does not have to change both the list and the dict if they want to make a change
    list_of_expense_keys.append(dict_title)

transaction_keys_income = {
    "Chores Income": "ch",
    "Work Income": "wo",
    "YouTube Income": "yt",
    "Gift Income": "gf",
    "Miscellaneous Income": "mi",
    "Interest": "in",
    "Cash": "ca"
}

list_of_income_keys = []

for dict_title in transaction_keys_income: # means the user does not have to change both the list and the dict if they want to make a change
    list_of_income_keys.append(dict_title)


known_descriptions = {
    "Interest Credit": "in",
    "Just Ride Nerang AU": "mt",
} # a list to add frequent descriptions to allow recognition of the transfers and their key without asking the user (i.e. interest)



def main():

    month = month_checks()

    debit_file_name = "SavingAccount-0833_2022-" + month + ".csv"
    savings_file_name = "DebitCardAccount-0832_2022-" + month + ".csv"

    read_csv(debit_file_name, savings_file_name) # Reading into memory from file

    all_transactions = debit_transactions + savings_transactions  # combines into single list

    a = sort_transactions(all_transactions)  # asks the user to sort through the transactions
    sorted_trans_list = a[0]
    chores_cash_sum = a[1]

    opening_balance = calculate_opening_balance()

    closing_balance = calculate_closing_balance(chores_cash_sum)

    change_in_balance = calculate_change_in_balance(opening_balance, closing_balance)

    category_sums = calculate_category_sum(list_of_income_keys, sorted_trans_list)

    d = database(month, year, category_sums, change_in_balance, opening_balance, closing_balance) #adds to db for future features
    difference_between_months = d[0]
    identifiers = d[1]
    is_prev_month = d[2]

    image_output(month, category_sums, change_in_balance, opening_balance, closing_balance, year, difference_between_months, identifiers, is_prev_month) # uses matplotlib for plotting



def month_checks(): # ensures month is in correct format
    # Ensure correct usage
    if len(sys.argv) != 2:
        sys.exit("Usage: python main.py MONTH-DIGIT")

    month = int(sys.argv[1])

    if month < 10:
        month = str(0) + str(month) # for the file format it must be in '05' instead of '5'

    return month


def read_csv(debit_file_name, savings_file_name):  # reads the csv files (one being the savings acc, the other the debit card)
    try:
        with open(debit_file_name, "r") as file: # opens each file and reads it into memory
            transactions = csv.DictReader(file)
            for debit_transaction in transactions:
                debit_transactions.append(debit_transaction)

        with open(savings_file_name, "r") as file:
            transactions = csv.DictReader(file)
            for savings_transaction in transactions:
                savings_transactions.append(savings_transaction)
    except FileNotFoundError:
        sys.exit("File not found!")

    return


def sort_transactions(transaction_list):  # allows the user to sort into categories
    print("")
    print("Please Sort the Following Transactions according to these keys: \n")
    
    print("Expenses:")
    for i in range(len(list_of_expense_keys)): # lists all of the income keys the user can use
        print("   " + transaction_keys_expense[list_of_expense_keys[i]].upper() + " : " + list_of_expense_keys[i])
    
    print("")
    print("Income:")
    for y in range(len(list_of_income_keys)): # lists all of the expense keys the user can use
        if list_of_income_keys[y] != "Cash" and list_of_income_keys[y] != "Interest":
            print("   " + transaction_keys_income[list_of_income_keys[y]].upper() + " : " + list_of_income_keys[y])

    print("")

    for i in range(len(transaction_list)): # for each item in the list
        expense = False  # allows for the correct sorting types
        date = transaction_list[i]["Date"].replace(" 2022", "")
        description = transaction_list[i]["Description"]

        if description == "Transfer": # ignore transfers as they show on both credit and debit for 2 accounts
            transaction_list[i].update({"Key":"Transfer"}) 

        elif description in known_descriptions: # this uses a known descriptions list to recognise transfers and their key without asking the user (i.e. interest)
            transaction_list[i].update({"Key":known_descriptions[description]}) 
            
        else:
            if transaction_list[i]["Credit"] != "": # prints each of the list items for the user
                current_transaction = date + ": +" + transaction_list[i]["Credit"] + " @ " + description
            else:  # therfore a debit
                expense = True
                current_transaction = date + ": -" + transaction_list[i]["Debit"] + " @ " + description

            print("")

            while True:  # verifies if a valid answer
                userInput = valid_key(current_transaction, expense) # asks the user to confirm the key
            
                if userInput != 0:
                    break

            transaction_list[i].update({"Key":userInput}) # once confirmed this transaction can be identified by the key


    # incorporating any chores from the excel sheet
    chores_amount = chores()
    transaction_list.append( {'Date': '', 'Description': 'Chores', 'Debit': '',
    'Credit': chores_amount, 'Balance': '', 'Key': 'ch'})  

    cash_amount = cash()

    # incorporating any cash from the excel sheet
    transaction_list.append( {'Date': '', 'Description': 'Cash', 'Debit': '',
    'Credit': cash_amount, 'Balance': '', 'Key': 'ca'}) 


    return transaction_list, chores_amount+cash_amount
    

def valid_key(current_transaction, expense):  # determines if the user input from sort_transactions is valid
    userInput = (input(current_transaction + ": ")).lower()

    if expense == True:  # must be an expense key option
        for i in range(len(list_of_expense_keys)):
            if userInput == transaction_keys_expense[list_of_expense_keys[i]]:
                return userInput
            
    else:  # must be an income key option
        for j in range(len(list_of_income_keys)):
            if userInput == transaction_keys_income[list_of_income_keys[j]]:
                return userInput

    return 0


def calculate_category_sum(list_of_income_keys, sorted_trans_list):  # calculates the total monetary sum for each category
    category_list = [] 
    sum_of_category_sums_list = []
    sum_of_category_sums = 0

    num_of_income_keys = len(list_of_income_keys)  # useful to sort through list at to differeniate between the two groups
    category_list.append(num_of_income_keys)

    for i in range(num_of_income_keys):
        category_sum = 0

        for j in range(len(sorted_trans_list)): # goes through each key type
            if sorted_trans_list[j]['Key'] == transaction_keys_income[list_of_income_keys[i]]: # goes through each transaction and adds them to category
                category_sum += money_to_float(sorted_trans_list[j]["Credit"])
        
        category_list.append([list_of_income_keys[i], round(category_sum, 2)])
        sum_of_category_sums += round(category_sum, 2)

    sum_of_category_sums_list.append(["Income", round(sum_of_category_sums, 2)]) # adds all income categories to the total income
            

    sum_of_category_sums = 0

    for j in range(len(list_of_expense_keys)):
        category_sum = 0

        for z in range(len(sorted_trans_list)): # goes through each key type
            if sorted_trans_list[z]['Key'] == transaction_keys_expense[list_of_expense_keys[j]]: # goes through each transaction and adds them to category
                category_sum += money_to_float(sorted_trans_list[z]["Debit"])

        category_list.append([list_of_expense_keys[j], round(category_sum, 2)])
        sum_of_category_sums += round(category_sum, 2)

    sum_of_category_sums_list.append(["Expenses", round(sum_of_category_sums, 2)])  # adds all income categories to the total income

    final_list = sum_of_category_sums_list + category_list # combines the income and expense amounts with all the rest of the categories

    return final_list     
   

def cash(): # asks the user for the total cash for the month
    print("")
    while True:
        cash = input("What is the Value of the Cash/Coins this Month? $")
        try:
            float(cash)  # ensures it is a float
            break
        except:
            pass
    print("")
    return cash


def chores(): # asks the user for the total chore money for the month
    print("\n")
    while True:
        print("")
        chores = input("What is the Value of the Chores this Month? $")
        try:
            float(chores) # ensures it is a float
            break
        except:
            pass
    return chores


def calculate_opening_balance(): # calculates the opening balance for the month
    #Savings Acc Inital Row Balance +- 1st Row) + (Debit Card Acc Inital Row Balance +- 1st Row
    savings_balance = money_to_float(savings_transactions[0]["Balance"]) - money_to_float(savings_transactions[0]["Credit"]) + money_to_float(savings_transactions[0]["Debit"])
    debit_balance = money_to_float(debit_transactions[0]["Balance"]) - money_to_float(debit_transactions[0]["Credit"]) + money_to_float(debit_transactions[0]["Debit"])
    return round(savings_balance + debit_balance, 2)


def calculate_closing_balance(chores_cash_sum): # calculates the closing balance for the month
    #Savings Acc Final Row Balance + Debit Card Acc Final Row Balance + any cash or chores for the month
    balance = money_to_float(savings_transactions[-1]["Balance"]) + money_to_float(debit_transactions[-1]["Balance"] + chores_cash_sum)
    return round(balance, 2)


def calculate_change_in_balance(opening_balance, closing_balance): # calculates the change in balance for the month
    #Opening - Closing
    balance = closing_balance - opening_balance
    return round(balance, 2)


def database(month, year, category_sums, change_in_balance, opening_balance, closing_balance, is_prev_month): # adds the monthly performance to the database for future features

    def connect_db():  # ensure the db is always connected
        return sqlite3.connect("finances.db")


    CREATE_MONTH_TABLE = """CREATE TABLE months (
                    id INTEGER PRIMARY KEY,
                    month TEXT,
                    Year INT,
                    Income FLOAT,
                    Expenses FLOAT, 
                    Chores_Income FLOAT,
                    Work_Income FLOAT,
                    YouTube_Income FLOAT,
                    Gift_Income FLOAT,
                    Miscellaneous_Income FLOAT,
                    Interest FLOAT,
                    Cash FLOAT,
                    Mountain_Biking FLOAT,
                    Tennis FLOAT,
                    Technology FLOAT,
                    Food_Social_Gatherings FLOAT,
                    Community_Donations FLOAT,
                    Miscellaneous_Expenses FLOAT,
                    Covered_by_Parents FLOAT,
                    Change_Balance FLOAT,
                    Opening_Balance FLOAT,
                    Closing_Balance FLOAT
                    );"""

    def create_tables(connection):  # creates the inital table using the above sql code
        with connection:
            connection.execute(CREATE_MONTH_TABLE)


    INSERT_MONTH = """INSERT INTO months
                    (month, Year, Income, Expenses, Chores_Income, Work_Income,
                    YouTube_Income, Gift_Income, Miscellaneous_Income, Interest, Cash,
                    Mountain_Biking, Tennis, Technology, Food_Social_Gatherings,
                    Community_Donations, Miscellaneous_Expenses, Covered_by_Parents,
                    Change_Balance, Opening_Balance, Closing_Balance)
                    
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);"""


    values = (month, year, category_sums[0][1], category_sums[1][1], category_sums[3][1],
                    category_sums[4][1], category_sums[5][1], category_sums[6][1], category_sums[7][1],
                    category_sums[8][1], category_sums[9][1], category_sums[10][1], category_sums[11][1],
                    category_sums[12][1], category_sums[13][1], category_sums[14][1], category_sums[15][1],
                    category_sums[16][1], change_in_balance, opening_balance, closing_balance)

    def add_month(connection, values): # creates a new month to be added to the table using the values above
        with connection:
            connection.execute(INSERT_MONTH, values)


    DELETE_MONTH = """DELETE FROM months WHERE month = ? AND Year = ?;"""
    
    def delete_month(connection, month, year): # creates a new month to be added to the table using the values above
        connection.execute(DELETE_MONTH, (month, year))

    
    SEARCH = "SELECT * FROM months WHERE year = ? AND month = ? ORDER BY id DESC LIMIT 1;"

    def search(connection, month):  # search and returns values that satisfy the search conditions
        with connection:
            answers = connection.execute(SEARCH, (year, month))
        
            for i in answers:
                return i


    connection = connect_db()

    #create_tables(connection)  # only required initally
    delete_month(connection, values[0], values[1]) # any prev month accounts are deleted

    add_month(connection, values)  # occurs each time the code is run
    
    search(connection, month) # occurs each time the code is run


    def difference_between_months(month):  # calculates the difference of each category for the prev and current month
        is_prev_month = False

        prev_month = int(month) - 1  # we also need to find the details from the previous month

        if prev_month < 10:
            prev_month = "0" + str(prev_month)

        current_month_details = search(connection, month) # runs for this month

        prev_month_details = search(connection, prev_month) # runs for prev month

        if prev_month_details != None:
            is_prev_month = True

        difference_between_months = []

        try:
            for i in range(len(current_month_details)):  # subracts each item in the months
                if i >= 3:  # ignore month and year and id
                    difference_between_months.append(round(float(current_month_details[i]) - float(prev_month_details[i]), 2))
        except:
            difference_between_months.append("")


        identifiers = []
        # the following code is to sort the positives, negatives and neturals
        for i in range(len(difference_between_months)):
            try:
                if difference_between_months[i] == 0:
                    identifiers.append("▬")
                    difference_between_months[i] = ""

                elif difference_between_months[i] > 0: # pos num
                    identifiers.append("↑$")
                    difference_between_months[i] = float_to_2sf(difference_between_months[i])

                elif difference_between_months[i] < 0: # neg num
                    identifiers.append("↓$")
                    difference_between_months[i] = float_to_2sf(abs(difference_between_months[i]))
            except:
                identifiers.append("")
        
        return difference_between_months, identifiers, is_prev_month


    return difference_between_months(month)


def money_to_float(value): # converts the money values to floats
    try:
        new_value = float(value.strip("$").replace(",", ""))
    except ValueError:
        new_value = 0

    return new_value


def float_to_money(value): # converts the float_to_money
    return ("$" + "{:,.2f}".format(value))


def float_to_2sf(value): # converts the float_to_money
    return ("{:,.2f}".format(value))


def image_output(month, category_sums, change_in_balance, opening_balance, closing_balance, year, difference_between_months, identifiers, is_prev_month): # uses matplotlib to plot the financial performance
    figure, axis = plt.subplots(1,2)  # creates a image with 2 figures

    months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    month = months[int(month) - 1]

    for i in range(len(category_sums)):  # finding amount covered by parents so that we can subtract from the expenses for the pie chart
        try:
            if "Covered by Parents" in category_sums[i]:
                parents_row = category_sums[i]
                owed_by_parents = parents_row[1]

        except:
            pass


    # Pie chart for Savings VS Expenses Comparision
    if is_prev_month == True:  # if there is a prev month
        labels = ('\nSavings: ' + float_to_money(category_sums[0][1])  + "\n (" + identifiers[0]
        + difference_between_months[0] + ")", 'Expenses: ' + str(float_to_money(category_sums[1][1]
        - owed_by_parents)) + "\n (" + identifiers[1] + difference_between_months[1] + ")")
    else:
        labels = ('Savings: ' + float_to_money(category_sums[0][1]), 'Expenses: ' + str(float_to_money(category_sums[1][1]
        - owed_by_parents)))

    values = [category_sums[0][1], category_sums[1][1] - owed_by_parents]

    axis[0].pie(values, explode=(0, 0), labels=labels, startangle=90, colors=['#2D95AE', '#EDAF2D'], textprops={"fontsize":15}, autopct='%1.1f%%')


    # Bar chart
    values = []
    labels = []

    #Savings
    num_of_income_keys = int(category_sums[2])

    for value in range(num_of_income_keys):
        current_pos = int(value + 3)
        values.append(category_sums[current_pos][1]) # adds the values of each income type to the values list
        labels.append(category_sums[current_pos][0]) # adds the labels of each income type to the values list

    colors = []

    for i in range(len(values)):
        if float(values[int(i)]) == float(max(values)):
            colors.append('#4CAE2D')  # i is the location of the largest value so we want to emphasise this
        else:
            colors.append('#79E956')  # normal color



    new_identifiers = identifiers[2:]  # we need to remove the month, year, opening balance etc
    new_difference_between_months = difference_between_months[2:]


    #Expenses
    expense_values = []
    num_of_expense_keys = len(category_sums) - num_of_income_keys - 3

    for value in range(num_of_expense_keys):  # removes parents
        current_pos = int(num_of_income_keys + 3 + value)
        if category_sums[current_pos][0] != "Covered by Parents":
            expense_values.append(category_sums[current_pos][1]) # adds the values of each expense type to the values list
            labels.append(category_sums[current_pos][0]) # adds the labels of each expense type to the values list


    for i in range(num_of_expense_keys - 1):
        if float(expense_values[int(i)]) == float(max(expense_values)):
            colors.append('#B52828')  # i is the location of the largest value so we want to emphasise this
        else:
            colors.append('#E16868')  # normal color

    values += expense_values  # after finding the highest expense we can combine the two lists together

    axis_formatting = axis[1].bar(labels, values, label=labels, color=colors) # formatting
    axis[1].set_ylabel('Value ($)')
    axis[1].set_title('Comparison of Expense & Income Streams for ' + str(month) + " " + str(year), fontweight='bold')
    axis[1].tick_params(axis='x', rotation=90)
    axis[1].set_ylim([0, float(max(values))+50])
    
    # creation of chart
    formatted_values = []  # adding labels of each bar
    for i in range(len(values)):
        if is_prev_month == True:
            formatted_values.append(float_to_money(values[i]) + "\n (" + new_identifiers[i] + new_difference_between_months[i] + ")")
        else:
            formatted_values.append(float_to_money(values[i]))
            
    axis[1].bar_label(axis_formatting, labels = formatted_values, fontsize=7, linespacing=1.5, padding=3.5) # formatting


    #Using text to add other important info
    axis[0].text(1,-1.9,"Owed by Parents: " + float_to_money(owed_by_parents), fontsize=15, fontweight='bold', horizontalalignment='center')

    if change_in_balance < 0: # formatting for if change is positive or negative
        axis[0].text(-.5,-1.6,"Change in Balance: -" + float_to_money(abs(change_in_balance)), fontsize=15, fontweight='bold', horizontalalignment='center', color="red")
        axis[0].text(1,-1.6,"Growth: " + str(round(((change_in_balance/opening_balance)*100), 2)) + "%", fontsize=15, fontweight='bold', horizontalalignment='center', color="red")
    else:
        axis[0].text(-.5,-1.6,"Change in Balance: " + float_to_money(change_in_balance), fontsize=15, fontweight='bold', horizontalalignment='center', color="green")
        axis[0].text(1,-1.6,"Growth: " + str(round(((change_in_balance/opening_balance)*100), 2)) + "%", fontsize=15, fontweight='bold', horizontalalignment='center', color="green")
     
    axis[0].text(-.8,-1.9,"Current Balance: " + float_to_money(closing_balance+owed_by_parents), fontsize=15, fontweight='bold', horizontalalignment='center')
    

    # Creation of final image
    figure.set_size_inches(18, 7)
    figure.tight_layout()
    figure.savefig(str(month) + "-" + str(year) + "-" + "financial_analysis.png", dpi=200)

if __name__ == "__main__":
    main()