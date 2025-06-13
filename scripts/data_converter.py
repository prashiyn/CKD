import json
import os
import sys

# Add the project root to the path so we can import from models
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models import PatientQnA

# Questions from prompts.py
questions = [
    "What is your gender?",
    "What is your current age?",
    "Do you have high blood pressure (hypertension)?",
    "Do you have Type 1 diabetes?",
    "Do you have Type 2 diabetes?",
    "Do you have any cardiovascular disease?",
    "Have you noticed any changes in your appetite?",
    "Do you have swelling in your feet and ankles (pedal edema)?",
    "Have you noticed blood in your urine (hematuria)?",
    "Do you wake up frequently at night to urinate (nocturia)?",
    "Do you experience pain in your side or back (flank discomfort)?",
    "Have you noticed a decrease in your urine output?",
    "Do you feel unusually tired or weak (fatigue)?",
    "Do you experience nausea or vomiting?",
    "Do you have a metallic taste in your mouth?",
    "Have you lost weight unintentionally?",
    "Do you experience persistent itching?",
    "Have you noticed any changes in your mental state?",
    "Do you have difficulty breathing?",
    "At what age were you first diagnosed with kidney disease?",
    "If you are on dialysis, what is your current age during dialysis?",
    "When was your most recent medical report obtained?"
]

