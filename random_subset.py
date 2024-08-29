import csv
import random

def create_random_csv_subset(input_file, output_file, subset_size):
    try:
        with open(input_file, 'r', newline='') as infile:
            reader = csv.reader(infile)
            
            # Read all rows
            all_rows = list(reader)
            
            # Separate header and data
            header = all_rows[0]
            data = all_rows[1:]
            
            # Calculate the actual subset size (in case the requested size is larger than the dataset)
            actual_subset_size = min(subset_size, len(data))
            
            # Randomly sample the rows
            subset = random.sample(data, actual_subset_size)
            
            # Write the subset to the output file
            with open(output_file, 'w', newline='') as outfile:
                writer = csv.writer(outfile)
                writer.writerow(header)  # Write the header
                writer.writerows(subset)  # Write the randomly selected rows
        
        print(f"Random subset of {actual_subset_size} rows created successfully in {output_file}")
    
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    input_file = 'ingredients.csv'
    output_file = 'home_items.csv'
    subset_size = 25  # Specify the number of rows you want in your subset
    create_random_csv_subset(input_file, output_file, subset_size)