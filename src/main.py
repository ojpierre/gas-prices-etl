from extract import extract
from transform import transform
from load import load


def main():
    data = extract()
    transform_data = transform(data)
    load(transform_data)
    print("ETL process is complete!")


if __name__ == "__main__":
    main()
    