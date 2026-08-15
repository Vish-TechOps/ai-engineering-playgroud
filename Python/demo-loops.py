# For loop with iteration varible and range function 

# code-1
for i in range(5):
    print("Hello!")
print("Hi!")

# code-2
stuck = False
while stuck:
    print("I am stuck...")
print("I am free")

# code-3
playing = "yes"
while playing == "yes":
    print("I am playing!!")
    playing = input("Do you want more play: ")
print("It was fun!")

# code-4 - Guess number 3 times
my_number = "5"
for guess in range(3):
    your_number = input("Please guess your number: ")
    print("your number is ->", your_number)
    if your_number == my_number:
        print("you guessed right!")
        break
    else:
        print("nope! continue guessing...")
print("This is fun activity")


# code-5 - Print floors with continue

for floor in range(10,15):
    if floor == 13:
        continue
    print("Floor number is ->", floor)