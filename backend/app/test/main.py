from apirequest import get_weather
from apirequest import transform_data
from apirequest import save_data


def main():
    print("Starting backend test…")
    api_data = get_weather()
    #transform_data(api_data)

    save_data_result = transform_data(api_data)
    save_data(save_data_result)

if __name__ == "__main__":
    main()