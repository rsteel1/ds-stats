import json
import pandas as pd
import streamlit as st
from io import StringIO
import csv

def main():
    st.title("DS Net Time Generator")
    
    # File upload section
    st.header("Paste Dreaming Spanish JSON")
    st.write("This tool calculates the net watch time for each day by subtracting the external watch time from the total watch time.")
    st.write("You need to first save your dayWatchedTime and externalTime as .json files from the Dreaming Spanish progress page using the Developer Tools.")
    st.write("Open Dev Tools -> Network -> Refresh the page -> Select dayWatchedTime -> Select Response -> Select 'View Raw or View Source' -> Copy/Paste to the respective boxes below")
    st.write("Once complete, you can download the results as either .json or .csv to do whatever you like with it.")
    # day_watched_time_file = st.file_uploader("Upload day watched time JSON file", type="json")
    # external_file = st.file_uploader("Upload external time JSON file", type="json")

    st.write("Paste the raw contents of the dayWatchedTime response below:")    
    day_watched_time_data = st.text_area("dayWatchedTime", height=100)
    
    st.write("Paste the raw contents of the externalTime response below:")
    external_text_data = st.text_area("externalTime", height=100)
    
    # add an okay button to proceed
    if st.button("Calculate Net Watch Time"):
        if day_watched_time_data != "" and external_text_data != "":
            # Process uploaded files
            try:
                day_watched_time = json.loads(day_watched_time_data)
                external_data = json.loads(external_text_data)

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

                st.header("Net Watch Time Results")
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

                st.header("Some pretty graphs")
                # Create DataFrame for visualization
                df = pd.DataFrame(day_watched_time)
                df['date'] = pd.to_datetime(df['date'])
                df.set_index('date', inplace=True)

                external_df = pd.DataFrame(external_data['externalTimes'])
                external_df['date'] = pd.to_datetime(external_df['date'])
                external_df.set_index('date', inplace=True)

                df['externalTime'] = external_df['timeSeconds']

                # Plot total watch time
                st.header("Total Watch Time Over Time")
                # Convert timeSeconds to hours
                df['timeHours'] = df['timeSeconds'] / 3600
                df['extenralTimeHours'] = df['externalTime'] / 3600
                
                # Plot total watch time and external watch time in hours
                st.line_chart(df[['timeHours', 'externalTimeHours']], x_label="Date", y_label="Watch Time (hours)")

                st.header("Goal Reached Over Time")
                st.bar_chart(df['goalReached'])
            except Exception as e:
                st.error("Error parsing JSON data, please make sure the data is in the correct format")
                return

if __name__ == "__main__":
    main()