# Fix the data_past and data_present lists by adding commas between rows
# Raw data extracted from the table
data_past = [
    [1, 4, 46, 50, "Female", "yes", "no", "no", "yes", "yes", "yes", "no", "no", "yes", "yes", "yes", "no", "no", "no", "yes", "yes", "yes"],
    [2, 2, 50, 52, "Male", "yes", "yes", "yes", "no", "yes", "no", "no", "yes", "no", "yes", "yes", "no", "no", "yes", "yes", "no", "yes"],
    [4,"yes", 28, 29, "Female","yes","no","no","no","yes","yes","no","no","yes","maybe","yes","no","no","no","no","yes","no"],
    [5, 7, 45, 52, "Male","yes","no","no","no","no","no","no","no","yes","no","yes","no","no","yes","yes","yes","yes"],
    [6, 3, 29, 32, "Male","yes","no","no","no","no","yes","no","no","yes","no","no","no","maybe","yes","no","no","no"],
    [7, 8, 25, 33, "Male","yes","no","no","no","no","no","no","no","no","no","no","no","no","yes","no","no","maybe"],
    [8, 8, 37, 45, "Female","yes","no","no","no","no","no","no","no","no","yes","yes","no","no","no","no","no","yes"],
    [9, 8, 51, 59, "Male","yes","no","no","no","no","yes","no","yes","maybe","no","yes","no","no","no","no","no","yes"],
    [10, 2, 62, 64, "Male","yes","yes","yes","yes", None,"no","no","no","no","yes","no","no","no","no","no","no","no"],
    [11, 2, 49, 51, "Male","no","no","no","yes","no","no","no","yes","no","no","no","no","no","no","no","no","no"],
    [12, 9, 49, 58, "Female","yes","no","no","no","yes","yes","no","yes","yes","yes","yes","no","no","no","no","yes","no"],
    [13, 2, 47, 42, "Male","yes","no","no","no","no","no","no","no","no","no","no","no","no","no","no","no", "maybe"],
    [14, 2, 53, 53, "Female","yes","yes", None,"no","no","no","no","yes","no","no","yes","yes","no","yes","yes","no","no"],
    [15,"yes", 58, 59, "Female","no","no","no","no","no","no","no","no","no","yes","yes","yes","no","no","no","no","maybe"],
    [16,"maybe", 55, 55, "Male","no","yes","no","no","no","no","no","no","yes","no","no","no","no","no","no","no","no"],
    [18, 3, 27, 30, "Female","no","no","no","no","no","no","no","no","maybe","no","yes","no","yes","no","no","no","yes"],
    [19, 7, 30, 37, "Male","yes","no","no","no","yes","no","no","no","no","yes","yes","yes","yes","no","no","no","yes"],
    [20, 5, 59, 64, "Male","yes","yes","yes","yes","no","yes","no","no","yes","no","yes","yes","no","no","no","no","yes"],
    [21, 8, 47, 55, "Female","yes","no","no","no","no","no","yes","no","no","no","yes","no","no","no","no","no","no"],
    [22,"yes", 58, 58, "Female","yes","no","no","no","yes","no","no","no","yes","no","yes","yes","yes","yes","maybe","no","yes"],
    [25, 'NA', 'NA', 42, "Female","no","no","no","no","no","no","no","no","yes","no","no","yes","no","no","no","no","maybe"],
    [26, 2, 61, 63, "Male","yes","no","no","no","no","yes","no","no","no","no","no","no","yes","no","no","no","yes"],
    [27, 3, 61, 63, "Male","no","no","no","no","no","no","no","no","no","yes","no","no","no","no","no","no","no"],
    [28, 0.25, 68, 68, "Male","no","no","yes","no","no","yes","yes","yes","maybe","no","yes","no","no","no","no","no","no"],
    [29, 0.1, 65, 65, "Female","yes","yes","yes","no","no","no","no","no","no","no","yes","no","no","no","no","no","no"],
    [30,"no", 45, 45, "Female","yes","yes","no","no","yes","no","no","no","no","no","no","no","no","no","no","no","no"],
    [31,"no", 78, 78, "Male","no","yes","no","no","no","yes","no","no","no","yes","no","no","no","no","no","no","yes"],
    [32, 'NA', 'NA', 67, "Male","yes","no", 'NA',"yes","no","yes","no","yes","no","no","no","no","no","no","no","yes"],
    [33, 11, 50, 61, "Female","yes","no","no","no","yes","no","no","no","yes","yes","yes","yes","maybe","no","yes","yes","yes"],
    [34, 2, 63, 65, "Female","yes","yes","yes","yes","yes","yes","no","yes","yes","yes","yes","yes","yes","yes","no","yes","no"],
    [35, 6, 32, 38, "Male","yes","no","no","yes","no","no","no","no","no","no","yes","no","no","yes","no","no","no"],
    [36,"yes", 82, 83, "Male","yes","no","no","yes","yes","yes","no","no","yes","no","yes","no","no","yes","no","no","yes"],
    [37,"yes", 74, 75, "Female","yes","yes","yes","no","no","yes","no","no","no","yes","no","no","no","no","yes","no","no"],
    [38,"no", 55, 55, "Female","yes","yes", 'NA',"no","yes","yes","no","no","no","yes","yes","no","no","no","yes","no","no"],
    [39, 4, 27, 31, "Female","yes","no","no","no","yes","no","no","no","no","no","yes","yes","no","no","no","no","no"],
    [40,"yes", 65, 67, "Female","yes","no", 'NA',"no","yes","yes","no","yes","no","yes","yes","yes","no","no","no","no","yes"],
    [41, 3, 60, 54, "Female","no","no", 'NA',"yes","yes","yes","yes","yes","yes","yes","yes","no","yes","no","yes","maybe","maybe"],
    [42,"yes", 64, 65, "Female","yes","yes","yes","yes","yes","no","no","yes","yes","no","no","no","no","no","yes","no","no"],
    [43,"yes", 29, 30, "Male","no","no", 'NA',"no","yes","no","yes","no","no","maybe","yes","no","no","yes","no","no","no"],
    [44, 'NA', 'NA', 62, "Male","no","no","no","no","no","no","no","maybe","no","no","yes","no","maybe","no","yes","no","no"],
    [46, 1.5, 73, 72, "Male","no","yes", 'NA',"yes","no","yes","maybe","yes","yes","no","yes","no","no","no","no","yes","yes"],
    [47,"yes", 55, 56, "Female","yes","no", 'NA',"yes","yes","yes","no","no","yes","no","yes","yes","no","no","yes","yes","yes"],
    [48,"yes", 72, 73, "Female","yes","no", 'NA',"no","no","yes","yes","yes","yes","yes","yes","no","yes","yes","no","no","no"],
    [49,"yes", 32, 30, "Male","no","no","no","no","yes","no","no","no","no","yes","maybe","no","no","no","no","no","no"],
    [50,"no", 48, 48, "Female","yes","no", 'NA',"no","no","no","no","no","no","yes","maybe","no","yes","yes","no","no","no"],
    [51,"yes", 52, 53, "Female","no","no","no","yes","yes","yes","no","yes","no","no","no","no","no","yes","maybe","yes"],
    [53,"yes", 70, 70, "Female","yes","yes", 'NA',"no","no","yes","no","yes","yes","no","yes","yes","yes","no","yes","yes","yes"],
    [56, 'NA', 'NA', 63, "Male","no","no","no","no","no","yes","no","no","yes","no","no","yes","no","no","yes","no","no"],
    [58, 4, 63, 67, "Female","yes","yes","yes","no","yes","no","no","no","no","maybe","yes","no","yes","yes","yes","no","no"],
    [59, 1.5, 63.5, 65, "Male","yes","no","no","no","no","yes","maybe","no","no","no","yes","no","no","no","no","no","no"],
    [60, 2, 63, 64, "Male","yes","yes","yes","no","no","no","no","no","no","no","maybe","no","no","yes","no","maybe"],
    [61, 3, 70, 73, "Male","no","no", 'NA',"no","yes","no","no","no","no","no","yes","yes","no","no","no","no","yes"],
    [62, 6, 48, 54, "Male","no","yes","yes","yes","yes","yes","no","no","no","no","yes","maybe","no","no","no","maybe","no"],
    [71, 4, 65, 69, "Female","no","no", 'NA',"no","no","no","no","no","no","no","yes","no","no","yes","no","no","no"],
    [72, 5, 61, 66, "Male","yes","no", 'NA',"no","no","no","no","maybe","no","no","maybe","no","no","no","yes","no","no"],
    [73, 2, 62, 64, "Male","yes","yes", 'NA',"yes","yes","yes","no","no","yes","yes","no","yes","no","yes","no","no","yes"],
    [74,"no", 59, 59, "Male","no","no", 'NA',"yes","no","no","no","no","no","no","maybe","no","no","no","no","no","no"],
    [75,"yes", 68, 69, "Male","no","yes", 'NA',"no","yes","yes","no","yes","no","no","no","no","no","yes","no","no","maybe"],
    [81, 2, 65, 67, "Male","yes","no", 'NA',"yes","yes","yes","no","no","no","no","maybe","no","no","no","yes","no","maybe"],
    [82, 7, 63, 70, "Male","yes","no", 'NA',"yes","no","yes","no","no","no","no","no","yes","yes","yes","no","yes","no"],
    [83,"yes", 39, 40, "Male","yes","yes","yes","no","yes","no","yes","no","yes","no","yes","no","yes","yes","yes","maybe","yes"],
    [91, 5, 54, 59, "Female","yes","yes", 'NA',"yes","yes","yes","no","no","no","no","yes","maybe","yes","yes","yes","no","yes"],
    [92, 0.3, 33, 33, "Male","yes","no", 'NA',"no","no","yes","no","no","no","no","no","no","no","no","yes","no","no"],
    [93,"yes", 58, 59, "Female", 'NA',"no", 'NA',"no","no","no","no","yes","no","no","no","no","no","no","yes","no","no"],
    [94, 3, 61, 64, "Male","yes","no", 'NA',"yes","yes","no","no","no","yes","no","yes","no","no","yes","yes","no","yes"],
    [106, 'NA', 61, 68, "Male","yes","yes", 'NA',"no","yes","yes","no","no","yes","yes","yes","yes","yes","yes","yes","no"],
    [107, 2, 60, 80, "Male","yes","yes","yes","no","yes","no","no","no","no","maybe","no","no","no","yes","yes","no","maybe"],
    [108,"yes", 61, 66, "Male","yes","no","no","yes","no","yes","no","yes","no","no","no","no","no","no","no","no"],
    [109, 'NA', 'NA', 83, "Male","no","no","no","no","no","no","no","no","no","yes","no","no","no","no","yes","no","yes"],
    [110, 12, 56, 68, "Male","yes","no","no","no","no","maybe","no","no","no","no","yes","no","no","yes","no","no","no"],
    [111, 15, 25, 40, "Male","yes","no","no","no","no","yes","no","no","no","no","yes","no","no","yes","no","no","yes"],
    [112, 'NA', 'NA', 46, "Male","yes","no", 'NA',"no","no","no","no","no","no","yes","no","yes","no","yes","no","no","no"],
    [113, 2, 31, 33, "Female","yes","yes", 'NA',"no","yes","yes","no","no","yes","no","yes","yes","yes","yes","yes","no","yes"],
    [114, 2, 71, 73, "Male","yes","yes", 'NA',"no","yes","no","no","yes","no","no","yes","yes","yes","yes","no","no","yes"],
    [115, 0.1, 57, 57, "Female","yes","yes","yes","no","yes","yes","no","yes","yes","no","yes","yes","yes","yes","yes","no", "maybe"],
    [116, 4, 71, 75, "Female","yes","no","no","no","yes","maybe","no","no","yes","no","yes","no","no","no","no","yes","no"],
    [117, 3, 73, 76, "Female","yes","yes","yes","yes","yes","yes","no","no","no","no","no","no","no","no","no","maybe","no"],
    [118, 'NA', 'NA', 51, "Male","yes","no","no","no","no","no","no","no","yes","no","no","no","maybe","yes","no","no","maybe"],
    [119, 'NA', 'NA', 36, "Male","yes","no","no","no","yes","yes","maybe","no","maybe","no","yes", "maybe","no","no","no","no","yes"],
    [120, 'NA', 'NA', 34, "Male","no","no","no","no","yes","no","yes","no","no","yes","no","no","maybe","yes","yes","no","maybe"],
    [121, 2, 62, 64, "Male","yes","yes","yes","yes","no","no","no","yes","no","yes","no","no","no","no","no","no","yes"]
]

