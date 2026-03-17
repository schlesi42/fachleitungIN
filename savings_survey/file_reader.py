import csv

def read_csv_to_dict(filename: str) -> dict[str, list[str]]:
    """
    Reads a CSV file and returns a dictionary where keys are column names
    and values are lists containing the values for each column.
    
    Args:
        filename (str): Path to the CSV file
        
    Returns:
        dict: Dictionary with column names as keys and lists of values
    """
    result = {}
    
    with open(filename, 'r', encoding='utf-8') as file:
        # Use csv.DictReader which automatically uses first line as headers
        reader = csv.DictReader(file, delimiter=';')
        
        # Initialize lists for each column
        for fieldname in reader.fieldnames:
            result[fieldname] = []
        
        # Read each row and append values to respective column lists
        for row in reader:
            for key, value in row.items():
                result[key].append(value)
    
    return result


if __name__ == '__main__':
    filename = "data/data.csv"
    d = read_csv_to_dict(filename)
    print(d)
