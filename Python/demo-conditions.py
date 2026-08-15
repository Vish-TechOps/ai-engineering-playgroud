# 3 keywords/statements are if, else if(elif), else
date = "28-05-2026"
early_bird = "20-05-2026"
# code-1
if date <= early_bird:
    ticket_price = 50
else:
    ticket_price = 75
print("your ticket price is:", ticket_price)

# code-2
ticket_price = 75
if date <= early_bird:
    ticket_price = 50
print("your TICKET PRICE is:", ticket_price)

# code-3
temp = 20
if temp > 30:
    print("There is hot outside")
elif temp > 15:
    print("This is nice outside")
elif temp > 0:
    print("There is cold outside")
else:
    print("There is freezing cold outside")

# code-4
username = "admin"
password = "correctPassword"
age = 10
if username == "admin" and password == "correctPassword":
    print("Welcome", "admin!")
else:
    print("This is not admin")

if age < 5 or age > 65:
    print("You are eligible for discount")
else:
    print("Not eligible for discount")








