import sqlite3
import random
import sys


connection = sqlite3.connect('card.s3db')
cursor = connection.cursor()

with connection:
    cursor.execute('CREATE TABLE IF NOT EXISTS card ( id INTEGER, number TEXT, pin TEXT, balance INTEGER DEFAULT 0)')


class Bank:
    users_passwords = {}
    n_clients = 0

    def __init__(self):
        self.start()

    def printMainMenu(self):
        print('1. Create an account')
        print('2. Log into account')
        print('0. Exit')

    def start(self):
        while True:
            self.printMainMenu()
            self.action(input())

    def action(self, input1):
        if input1 == '1':
            self.createAccount()
        elif input1 == '2':
            self.logIn()
        elif input1 == '0':
            print('Bye')
            sys.exit()

    def calculateLuhnDigit(self, strInteger1):
        sum = 0
        for i in range(len(strInteger1)):
            if i % 2 == 0:
                if (int(strInteger1[i]) * 2) > 9:
                    sum += (int(strInteger1[i]) * 2) - 9
                else:
                    sum += (int(strInteger1[i]) * 2)
            else:
                sum += int(strInteger1[i])
        if sum % 10 == 0:
            return 0
        else:
            return 10 - (sum % 10)

    def checkIfLuhn(self, strInteger2):
        sum = 0
        for i in range(len(strInteger2)):
            if i % 2 == 0:
                if (int(strInteger2[i]) * 2) > 9:
                    sum += (int(strInteger2[i]) * 2) - 9
                else:
                    sum += (int(strInteger2[i]) * 2)
            else:
                sum += int(strInteger2[i])
        return sum % 10 == 0

    def createAccount(self):
        print()
        print('Your card has been created')
        number = random.randint(0, 999999999)
        number = str(number).zfill(9)
        last_digit = str(self.calculateLuhnDigit('400000' + number))
        number = int('400000' + number + last_digit)
        print('Your card number:')
        print(number)
        pin = random.randint(0, 9999)
        pin = str(pin).zfill(4)
        print('Your card PIN:')
        print(pin)
        print()
        params = (self.n_clients + 1, number, pin, 0)
        with connection:
            cursor.execute('INSERT INTO card VALUES (?, ?, ?, ?)', params)
        self.n_clients += 1

    def logIn(self):
        print()
        num_entered = int(input('Enter your card number:'))
        str_entered = str(num_entered)
        pin_entered = input('Enter your PIN:')
        print()
        if self.checkIfLuhn(str_entered):
            with connection:
                cursor.execute('SELECT * from card WHERE (number=? AND pin=?)', (str_entered, pin_entered))
                if cursor.fetchone() is None:
                    print('Wrong card number or PIN!')
                else:
                    print('You have successfully logged in!')
                    self.logAction(str_entered)
        else:
            print('Wrong card number or PIN!')

    def printLogMenu(self):
        print('1. Balance')
        print('2. Add income')
        print('3. Do transfer')
        print('4. Close account')
        print('5. Log out')
        print('0. Exit')

    def logAction(self, client_num):
        while True:
            self.printLogMenu()
            self.logDo(input(), client_num)

    def logDo(self, input_, client_num):
        client_num = int(client_num)
        if input_ == '1':
            with connection:
                cursor.execute('SELECT balance FROM card WHERE number=?', (client_num,))
                bal = cursor.fetchone()
            print('Balance: ', bal)
        elif input_ == '2':
            money_to_add = input('Enter income:')
            with connection:
                cursor.execute('UPDATE card SET balance = balance+(?) WHERE (number=?)', (money_to_add, client_num))
            print('Income was added!')
        elif input_ == '3':
            print('Transfer')
            num_to_send = input('Enter card number:')
            if self.checkIfLuhn(str(num_to_send)):
                if num_to_send[0] != '4':
                    print('Such a card does not exist.')
                    return
                else:
                    with connection:
                        cursor.execute('SELECT * from card WHERE (number=?)', (client_num,))
                        if cursor.fetchone() is None:
                            print('Such a card does not exist.')
                            return
                        else:
                            if num_to_send == client_num:
                                print("You can't transfer money to the same account!")
                                return
                            else:
                                money_to_transfer = int(input("Enter how much money you want to transfer:"))
                                with connection:
                                    cursor.execute('SELECT balance FROM card WHERE (number=?)', (client_num,))
                                    bal_now = cursor.fetchone()
                                if money_to_transfer > bal_now[0]:
                                    print('Not enough money!')
                                    return
                                else:
                                    with connection:
                                        cursor.execute('UPDATE card SET balance = balance-(?) WHERE (number=?)', (money_to_transfer, client_num))
                                        cursor.execute('UPDATE card SET balance = balance+(?) WHERE (number=?)', (money_to_transfer, num_to_send))
                                    print("Success!")
            else:
                print('Probably you made mistake in the card number. Please try again!')
                print()
        elif input_ == '4':
            with connection:
                cursor.execute('DELETE FROM card WHERE (number=?)', (client_num,))
            print('The account has been closed!')
            return
        elif input_ == '5':
            print('You have successfully logged out!')
            return
        elif input_ == '0':
            sys.exit()


b1 = Bank()
connection.close()