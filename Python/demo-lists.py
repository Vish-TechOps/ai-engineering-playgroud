## demo-1
print("---demo-1---")
employees = ["Olivia", "James"]
print(employees)
employees.append("Emily")
print(employees)
employees.insert(2, "Michael")
print(employees)
if "James" in employees:
    employees.remove("James")
print(employees)

## demo-2
print("---demo-2---")
stores = ["Sunrise books", "Moonlight market", "Gadget shop", "Magic toy", "Moonlight market"]
print(len(stores))
while "Moonlight market" in stores:
    stores.remove("Moonlight market")
print(stores)
print(len(stores))

## demo-3
print("---demo-3---")
print(employees[0])
print(employees[-1])
print(employees[2])
print(employees[-3])

## demo-4
print("---demo-4---")
business_expenses = [100,10,40,200,5,95,100]
total = 0
for expense in business_expenses:
    total += expense
print("Weekly business expense is: ", total)

## demo-5
print("---demo-5---")
business_expenses = [100,10,40,200,5,95,100]
total = 0
for day in range(len(business_expenses)):
    expense = business_expenses[day]
    print("Day", day+1, "expenses are", expense)
    total += expense
print("Weekly business expense is: ", total)

## demo-6
print("---demo-6---")
business_expenses = [100,10,40,200,5,95,100]
total = 0
for day, expense in enumerate(business_expenses, 1):
    print("The expenses for day", day, "are", expense)
    total += expense
print("Weekly business expense is: ", total)