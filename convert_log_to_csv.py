import argparse
import math
import json
import csv

def load_log_file(file_path):
    """
    Load a log file and return its content in a format compatible with the parse_log_to_csv function.

    :param file_path: Path to the log file
    :return: String containing the log file data
    """
    try:
        with open(file_path, 'r') as file:
            return file.read()
    except Exception as e:
        return str(e)

# Example usage:
# file_content = load_log_file('path/to/your/logfile.log')
# csv_file_path = parse_log_to_csv(file_content)
def modified_text_length_calculation(data):
    """
    Calculates the length of the text from the 'choices' or '0' key in the data.
    If 'choices' key is present, uses the text from it; otherwise, uses the text from the '0' key.
    The length is calculated by dividing the length of the text by 5 and rounding up.

    :param data: JSON data from the log
    :return: Calculated length of the text
    """
    text = ""
    if "choices" in data:
        text = "".join(choice.get("text", "") for choice in data["choices"])
    elif "0" in data:
        text = data["0"].split("2. Then, ask the sheriff about the details of this strange letter. 3. Finally, suggest a theory about the possible connection between this letter and Mr. Smith's death, and propose your next steps in the investigation.")[-1]

    # Calculate the token count
    token_count = math.ceil(len(text) / 5)
    return token_count

# Example usage in the main parsing function
# Inside the loop, where you parse each line:
# if action == "Invocation":
#     token_count = modified_text_length_calculation(data)
#     # Rest of the code to handle the 'Invocation' action...

def parse_config_and_invocation_log_to_csv(log_data,outputcsv):
    """
    Parses log data to extract specific fields from JSON content for lines containing the 'Configuration' 
    and 'Invocation' actions, and writes this data to a CSV file.

    :param log_data: String containing the log file data
    :return: Path to the created CSV file
    """
    # Split the log data into lines
    lines = log_data.strip().split('\n')
    
    # List to store parsed data
    parsed_data = []
    last_config_model_path = None

    json_str = ""
    inside_json = False

    # Iterate through each line in the log data
    for line in lines:
        # Check if the line indicates the start of JSON data
        if '{' in line and not inside_json:
            json_str = line[line.find('{'):]  # Start capturing JSON string
            inside_json = True
        elif inside_json:
            json_str += line

        # Check if the line indicates the end of JSON data
        if inside_json and '}' in line:
            try:
                data = json.loads(json_str)
                action = data.get("Action")

                if action == "Configuration":
                    last_config_model_path = data.get("model_path") or data.get("pretrained_model_name_or_path")

                if action == "Invocation":
                    # Calculate text length / 5 (rounded up)
                    token_count = modified_text_length_calculation(data)

                    extracted_data = {
                        "roundtrip_time": data.get("roundtrip_time"),
                        "instance_type": data.get("instance_type"),
                        "on_demand_cost": data.get("on_demand_cost"),
                        "total_cost": data.get("total_cost"),
                        "model_path": last_config_model_path,
                        "text_token_count": token_count
                    }
                    parsed_data.append(extracted_data)

                inside_json = False
                json_str = ""
            except json.JSONDecodeError:
                # If JSON parsing fails, reset and continue
                inside_json = False
                json_str = ""
                continue

    # Define CSV file name
    csv_file = outputcsv

    # Writing data to CSV
    with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
        fieldnames = ["roundtrip_time", "instance_type", "on_demand_cost", "total_cost", 
                      "model_path", "text_token_count"]
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(parsed_data)

    return csv_file


def parse_arguments():
    """
    Parse command line arguments for the log file path and the output CSV file path.
    :return: Namespace object with the parsed arguments
    """
    parser = argparse.ArgumentParser(description='Convert log file to CSV format.')
    parser.add_argument('--logpath', type=str, required=True, help='Path to the log file')
    parser.add_argument('--outputcsv', type=str, required=True, help='Path for the output CSV file')
    return parser.parse_args()


def main():
    # Parse the command line arguments
    args = parse_arguments()

    # Load the log file
    log_content = load_log_file(args.logpath)

    # Parse the log and save it to CSV
    csv_file_path = parse_config_and_invocation_log_to_csv(log_content, args.outputcsv)
    print(f"CSV file created at: {csv_file_path}")

    # Execute the main function
if __name__ == "__main__":
    main()