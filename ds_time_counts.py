import json
import pandas as pd
import streamlit as st
from io import StringIO
import csv

def main():
    st.title("DS Data Analysis")
    
    # File upload section
    st.header("Paste Dreaming Spanish JSON")
    st.markdown("""
    This tool generates some graphs and calculates the net watch time for each day by subtracting the external watch time from the total watch time.

    1. Go to Dreaming Spanish Progress page
    2. Open Dev Tools -> Network -> Refresh the page -> Select `dayWatchedTime` -> Select `Response` -> Select 'View Raw or View Source' -> Copy/Paste to the respective boxes below
    3. Do the same for 'externalTime'
    4. Click 'Run Calculation' to generate the results
    Once complete, you can download the net watch time results as either .json or .csv to do whatever you like with it.
    We'll also make some graphs just for fun.
    
    Enjoy!
    Your friendly neighbourhood Potato
    """)
    
    st.write("Paste the raw contents of the dayWatchedTime response below:")    
    day_watched_time_data = st.text_area("dayWatchedTime", height=100)
    
    st.write("Paste the raw contents of the externalTime response below:")
    external_text_data = st.text_area("externalTime", height=100)
    
    # add an okay button to proceed
    if st.button("Run Calculation"):
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
                
                external_df = pd.DataFrame(external_data["externalTimes"])
                external_df['date'] = pd.to_datetime(external_df['date'])
                external_df.set_index('date', inplace=True)

                # Convert timeSeconds to hours in external_df
                external_df['timeHours_external'] = external_df['timeSeconds'] / 3600
                external_df['timeHours_total'] = 0

                # Convert timeSeconds to hours in df
                df['timeHours_total'] = df['timeSeconds'] / 3600
                df['timeHours_external'] = 0

                # Concatenate the two DataFrames
                combined_df = pd.concat([df, external_df])

                # Sort the DataFrame by date
                combined_df.sort_index(inplace=True)

                # # Debug: Print DataFrame to inspect values
                # st.write("Debug: DataFrame after concatenation and sorting")
                # st.write(combined_df)

                # Calculate average watch time
                combined_df['average_watch_time'] = combined_df[combined_df['timeHours_total'] > 0]['timeHours_total'].expanding().mean()

                # Plot total watch time and external watch time in hours
                st.header("Total Watch Time and Average Watch Time Over Time")
                st.line_chart(combined_df[(combined_df['timeHours_total'] > 0)][['timeHours_total', 'average_watch_time']], x_label="Date", y_label="Watch Time (hours)")
                st.header("External Watch Time Over Time")
                st.line_chart(combined_df[(combined_df['timeHours_external'] > 0)][['timeHours_external']], x_label="Date", y_label="External Watch Time (hours)")

                # Convert timeSeconds to hours in external_df
                external_df['timeHours_external'] = external_df['timeSeconds'] / 3600
                external_df['timeHours_total'] = 0

                # Calculate total time spent on each type of content
                type_metrics = external_df[external_df['type'] != 'initial'].groupby('type')['timeHours_external'].sum()

                # Calculate total time spent on each description
                description_metrics = external_df.groupby('description')['timeHours_external'].sum()

                # Display the metrics
                st.header("Total Time Spent on Each Type of External Content")
                st.bar_chart(type_metrics, x_label="type", y_label="Time Spent (hours)")

                st.header("Total Time Spent on Each External Description")
                with st.expander("Show Description Metrics"):
                    st.table(description_metrics.reset_index())
                st.bar_chart(description_metrics, x_label="description", y_label="Time Spent (hours)")

                # Calculate total time spent and total external time spent
                total_time_spent = combined_df['timeHours_total'].sum()
                total_external_time_spent = combined_df['timeHours_external'].sum()

                # Display the metrics
                st.metric("Total Time Spent", f"{total_time_spent} hours")
                st.metric("Total External Time Spent", f"{total_external_time_spent} hours")

                st.header("Goal Reached Over Time")
                st.bar_chart(df['goalReached'], x_label="Date", y_label="Goal Reached")
            except Exception as e:
                st.error(str(e))
                return

if __name__ == "__main__":
    main()