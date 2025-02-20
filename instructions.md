# Train Status Scraping Project Instructions

## Project Overview
This project aims to scrape train running status information from confirmtkt.com by automating the process of checking train status with given inputs.

## Required Inputs
1. Train Number - The train number to check status for
2. Day Selection - Integer input (1 for today, 2 for yesterday, etc.)

## Project Steps

### 1. Initial Setup
- Set up Python environment
- Install required packages:
  - selenium (for web automation)
  - webdriver_manager (for Chrome driver management)
  - beautifulsoup4 (for HTML parsing)
  - requests (for HTTP requests)

### 2. Website Navigation
1. Navigate to https://www.confirmtkt.com/train-running-status
2. Locate and interact with the train number input field
3. Enter the provided train number
4. Click on "Check Live Status" button

### 3. Date Selection
1. Wait for the date selection screen to load
2. Based on the day input (1,2,3...), select appropriate date:
   - 1: Today
   - 2: Yesterday
   - 3: Day before yesterday, etc.
3. Click on Submit button

### 4. Data Extraction
1. Wait for the status page to load
2. Extract the following information:
   - Current station (departed from)
   - Next station
   - Last updated time
   - Train delay status (if any)

### 5. Output Handling
1. Format the extracted information
2. Return/save the data in structured format
3. Handle any errors or invalid inputs

## Error Handling
- Handle network connectivity issues
- Handle invalid train numbers
- Handle cases where train is not running
- Handle session timeouts

## Expected Output Format
```json
{
    "train_number": "XXXXX",
    "current_status": {
        "last_station": "Station Name",
        "next_station": "Next Station Name",
        "last_updated": "timestamp",
        "delay_status": "XX mins"
    }
}
```

## Technical Requirements
1. Python 3.7+
2. Chrome/Firefox browser
3. Stable internet connection
4. Required Python packages (listed in requirements.txt) 