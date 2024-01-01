import pickle
import os
import datetime
from pick import pick
import csv

# Define shifts
shifts = [
    {"name": "14-18", "start": 14, "end": 18},
    {"name": "18-22", "start": 18, "end": 22},
    {"name": "22-02", "start": 22, "end": 2},
    {"name": "02-06", "start": 2, "end": 6},
    {"name": "06-10", "start": 6, "end": 10},
    {"name": "10-14", "start": 10, "end": 14},
]

all_guards=[]
# Read guards from csv file
try:
    with open('guards.csv', 'r', encoding='utf-8-sig') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            all_guards.append(row[0])  # assuming guard name is in the first column
except FileNotFoundError:
    with open(input('העתק-הדבק את הנתיב לקובץ רשימת שומרים כולל סיומת (.csv)'), 'r', encoding='utf-8-sig') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                all_guards.append(row[0])  # assuming guard name is in the first column

# Selector for unavailable guards
title=("(מי בחוץ? (לבחור באמצעות רווח, להתקדם עם אנטר")
options=all_guards
selected= pick(options,title,multiselect=True, min_selection_count=0)
out_guards=[x[0] for x in selected]
print(out_guards, "מחוץ לסבב: ")
# Remove unavailable guards from available list
available_guards = [guard for guard in all_guards if not any(guard in tup for tup in selected)]

# Initialize day and night shifts
day_shifts = []
night_shifts = []

# Selector for number of guards during the day
title=("כמה שומרים ביום?")
options=["1","2","3","4"]
selected= pick(options,title)
print(selected[0], " שומרים ביום")
day_count=int(selected[0])

# Selector for number of guards during the night
title=("כמה שומרים בלילה?")
options=["1","2","3","4"]
selected= pick(options,title)
print(selected[0], " שומרים בלילה")
night_count=int(selected[0])

# Last shift file path
last_shift_file = 'last_shift.pkl'
# Check if the file exists
load_file=False
if os.path.exists(last_shift_file):
    # Selector for loading shift history or starting from scratch
    title=("לטעון היסטוריית שמירות או להתחיל מהתחלה?")
    options=["לטעון היסטוריה","להתחיל מהתחלה"]
    selected= pick(options,title)
    print(selected[0])
    if selected[0]=="לטעון היסטוריה": load_file=True
if os.path.exists(last_shift_file) and load_file:
    # Load last_shift from the file
    with open(last_shift_file, 'rb') as f:
        last_shift = pickle.load(f)
else:
    # Initialize last shift for each guard
    last_shift = {guard: 6 for guard in all_guards}
    
    # Ask the user for input about the guards from the previous day's 18-22 shift
    previous_18_22_guards = []
    title=("מי שמר 18-22?")
    options=all_guards    # Update last_shift for these guards
    selected=pick(options,title,multiselect=True, min_selection_count=0)
    for guard in selected: previous_18_22_guards.append(guard[0])
    for guard in previous_18_22_guards:
        last_shift[guard] = 5
    
    # Ask the user for input about the guards from the previous day's 22-2 shift
    previous_22_2_guards = []
    title=("מי שמר 22-02?")
    options=all_guards    # Update last_shift for these guards
    selected=pick(options,title,multiselect=True, min_selection_count=0)
    for guard in selected: previous_22_2_guards.append(guard[0])
    for guard in previous_22_2_guards:
        last_shift[guard] = 4
    
    # Ask the user for input about the guards from the previous day's 2-6 shift
    previous_2_6_guards = []
    title=("מי שמר 02-06?")
    options=all_guards    # Update last_shift for these guards
    selected=pick(options,title,multiselect=True, min_selection_count=0)
    for guard in selected: previous_2_6_guards.append(guard[0])
    for guard in previous_2_6_guards:
        last_shift[guard] = 3
    
    # Ask the user for input about the guards from the previous day's 6-10 shift
    previous_6_10_guards = []
    title=("מי שמר 06-10?")
    options=all_guards    # Update last_shift for these guards
    selected=pick(options,title,multiselect=True, min_selection_count=0)
    for guard in selected: previous_6_10_guards.append(guard[0])
    for guard in previous_6_10_guards:
        last_shift[guard] = 2

    # Ask the user for input about the guards from the previous day's 10-14 shift
    previous_10_14_guards = []
    title=("מי שמר 10_14?")
    options=all_guards    # Update last_shift for these guards
    selected=pick(options,title,multiselect=True, min_selection_count=0)
    for guard in selected: previous_10_14_guards.append(guard[0])
    for guard in previous_10_14_guards:
        last_shift[guard] = 1

# Check if each guard in the CSV file exists in the last_shift dictionary
for guard in all_guards:
    if guard not in last_shift:
        # If a guard doesn't exist, add them with a default last_shift value
        last_shift[guard] = 6

# Ask the user for input about the returning guards
returning_guards = []
# Selector for returning guards
title=("מי חוזר?")
options=available_guards
selected=pick(options,title,multiselect=True, min_selection_count=0)
return_guards=[x[0] for x in selected]
print(return_guards, "חוזרים: ")
for guard in selected: returning_guards.append(guard[0])

# Selector for returning guards shift time
title=("האם חוזרים שומרים 14-18?")
options=["כן","לא"]
selected=pick(options,title)
print("14-18 ","חוזרים ",selected[0], " שומרים")
if selected[0]=="כן":
    return_break=False
elif selected[0]=="לא":
    return_break=True

