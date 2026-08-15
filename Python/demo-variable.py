# input("What's your name: ")
# # This is input fuction which does not store user value automatically

# name = input("What is your name: ")
# print("Hello", name)

name = "John"
print("Hello", name)

name = "Sarah"
age = "25"
print(name, "is", age)

# Variables are mutable and dynamically typed

## Verbose
bank_balance = 500
# withdraw 20
bank_balance = bank_balance - 20
# deposit 100
bank_balance = bank_balance + 100
# print
print("Your bank balance is", bank_balance)

## Shorthand
bank_balance = 500
# withdraw 20
bank_balance -= 20
# deposit 100
bank_balance += 100
# print
print("Your bank balance is", bank_balance)