import data_finder
import token_updater
import json

base_url = "https://api.epitest.eu/me"

def get_percent(mouli):
    passed = 0.0
    total = 0.0

    for result in mouli["results"]["skills"]:
        #print("------- " + str(mouli["results"]["skills"][result]))
        total  += int(mouli["results"]["skills"][result]["count"])
        passed += int(mouli["results"]["skills"][result]["passed"])
    if total <= 0:
        return -1.0
    return (passed / total) * 100.0

def parse_data(mouli):
    return f"{mouli["project"]["name"]}:{get_percent(mouli)}\n"

def main():
    token = data_finder.load_token()
    data = data_finder.fetch_data(token, f"{base_url}/2024")

    data.reverse()
    print(f"{data}\n\n\n\n\n\n\n")
    with open("mouli_data", "w") as file:
        for mouli in data:
            file.write(parse_data(mouli))

if __name__ == "__main__":
    main()