# Assign guards to shifts
for i, shift in enumerate(shifts):
    # Sort available guards by the number of shifts since their last shift
    available_guards.sort(key=lambda guard: (i - last_shift[guard] if last_shift[guard] is not None else float('inf')))
    assigned_guards = 0
    # Initialize not_assigned_guards with all available guards
    not_assigned_guards = available_guards.copy()
    if shift["start"] != 22 and shift["start"] != 2:
        # Day shift
        for _ in range(day_count):
            if available_guards:
                for guard in available_guards:
                    # Check if guard has had at least 2 shifts of rest
                    if last_shift[guard] >= 2:
                        # Make sure returning guards are not assigned to the 14-18 shift
                        if shift["start"] == 14 and guard in returning_guards and return_break==True:
                            continue
                        # Assign guard to shift and update last shift
                        last_shift[guard] = 0
                        day_shifts.append((shift["name"], guard))
                        assigned_guards += 1
                        # Remove guard from not_assigned_guards
                        not_assigned_guards.remove(guard)
                        break
        # Increment last shift for guards not assigned to the current shift
        for guard in not_assigned_guards:
            last_shift[guard] += 1
        
        # If not enough guards are assigned, assign returning guards
        if assigned_guards < day_count:
            for guard in returning_guards:
                if last_shift[guard] >= 2:
                    last_shift[guard] = 0
                    day_shifts.append((shift["name"], guard))
                    assigned_guards += 1
                    if assigned_guards == day_count:
                        break
            # If still not enough guards, print error and add placeholder
            while assigned_guards < day_count:
                # print(f"שגיאה: אין מספיק שומרים עבור משמרת {shift['name']}")
                day_shifts.append((shift["name"], "חסר שומר"))
                assigned_guards += 1
    else:
        # Night shift
        for _ in range(night_count):
            if available_guards:
                for guard in available_guards:
                    # Check if guard has had at least 2 shifts of rest
                    if last_shift[guard] >= 2:
                        # Assign guard to shift and update last shift
                        last_shift[guard] = 0
                        night_shifts.append((shift["name"], guard))
                        assigned_guards += 1
                        # Remove guard from not_assigned_guards
                        not_assigned_guards.remove(guard)
                        break
        # Increment last shift for guards not assigned to the current shift
        for guard in not_assigned_guards:
            last_shift[guard] += 1
        # If not enough guards are assigned, print error and add placeholder
        while assigned_guards < night_count:
            # print(f"שגיאה: אין מספיק שומרים עבור משמרת {shift['name']}")
            night_shifts.append((shift["name"], "חסר שומר"))
            assigned_guards += 1

            
# Combine day_shifts and night_shifts into one list
shifts = day_shifts + night_shifts

# Define sorting key function
def sorting_key(shift):
    start_time = int(shift[0].split('-')[0])
    return start_time + 24 if start_time < 14 else start_time

# Sort shifts by start time in a circular manner
shifts.sort(key=sorting_key)

# Group shifts by time
shifts_dict = {}
for shift in shifts:
    if shift[0] not in shifts_dict:
        shifts_dict[shift[0]] = list(shift[1:])
    else:
        shifts_dict[shift[0]].extend(shift[1:])

# Print shift roster
days_of_the_week = {"Sunday":"ראשון", "Monday":"שני", "Tuesday":"שלישי", "Wednesday":"רביעי", "Thursday":"חמישי", "Friday":"שישי", "Saturday":"שבת"}
print("\n")
print(days_of_the_week[datetime.date.today().strftime("%A")],"-",days_of_the_week[(datetime.date.today() + datetime.timedelta(days=1)).strftime("%A")])
#print(datetime.date.today().strftime("%A"),"-",(datetime.date.today() + datetime.timedelta(days=1)).strftime("%A")) #English DotW
print(datetime.date.today().strftime("%d/%m"),"-",(datetime.date.today() + datetime.timedelta(days=1)).strftime("%d/%m"))
for time, guards in shifts_dict.items():
    print(f"{time}: {', '.join(guards)}")

# # Ask user to swap WIP
# swap=input("האם תרצה להחליף ראש בראש? ")
# if swap=="כן":
#     # Selector for swapping shifts
#     title=("בחר שני שומרים להחליף ראש בראש")
#     options=available_guards
#     selected=pick(options,title,multiselect=True, min_selection_count=2)
#     if len(selected) != 2:
#         print("שגיאה: יש לבחור שני שומרים להחליף ראש בראש.")
#     else:
#         swap_guards=[x[0] for x in selected]
#         a = swap_guards[0]
#         b= swap_guards[1]
#         temp_var=shifts_dict[shifts[b][0]]
#         shifts_dict[shifts[b][0]] = shifts_dict[shifts[a][0]]
#         shifts_dict[shifts[a][0]] = temp_var
#         temp_var=last_shift[shifts[b][1]]
#         last_shift[shifts[b][1]] = last_shift[shifts[a][1]]
#         last_shift[shifts[a][1]] = temp_var  
# else:
#     # Wait for user input to exit
#     input("לחץ על אנטר כדי לצאת מהתוכנה...")

input("לחץ על אנטר כדי לצאת מהתוכנה...")

# Pop last element for last_shift if empty
if list(last_shift.keys())[-1]=='':
    last_shift.popitem()
# At the end of the program, write last_shift to the file
with open(last_shift_file, 'wb') as f:
    pickle.dump(last_shift, f)