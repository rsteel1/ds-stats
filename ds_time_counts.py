import json
import csv
import argparse
import streamlit as st

def main():
    st.title("Watch Time Analyzer")
    
    # File upload section
    st.header("Upload Files")
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

        # Output result to JSON file
        with open("net_platform_watch_time.json", "w") as json_output_file:
            json.dump(date_total_watch_time, json_output_file, indent=4)
            st.success(f"Saved to {json_output_file.name}")

        # Output result to CSV file
        with open("net_platform_watch_time.csv", "w", newline="") as csv_output_file:
            writer = csv.writer(csv_output_file)
            writer.writerow(["date", "total_watch_time"])
            for date, total_watch_time in date_total_watch_time.items():
                writer.writerow([date, total_watch_time])
            st.success(f"Saved to {csv_output_file.name}")

if __name__ == "__main__":
    main()
