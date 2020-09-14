import random
import sqlite3

# Connect to database
conn = sqlite3.connect('card.s3db')
c = conn.cursor()

# Create table if it doesn't exist
c.execute('''CREATE TABLE IF NOT EXISTS card
              (id INTEGER PRIMARY KEY AUTOINCREMENT, 
               number TEXT, pin TEXT, balance INTEGER)'''
          )


class BankAccount:
    BIN = 400000

    def __init__(self):
        self.id = random.randrange(100000000, 1000000000)
        self.card_number = BankAccount.generate_card_num(self)
        while BankAccount.is_existing_card(self):
            self.card_number = BankAccount.generate_card_num(self)
        self.pin_code = str(random.randrange(1000, 10000))
        self.balance = 0

    def generate_card_num(self):
        number_15_digit = str(BankAccount.BIN) + str(self.id)
        total = 0
        num_list = [int(x) for x in number_15_digit]
        for i, digits in enumerate(num_list):
            if i % 2 == 0:
                num_list[i] *= 2
        for i, digits in enumerate(num_list):
            if num_list[i] > 9:
                num_list[i] -= 9
        for i, digits in enumerate(num_list):
            total += num_list[i]
        check_sum = (10 - (total % 10)) % 10
        return str(number_15_digit) + str(check_sum)

    @staticmethod
    def luhn_algorithm(card):
        num_list = [int(x) for x in card]
        total = 0
        for i, digits in enumerate(num_list):
            if i % 2 == 0:
                num_list[i] *= 2
        for i, digits in enumerate(num_list):
            if num_list[i] > 9:
                num_list[i] -= 9
        for i, digits in enumerate(num_list):
            total += num_list[i]
        return total % 10 == 0

    def add_data(self):
        c.execute(
            "INSERT INTO card (id, number, pin, balance)"
            "VALUES (?, ?, ?, ?)",
            (self.id, self.card_number, self.pin_code, self.balance)
        )
        conn.commit()

    def is_existing_card(self):
        c.execute("SELECT number "
                  "FROM card "
                  "WHERE number=?",
                  (self.card_number,)
                  )
        res = c.fetchone()
        return res is not None

    @staticmethod
    def display_menu():
        print("1. Create an account")
        print("2. Log into account")
        print("0. Exit")

    @staticmethod
    def log_in_menu():
        print("1. Balance")
        print("2. Add income")
        print("3. Do transfer")
        print("4. Close account")
        print("5. Log out")
        print("0. Exit")

    @staticmethod
    def create_an_acct():
        new_acct = BankAccount()
        BankAccount.add_data(new_acct)
        print("\n" + "Your card has been created")
        print("Your card number:" + "\n" + str(new_acct.card_number))
        print("Your card pin:" + "\n" + str(new_acct.pin_code) + "\n")

    @staticmethod
    def log_into_acct():
        user_num = input(str("\n" + "Enter your card number:" + "\n"))
        user_pin = input("Enter your PIN:" + "\n")
        c.execute("SELECT * FROM card WHERE number=?", (user_num,))
        res = c.fetchone()
        if res is not None:
            db_pin = int(res[2])
        else:
            db_pin = -1
        if int(user_pin) == db_pin:
            print("\n" + "You have successfully logged in!" + "\n")
            while True:
                BankAccount.log_in_menu()
                user_input = int(input())
                if user_input == 1:
                    c.execute("SELECT balance "
                              "FROM card "
                              "WHERE number=?",
                              (user_num,)
                              )
                    balance = c.fetchone()
                    print("\n" + "Balance: " + str(balance[0]) + "\n")
                if user_input == 2:
                    add_balance = input("\n" + "Enter income: " + "\n")
                    c.execute("UPDATE card "
                              "SET balance=balance+? "
                              "WHERE number=?",
                              (add_balance, user_num,)
                              )
                    conn.commit()
                    print("Income was added!" + "\n")
                if user_input == 3:
                    print("\n" + "Transfer")
                    transfer_acct = input("Enter card number: " + "\n")
                    if BankAccount.luhn_algorithm(transfer_acct):
                        c.execute("SELECT number "
                                  "FROM card "
                                  "WHERE number=?",
                                  (transfer_acct,)
                                  )
                        res = c.fetchone()
                        if res is not None:
                            if res[0] == user_num:
                                print("You can't transfer money to the same account!" + "\n")
                            else:
                                transfer_amount = input("Enter how much money you want to transfer: ")
                                c.execute("SELECT balance "
                                          "FROM card "
                                          "WHERE number=?",
                                          (user_num,)
                                          )
                                user_balance = c.fetchone()
                                if int(user_balance[0]) >= int(transfer_amount):
                                    c.execute("UPDATE card "
                                              "SET balance=balance-? "
                                              "WHERE number=?",
                                              (transfer_amount, user_num,)
                                              )
                                    conn.commit()
                                    c.execute("UPDATE card "
                                              "SET balance=balance+? "
                                              "WHERE number=?",
                                              (transfer_amount, transfer_acct,)
                                              )
                                    conn.commit()
                                    print("Success!" + "\n")
                                else:
                                    print("Not enough money!" + "\n")
                        else:
                            print("Such a card does not exist.")
                    else:
                        print("Probably you made a mistake in the card number. Please try again!")
                if user_input == 4:
                    c.execute("DELETE FROM card "
                              "WHERE number=?",
                              (user_num,)
                              )
                    conn.commit()
                    print("\n" + "The account has been closed!" + "\n")
                    break
                if user_input == 5:
                    print("\n" + "You have successfully logged out!" + "\n")
                    break
                if user_input == 0:
                    BankAccount.exit_menu()
        else:
            print("\n" + "Wrong number or PIN!" + "\n")

    @staticmethod
    def exit_menu():
        print("\n" + "Bye!")
        conn.close()
        quit()


# Main loop
while True:
    BankAccount.display_menu()
    display_menu_choice = int(input())
    if display_menu_choice == 1:
        BankAccount.create_an_acct()
    elif display_menu_choice == 2:
        BankAccount.log_into_acct()
    elif display_menu_choice == 0:
        BankAccount.exit_menu()
