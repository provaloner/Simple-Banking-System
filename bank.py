import random
import string
import sqlite3

conn = sqlite3.connect('card.s3db')

c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS card
             (id INTEGER, number TEXT, pin TEXT, balance INTEGER DEFAULT 0)''')


def check_luhn(card_num):
    oddeven = []
    over_9 = []
    for index in range(1, len(card_num) + 1):
        if index % 2 != 0:
            oddeven.append(card_num[index - 1] * 2)
        else:
            oddeven.append(card_num[index - 1])
    for index in range(len(oddeven)):
        if oddeven[index] > 9:
            over_9.append(oddeven[index] - 9)
        else:
            over_9.append(oddeven[index])
    return sum(over_9)


def create_account():
    bank_id = [4, 0, 0, 0, 0, 0]
    acc_id = random.choices([0, 1, 2, 3, 4, 5, 6, 7, 8, 9], k=9)
    to_luhn = bank_id + acc_id
    luhn_sum = check_luhn(to_luhn)
    checksum = 10 - (luhn_sum % 10)
    if checksum == 10:
        checksum = 0
    to_luhn.append(checksum)
    new_acc = "".join([str(i) for i in to_luhn])
    new_pin = "".join(random.choices(list(string.digits), k=4))
    print(f"""\nYour card has been created
Your card number:
{new_acc}
Your card PIN:
{new_pin}\n""")
    return new_acc, new_pin


def login():
    print("\nEnter your card number:")
    try_acc = input()
    print("Enter your PIN:")
    try_pin = input()
    c.execute('SELECT count(number) FROM card WHERE number=? AND pin=?', (try_acc, try_pin))
    if c.fetchone()[0] == 1:
        print("You have successfully logged in!")
        conn.commit()
        return login_menu(try_acc)
    else:
        print("\nWrong card number or PIN!\n")
        return 1


def login_menu(acc):
    while True:
        print("""\n1. Balance
2. Add income
3. Do transfer
4. Close account
5. Log out
0. Exit""")
        option = int(input())
        if option == 0:
            return 0
        elif option == 1:
            c.execute('SELECT balance FROM card WHERE number = ?', (acc,))
            print(c.fetchone())
            conn.commit()
            continue
        elif option == 2:
            print("\nEnter income:")
            add = int(input())
            c.execute('UPDATE card SET balance = balance + ? WHERE number = ?', (add, acc))
            conn.commit()
            print("Income was added!\n")
            continue
        elif option == 3:
            print(transfer(acc))
            continue
        elif option == 4:
            c.execute('DELETE FROM card WHERE number = ?', (acc,))
            conn.commit()
            print("\nThe account has been closed!\n")
            return 4
        elif option == 5:
            print("\nYou have successfully logged out!\n")
            return 5


def transfer(acc):
    print("Enter card number:")
    trans_acc = str(input())
    luhn_check = [int(x) for x in trans_acc]
    last = luhn_check.pop()
    luhn_sum = check_luhn(luhn_check) + last
    c.execute('SELECT count(number) FROM card WHERE number=?', (trans_acc,))
    if luhn_sum % 10 != 0:
        return "Probably you made mistake in the card number. Please try again!"
    elif trans_acc == acc:
        return "You can't transfer money to the same account!"
    elif c.fetchone()[0] == 0:
        return "Such a card does not exist."
    else:
        print("Enter how much money you want to transfer:")
        trans_amount = int(input())
        c.execute('SELECT balance FROM card WHERE number=?', (acc,))
        current_balance = c.fetchone()[0]
        if trans_amount > current_balance:
            return "Not enough money!"
        else:
            c.execute('UPDATE card SET balance = balance - ? WHERE number = ?', (trans_amount, acc))
            c.execute('UPDATE card SET balance = balance + ? WHERE number = ?', (trans_amount, trans_acc))
            conn.commit()
            return "Success!"


while True:
    print("""1. Create an account
2. Log into account
0. Exit""")
    command = int(input())
    if command == 0:
        conn.close()
        break
    elif command == 1:
        a, p = create_account()
        c.execute("INSERT INTO card (number, pin) VALUES (?, ?)", (a, p))
        conn.commit()
        continue
    elif command == 2:
        c = login()
        if c == 0:
            conn.close()
            break
        else:
            continue