data_present = [
    [1,4,46,50,"Female","yes","no","no","yes","yes","yes","no","no","no","yes","yes","no","no","no","yes","yes","yes"],
    [2,2,50,52,"Male","yes","yes","yes","no","no","no","no","no","no","yes","yes","no","no","no","no","no","no"],
    [4,"yes",28,29,"Female","yes","no","no","no","yes","yes","no","no","no","yes","yes","no","no","no","no","no","no"],
    [5,7,45,52,"Male","yes","no","no","no","no","yes","no","yes","no","no","no","yes","no","yes","yes","yes","yes"],
    [6,3,29,32,"Male","yes","no","no","no","no","yes","no","no","yes","no","no","no","maybe","yes","yes","no","yes"],
    [7,8,25,33,"Male","yes","no","no","no","no","no","no","no","yes","no","no","no","no","no","no","no","maybe"],
    [8,8,37,45,"Female","yes","no","no","no","no","no","no","yes","no","yes","yes","yes","no","no","no","no","yes"],
    [9,8,51,59,"Male","yes","no","no","no","no","no","no","no","maybe","no","yes","no","yes","no","yes","no","no"],
    [10,2,62,64,"Male","yes","yes","yes","yes","NA","no","no","no","no","no","no","maybe","no","no","no","no","no"],
    [11,2,49,51,"Male","yes","no","no","no","no","yes","no","no","no","no","no","yes","yes","no","yes","yes","no"],
    [12,9,49,58,"Female","yes","no","no","no","yes","yes","no","no","no","yes","yes","maybe","yes","yes","yes","yes","yes"],
    [13,2,47,42,"Male","no","no","no","no","no","yes","no","yes","no","no","no","yes","no","yes","yes","no","maybe"],
    [14,2,53,53,"Female","yes","yes","NA","no","no","yes","no","yes","no","no","yes","yes","no","yes","yes","no","no"],
    [15,"yes",58,59,"Female","no","no","no","no","yes","yes","no","yes","yes","no","no","no","no","no","no","yes","maybe"],
    [16,"maybe",55,55,"Male","no","yes","no","no","yes","no","no","no","no","no","yes","no","no","yes","no","no","yes"],
    [18,3,27,30,"Female","yes","no","no","no","yes","no","no","yes","maybe","no","no","yes","no","no","no","no","no"],
    [19,7,30,37,"Male","yes","no","no","no","yes","yes","no","no","no","no","no","no","no","no","no","yes","no"],
    [20,5,59,64,"Male","yes","yes","yes","yes","no","no","no","yes","no","yes","no","yes","no","no","yes","yes","no"],
    [21,8,47,55,"Female","no","no","no","no","no","no","no","no","no","no","no","yes","yes","yes","no","no","no"],
    [22,"yes",58,58,"Female","yes","no","no","no","yes","no","no","no","no","no","no","no","yes","no","maybe","yes","no"],
    [25,"NA","NA",42,"Female","no","no","no","no","no","yes","no","no","no","no","yes","no","yes","no","no","no","yes"],
    [26,2,61,63,"Male","yes","yes","yes","yes","yes","no","no","yes","no","no","yes","yes","no","yes","yes","yes","no"],
    [27,3,61,63,"Male","yes","yes","yes","yes","no","no","no","yes","no","no","no","no","no","no","no","no","no"],
    [28,0.25,68,68,"Male","no","yes","no","no","no","no","no","no","maybe","no","no","yes","no","no","no","no","yes"],
    [29,0.1,65,65,"Female","no","no","no","no","no","maybe","no","yes","no","no","no","no","no","no","no","no","yes"],
    [30,"no",45,45,"Female","no","no","yes","no","yes","no","no","no","no","no","no","yes","no","yes","no","yes","no"],
    [31,"no",78,78,"Male","no","no","yes","no","no","no","no","no","yes","no","yes","no","no","no","yes","no","no"],
    [32,"NA","NA",67,"Male","yes","no","NA","yes","no","no","no","yes","no","no","no","yes","no","no","no","no","no"],
    [33,11,50,61,"Female","yes","no","no","no","yes","yes","no","no","yes","yes","yes","yes","maybe","yes","yes","yes","yes"],
    [34,2,63,65,"Female","yes","yes","yes","yes","yes","no","no","yes","yes","yes","yes","yes","yes","yes","no","yes","no"],
    [35,6,32,38,"Male","yes","no","no","yes","no","no","no","no","no","no","yes","no","no","yes","no","no","no"],
    [36,"yes",82,83,"Male","yes","no","no","yes","yes","yes","no","no","yes","no","no","no","no","yes","no","no","yes"],
    [37,"yes",74,75,"Female","yes","yes","yes","no","yes","yes","no","no","no","yes","yes","no","no","no","yes","no","no"],
    [38,"no",55,55,"Female","yes","yes","NA","no","yes","yes","no","no","no","yes","yes","no","no","no","yes","no","yes"],
    [39,4,27,31,"Female","no","no","no","no","yes","no","no","no","no","no","yes","yes","no","no","no","no","no"],
    [40,"yes",65,67,"Female","yes","yes","NA","no","yes","yes","no","yes","no","yes","no","yes","no","no","no","no","yes"],
    [41,3,60,54,"Female","no","no","NA","yes","yes","yes","yes","yes","yes","yes","yes","no","yes","no","yes","maybe","maybe"],
    [42,"yes",64,65,"Female","no","no","no","no","no","no","no","no","no","no","no","yes","no","no","maybe","no","no"],
    [43,"yes",29,30,"Male","yes","no","NA","no","yes","no","yes","no","no","maybe","yes","no","no","yes","no","no","no"],
    [44,"NA","NA",62,"Male","no","yes","yes","no","yes","yes","no","maybe","yes","no","no","no","maybe","no","no","no","yes"],
    [46,1.5,73,72,"Male","no","yes","NA","yes","no","yes","maybe","yes","no","no","yes","no","no","no","yes","yes","yes"],
    [47,"yes",55,56,"Female","yes","no","NA","yes","yes","yes","no","no","yes","no","yes","yes","no","no","yes","yes","yes"],
    [48,"yes",72,73,"Female","yes","no","NA","no","no","yes","yes","yes","yes","yes","yes","no","yes","yes","no","no","no"],
    [49,"yes",32,30,"Male","yes","no","no","no","no","no","no","no","no","yes","maybe","no","no","no","no","no","no"],
    [50,"no",48,48,"Female","yes","no","NA","no","no","yes","no","yes","no","yes","maybe","yes","yes","yes","no","no","no"],
    [51,"yes",52,53,"Female","yes","yes","yes","no","yes","yes","yes","no","yes","no","yes","yes","yes","yes","no","maybe","no"],
    [53,"yes",70,70,"Female","yes","yes","NA","no","no","yes","no","yes","yes","no","yes","yes","yes","no","yes","yes","yes"],
    [56,"NA","NA",63,"Male","no","yes","yes","no","no","yes","no","no","yes","no","yes","no","yes","no","yes","no","no"],
    [58,4,63,67,"Female","no","no","no","no","yes","no","no","no","no","maybe","no","yes","yes","no","no","no","no"],
    [59,1.5,63.5,65,"Male","no","no","no","no","no","no","maybe","no","no","no","no","no","no","no","no","no","no"],
    [60,2,63,64,"Male","yes","yes","yes","no","no","yes","no","yes","yes","no","no","maybe","no","yes","yes","no","maybe"],
    [61,3,70,73,"Male","no","no","NA","no","yes","no","no","no","no","no","yes","no","no","no","no","no","yes"],
    [62,6,48,54,"Male","no","yes","yes","yes","yes","no","no","no","yes","no","no","maybe","no","yes","yes","maybe","no"],
    [71,4,65,69,"Female","yes","no","NA","no","yes","yes","no","no","yes","no","yes","no","no","yes","yes","no","no"],
    [72,5,61,66,"Male","yes","no","NA","no","no","no","no","maybe","no","no","maybe","no","no","no","yes","no","no"],
    [73,2,62,64,"Male","yes","yes","NA","yes","yes","yes","no","no","yes","yes","no","yes","no","yes","no","no","yes"],
    [74,"no",59,59,"Male","yes","no","NA","yes","no","no","no","no","no","no","maybe","yes","no","no","no","no","no"],
    [75,"yes",68,69,"Male","yes","yes","NA","no","yes","no","no","yes","no","no","yes","no","no","yes","no","no","maybe"],
    [81,2,65,67,"Male","yes","yes","NA","yes","yes","yes","no","no","no","no","maybe","no","no","no","yes","no","maybe"],
    [82,7,63,70,"Male","yes","yes","NA","yes","no","yes","no","no","no","no","no","yes","yes","yes","no","yes","no"],
    [83,"yes",39,40,"Male","yes","yes","yes","no","yes","yes","no","no","no","no","no","no","no","no","yes","maybe","maybe"],
    [91,5,54,59,"Female","yes","yes","NA","yes","yes","yes","no","no","no","no","yes","maybe","yes","yes","yes","no","yes"],
    [92,0.3,33,33,"Male","yes","no","NA","no","no","yes","no","no","yes","no","no","no","no","no","yes","no","no"],
    [93,"yes",58,59,"Female","yes","yes","NA","no","no","no","no","yes","no","no","no","no","no","no","yes","no","no"],
    [94,3,61,64,"Male","yes","no","NA","yes","yes","yes","no","no","yes","no","yes","yes","no","yes","yes","no","yes"],
    [106,"NA",61,68,"Male","yes","yes","NA","no","yes","yes","no","no","yes","yes","yes","yes","yes","yes","yes","yes","no"],
    [107,2,60,80,"Male","yes","yes","yes","no","yes","no","no","no","no","maybe","no","no","no","yes","no","no","maybe"],
    [108,"yes",61,66,"Male","yes","no","no","yes","yes","yes","no","yes","no","no","no","yes","no","no","no","no","no"],
    [109,"NA","NA",83,"Male","no","no","no","no","no","no","no","no","no","yes","no","no","no","no","yes","no","no"],
    [110,12,56,68,"Male","yes","no","no","no","no","maybe","no","no","no","no","yes","no","no","yes","no","no","no"],
    [111,15,25,40,"Male","yes","no","no","no","no","yes","no","no","no","no","yes","no","no","yes","no","no","yes"],
    [112,"NA","NA",46,"Male","yes","no","NA","no","yes","no","no","no","no","yes","yes","yes","no","yes","no","no","no"],
    [113,2,31,33,"Female","yes","yes","NA","no","yes","yes","no","no","yes","no","yes","yes","yes","yes","yes","no","yes"],
    [114,2,71,73,"Male","yes","yes","NA","no","yes","no","no","yes","no","no","yes","yes","yes","yes","no","no","yes"],
    [115,0.1,57,57,"Female","yes","yes","yes","no","yes","yes","no","yes","yes","no","yes","yes","yes","yes","yes","no","no"],
    [116,4,71,75,"Female","yes","no","no","no","yes","maybe","no","no","yes","no","yes","no","no","no","no","yes","no"],
    [117,3,73,76,"Female","yes","yes","yes","yes","yes","yes","no","no","no","no","no","no","no","no","no","no","no"],
    [118,"NA","NA",51,"Male","yes","no","no","no","no","no","no","no","yes","no","no","no","maybe","yes","no","no","maybe"],
    [119,"NA","NA",36,"Male","yes","no","no","no","yes","yes","maybe","no","maybe","no","yes","maybe","no","no","no","no","yes"],
    [120,"NA","NA",34,"Male","no","no","no","no","yes","no","yes","no","no","yes","no","no","maybe","yes","yes","no","maybe"],
    [121,2,62,64,"Male","yes","yes","yes","yes","no","no","no","yes","no","yes","no","no","no","no","no","no","yes"]
]

