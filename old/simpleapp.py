import streamlit as st
from collections import defaultdict
import pandas as pd
import matplotlib.pyplot as plt

# Initialize session state to store user preferences
if 'user_preferences' not in st.session_state:
    st.session_state.user_preferences = defaultdict(lambda: defaultdict(int))

# Define event dates and times
event_schedule = {
    "Friday 14/02/2025": ["18:00", "19:00", "20:00"],
    "Saturday 15/02/2025": ["17:00", "18:00", "19:00"],
    "Sunday 16/02/2025": ["16:00", "17:00", "18:00"],
}

# Title of the app
st.title("Event Scheduler")

# User input form
with st.form("preference_form"):
    st.write("Choose your preferred date and time for the event:")
    
    # Input field for user name
    user_name = st.text_input("Your Name", key="user_name")
    
    # Display dates as headers and times as checkboxes
    selected_times = {}  # To store the selected times for each date
    for date, times in event_schedule.items():
        st.write(f"### {date}")
        selected_times[date] = []
        for time in times:
            if st.checkbox(f"{time}", key=f"{date}_{time}"):
                selected_times[date].append(time)
    
    # Submit button
    submitted = st.form_submit_button("Submit Preference")
    
    if submitted:
        if user_name:
            # Store the user's preferences
            for date, times in selected_times.items():
                for time in times:
                    st.session_state.user_preferences[date][time] += 1
            st.success(f"Thank you, {user_name}! Your preferences have been recorded.")
        else:
            st.error("Please enter your name.")

# Display current preferences
st.write("### Current Preferences")
for date, times in st.session_state.user_preferences.items():
    for time, votes in times.items():
        st.write(f"- **{date} at {time}**: {votes} votes")

# Determine the final event date and time
if st.button("Calculate Final Event Date and Time"):
    max_votes = -1
    best_date, best_time = None, None
    
    for date, times in st.session_state.user_preferences.items():
        for time, votes in times.items():
            if votes > max_votes:
                max_votes = votes
                best_date = date
                best_time = time
    
    if best_date and best_time:
        st.success(f"### Final Event Date and Time: **{best_date} at {best_time}**")
    else:
        st.warning("No preferences have been submitted yet.")
        
if st.button("Reset Preferences"):
    st.session_state.user_preferences = defaultdict(lambda: defaultdict(int))
    st.success("Preferences have been reset.")
        
# Convert preferences to a DataFrame
votes_data = []
for date, times in st.session_state.user_preferences.items():
    for time, votes in times.items():
        votes_data.append({"Date": date, "Time": time, "Votes": votes})
df = pd.DataFrame(votes_data)

# Plot the votes
if not df.empty:
    st.write("### Votes Visualization")
    fig, ax = plt.subplots()
    df.set_index(["Date", "Time"]).plot(kind="bar", ax=ax)
    st.pyplot(fig)