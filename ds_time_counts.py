import json
import csv
import argparse
import streamlit as st
from io import StringIO

def main():
    st.title("DS Net Time Generator")
    
    # File upload section
    st.header("Upload Files")
    st.write("This tool calculates the net watch time for each day by subtracting the external watch time from the total watch time.")
    st.write("You need to first save your dayWatchedTime and externalTime as .json files from the Dreaming Spanish progress page using the Developer Tools.")
    st.write("Open Dev Tools -> Network -> Refresh the page -> Select dayWatchedTime -> Select Response -> Select 'View Raw or View Source' -> Copy/Paste to a new .json file")
    st.write("Once complete, you can download the results as either .json or .csv to do whatever you like with it.")
    day_watched_time_file = st.file_uploader("Upload day watched time JSON file", type="json")
    external_file = st.file_uploader("Upload external JSON file", type="json")
    
    if day_watched_time_file is not None and external_file is not None:
        # Process uploaded files
        day_watched_time = json.load(day_watched_time_file)
        external_data = json.load(external_file)

        date_total_watch_time = {}

        for day in day_watched_time:
            day_date = day["date"]
            day_watch_time = day["timeSeconds"]
            date_total_watch_time[day_date] = day_watch_time

        for external_entry in external_data["externalTimes"]:
            external_date = external_entry["date"]
            external_time = external_entry["timeSeconds"]
            if external_date in date_total_watch_time:
                date_total_watch_time[external_date] -= external_time

        # Generate JSON content
        json_output = json.dumps(date_total_watch_time, indent=4)
        
        # Generate CSV content
        csv_output = StringIO()
        writer = csv.writer(csv_output)
        writer.writerow(["date", "total_watch_time"])
        for date, total_watch_time in date_total_watch_time.items():
            writer.writerow([date, total_watch_time])
        csv_output.seek(0)

        # Provide download buttons
        st.download_button(
            label="Download JSON file",
            data=json_output,
            file_name="net_platform_watch_time.json",
            mime="application/json"
        )
        
        st.download_button(
            label="Download CSV file",
            data=csv_output.getvalue(),
            file_name="net_platform_watch_time.csv",
            mime="text/csv"
        )

if __name__ == "__main__":
    main()