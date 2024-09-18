# the dataset is not sorted based on indiex due to multithreading 
#to sort the output based on index column and add indices that were there in the test dataset but failed to be outputed in the output csv
import pandas as pd

# Define the path to your CSV file
csv_file = "C:/Users/xgadg/Downloads/66e31d6ee96cd_student_resource_3/student_resource 3/dataset/test_out.csv"

# Step 1: Load the existing CSV file
df = pd.read_csv(csv_file)

# Step 2: Convert 'index' column to numeric, setting non-numeric values as NaN
df['index'] = pd.to_numeric(df['index'], errors='coerce')

# Step 3: Fill NaN values in 'index' with 0 or another placeholder, and convert to integers
df['index'] = df['index'].fillna(0).astype(int)

# Step 4: Define new indices (keeping it empty here as you indicated)
new_indices = {19968, 90626, 34310, 26631, 72200, 123401, 38922, 130568, 4622, 61967, 67088, 22033, 94225, 22037, 96790, 78363, 62492, 99327, 32798, 23584, 60449, 63008, 77859, 110629, 87590, 92198, 4649, 34858, 96812, 72749, 44591, 48691, 36405, 566, 60469, 24120, 46137, 39994, 96315, 56892, 64575, 38976, 60481, 130627, 48197, 13382, 11853, 54350, 95312, 97363, 47700, 114260, 31830, 47702, 114262, 48218, 94300, 26719, 40033, 107622, 15976, 90217, 79979, 7276, 20077, 28789, 96378, 87677, 67710, 13951, 26751, 5759, 87678, 88190, 127103, 91785, 65675, 15500, 73868, 7824, 90771, 18583, 33436, 8354, 34467, 85668, 47782, 26279, 4265, 21161, 101036, 28335, 9904, 49841, 74416, 97971, 128691, 128694, 104955, 63675, 48828, 20669, 69308, 71358, 115899, 99521, 21698, 46274, 35016, 105677, 39119, 87768, 72409, 72924, 77020, 93918, 43231, 61663, 77025, 115429, 18662, 109799, 78057, 5875, 71411, 25333, 99572, 30462, 96514, 58120, 86281, 66316, 61197, 37136, 110353, 128786, 111379, 1812, 98580, 74519, 69403, 3871, 99615, 122655, 9506, 39715, 30500, 23845, 27431, 48423, 116522, 26923, 57645, 29998, 47410, 88372, 1334, 100663, 106808, 111418, 129852, 88381, 94528, 27972, 87364, 87365, 108868, 103754, 40269, 48461, 13647, 127312, 88401, 12279, 31060, 2901, 23381, 31062, 73049, 40283, 73051, 21341, 113502, 18785, 85346, 50022, 98664, 73067, 14188, 44396, 29554, 45938, 88436, 102260, 96634, 78203, 56189, 19327, 50047, 50050, 67463, 56203, 3468, 25996, 64401, 116116, 104341, 105879, 2458, 28062, 106400, 79269, 66982, 76198, 85926, 109993, 113581, 124340, 1977, 130491, 22460, 60863, 94143, 109505, 120768, 61379, 46022, 46024, 72649, 90059, 43982, 96718, 15831, 55256, 33755, 63965, 99293, 63969, 60898, 102370, 88041, 103402, 7659, 64491, 61421, 100846, 106479, 113645, 60913, 38898, 130542, 130547, 23031, 44536, 78331, 130556, 5629, 72190, 83455}
# Create a DataFrame with these new indices and empty predictions
if new_indices:
    new_rows = pd.DataFrame({'index': list(new_indices), 'prediction': ''})
    # Combine the existing DataFrame with the new rows
    df_combined = pd.concat([df, new_rows], ignore_index=True)
else:
    df_combined = df  # No new indices to add

# Step 5: Sort the combined DataFrame based on the 'index' column, ensuring it's sorted as integers
df_sorted = df_combined.sort_values(by='index', ascending=True)

# Step 6: Save the sorted DataFrame back to a CSV file
output_file = "C:/Users/xgadg/Downloads/66e31d6ee96cd_student_resource_3/student_resource 3/dataset/finallll.csv"
df_sorted.to_csv(output_file, index=False)

# Print the sorted DataFrame (optional)
print(df_sorted)
