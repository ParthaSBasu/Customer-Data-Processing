# Data Processing Application

A Flask application that processes Excel data, cleans it, stores it in a MySQL database, and provides a REST API to access the data.

## Features

- Excel data processing and cleaning
- MySQL database integration
- REST API endpoint for accessing processed data
- Automated data validation and standardization


## API Endpoints

- `GET /table` - Returns the processed customer data in JSON format


## Data Processing Steps

1. Read Excel data
2. Remove duplicates and unnecessary columns
3. Clean and standardize phone numbers
4. Split address into components
5. Standardize categorical values (Yes/No to Y/N)
6. Handle missing values
7. Filter out records based on business rules
8. Store processed data in MySQL
9. Serve data via API endpoint

