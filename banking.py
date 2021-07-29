from random import randint
import sqlite3

conn = sqlite3.connect('card.s3db')
cur = conn.cursor()
cur.execute('''
CREATE TABLE IF NOT EXISTS card( 
    id INTEGER, 
    number TEXT, 
    pin TEXT, 
    balance INTEGER DEFAULT 0
);''')
conn.commit()


def entrance_menu():
    print("1. Create an account",
          "2. Log into account",
          "0. Exit", sep='\n')
    user_input = input()
    if user_input == '1':
        user.create_account()
    elif user_input == '2':
        user.login()
    elif user_input == '0':
        print('Bye!')
        exit()
    else:
        print('Invalid input')


def get_checksum(card):
    luhn = [int(x) for x in card]
    for i, num in enumerate(luhn):
        if (i + 1) % 2 == 0:
            continue
        temp = num * 2
        luhn[i] = temp if temp < 10 else temp - 9
    checksum = 10 - sum(luhn) % 10
    if checksum < 10:
        return str(checksum)
    else:
        return '0'


class User:

    def __init__(self):
        self.issuer_num = '400000'  # Issuer Identification Number (IIN)
        self.card_num = None
        self.customer_num = None

    def login(self):
        while True:
            card_input = input('Enter your card number:\n')
            pin_input = input('Enter your PIN:\n')

            cur.execute(f"""SELECT number, pin  FROM card 
                            WHERE number = {card_input} AND pin = {pin_input}""")
            res = cur.fetchone()
            if res:
                print('You have successfully logged in!')
                self.card_num = card_input
                user.main_menu()
                break
            else:
                print('Wrong card number or PIN!')
                entrance_menu()
                break

    def main_menu(self):
        while True:
            print("1. Balance", "2. Add income", "3. Do transfer",
                  "4. Close account", "5. Log out", "0. Exit ", sep='\n')
            user_input = input()
            if user_input == '1':
                cur.execute(f"""SELECT balance FROM card 
                                WHERE number = '{self.card_num}'""")
                print(cur.fetchone()[0])
            elif user_input == '2':
                try:
                    income = int(input('Enter income: '))
                    cur.execute(f'SELECT balance FROM card WHERE number = {self.card_num}')
                    cur.execute(f"""UPDATE card SET balance = balance + {income} 
                                    WHERE number = '{self.card_num}'""")
                except ValueError:
                    print('Invalid input')
                conn.commit()
                print('Income was added!')
            elif user_input == '3':
                print('Transfer', 'Enter card number:', sep='\n')
                receiver_card = input()
                if get_checksum(receiver_card[:15]) == receiver_card[-1]:
                    cur.execute(f'SELECT number FROM card WHERE number = {receiver_card}')
                    res = cur.fetchone()
                    if res:
                        if self.card_num != receiver_card:
                            try:
                                transfer_amount = int(input('Enter how much money you want to transfer: '))
                            except ValueError:
                                print('Invalid input')
                            cur.execute(
                                f"""SELECT balance FROM card 
                                    WHERE number = '{self.card_num}'AND balance >= {transfer_amount}""")
                            res = cur.fetchone()
                            if res:
                                cur.execute(f"""SELECT balance FROM card 
                                                WHERE number = '{self.card_num}';""")
                                cur.execute(f"""UPDATE card SET balance = balance - {transfer_amount} 
                                                WHERE number = '{self.card_num}'""")
                                cur.execute(f"""SELECT balance FROM card WHERE number = {receiver_card};""")
                                cur.execute(f"""UPDATE card SET balance = balance + {transfer_amount} 
                                                WHERE number = {receiver_card}""")
                                conn.commit()
                                print('Success!')
                            else:
                                print('Not enough money!')
                        else:
                            print("You can't transfer money to the same account!")
                    else:
                        print('Such a card does not exist.')
                else:
                    print('Probably you made a mistake in the card number. Please try again!')
            elif user_input == '4':
                cur.execute(f"DELETE FROM card WHERE number = '{self.card_num}'")
                conn.commit()
                print('The account has been closed!')
                entrance_menu()
                break
            elif user_input == '5':
                print('You have successfully logged out!')
                entrance_menu()
                break
            elif user_input == '0':
                print('Bye!')
                exit()

    def create_account(self):
        self.customer_num = str(randint(10 ** 8, 10 ** 9 - 1))
        card_num = self.issuer_num + self.customer_num + \
                   get_checksum(self.issuer_num + self.customer_num)
        pin_code = str(randint(1000, 10000))
        print(f"Your card has been created!\n"
              f"Your card number:\n"
              f"{card_num}\n"
              f"Your card PIN:\n"
              f"{pin_code}\n")

        cur.execute(f"""INSERT INTO card (number, pin) 
                        VALUES ('{card_num}', '{pin_code}')""")
        conn.commit()
        entrance_menu()


user = User()
entrance_menu()