# Column indices for mapping to questions
# ID is at index 0, report date at 1, diagnosis age at 2, current age at 3, gender at 4
# The rest of the columns map to questions 3-19
question_indices = {
    0: 4,  # gender
    1: 3,  # current age
    2: 5,  # hypertension
    3: 6,  # diabetes type 1
    4: 7,  # diabetes type 2
    5: 8,  # cardiovascular disease
    6: 9,  # appetite changes
    7: 10, # pedal edema
    8: 11, # hematuria
    9: 12, # nocturia
    10: 13, # flank discomfort
    11: 14, # decreased urine output
    12: 15, # fatigue
    13: 16, # nausea vomiting
    14: 17, # metallic taste
    15: 18, # unintended weight loss
    16: 19, # itching
    17: 20, # mental state changes
    18: 21, # breathing difficulty
    19: 2,  # first diagnosis age
    20: 3,  # current age during dialysis
    21: 1   # report obtained date
}

def convert_to_patient_qna(data_list, dataset_name):
    all_patients = []
    
    for patient_data in data_list:
        patient_id = patient_data[0]
        patient_responses = []
        
        for q_idx, question in enumerate(questions):
            if q_idx in question_indices:
                data_idx = question_indices[q_idx]
                answer = str(patient_data[data_idx]) if data_idx < len(patient_data) else "NA"
                
                # Convert boolean-like strings to consistent format
                if answer.lower() in ["yes", "true", "1"]:
                    answer = "yes"
                elif answer.lower() in ["no", "false", "0"]:
                    answer = "no"
                elif answer.lower() in ["maybe", "unknown", "na", "none"]:
                    answer = "maybe"
                
                patient_responses.append(
                    PatientQnA(question=question, answer=answer).model_dump()
                )
        
        all_patients.append({
            "patient_id": patient_id,
            "responses": patient_responses
        })
    
    # Create data directory if it doesn't exist
    os.makedirs("./data", exist_ok=True)
    
    # Save to JSON file
    output_file = f"./data/{dataset_name}_patient_responses.json"
    with open(output_file, "w") as f:
        json.dump(all_patients, f, indent=2)
    
    print(f"Converted {len(all_patients)} patient records to {output_file}")
    return all_patients

# Convert both datasets
past_patients = convert_to_patient_qna(data_past, "past")
present_patients = convert_to_patient_qna(data_present, "present")

# Print sample of the first patient's data
print("\nSample of first patient data:")
print(json.dumps(past_patients[0]["responses"][:5], indent=2))