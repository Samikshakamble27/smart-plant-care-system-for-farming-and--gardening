import streamlit as st
import pandas as pd
from sklearn.tree import DecisionTreeClassifier
import requests
from main_app import disease

# Load the dataset from CSV file
file_path = '1.csv'  # Replace with the actual path to your CSV file
df = pd.read_csv(file_path)

# Train a simple Decision Tree model
X = df.drop('label', axis=1)
y = df['label']

model = DecisionTreeClassifier()
model.fit(X, y)

# Function to predict crop label
def predict_crop_label(user_inputs):
    prediction = model.predict(pd.DataFrame([user_inputs]))
    return prediction[0]

def main():
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Home", "Crop Prediction", 'Statistics','Disease'])

    if page == "Home":
        home()
    elif page == "Crop Prediction":
        crop_prediction()
    elif page == 'Statistics':
        stats()
    elif page == 'Disease':
        disease()

def home():
    st.title("Welcome to the Crop Prediction App")
    st.write("This app helps you predict the crop label based on input features.")

def crop_prediction():
    st.title('Crop Prediction Dashboard')
    st.header('User Input Features')

    # Define the grid layout
    columns = st.columns(2)

    # User input for prediction
    # columns[0].header('User Input Features')

    # Collect user inputs
    user_inputs = {
        'N': columns[0].slider('Nitrogen (N)', min_value=0, max_value=100, value=50),
        'P': columns[0].slider('Phosphorus (P)', min_value=0, max_value=100, value=50),
        'K': columns[0].slider('Potassium (K)', min_value=0, max_value=100, value=50),
        'temperature': columns[1].slider('Temperature', min_value=0.0, max_value=40.0, value=25.0),
        'humidity': columns[1].slider('Humidity', min_value=0.0, max_value=100.0, value=50.0),
        'ph': columns[1].slider('pH', min_value=0.0, max_value=14.0, value=7.0),
        'rainfall': columns[1].slider('Rainfall', min_value=0.0, max_value=300.0, value=150.0),
    }

    # Display the user inputs
    # st.write('## User Input Features')
    # st.write(pd.DataFrame(user_inputs, index=[0]))

    # Predict the label
    prediction = predict_crop_label(user_inputs)
    st.write('## Prediction')
    st.write(f'The predicted crop label is: {prediction}')

# def stats():
def get_firebase_data(reference_url):
    try:
        response = requests.get(reference_url + '.json')
        data = response.json()
        return data
    except Exception as e:
        st.error(f"Error occurred: {e}")

def set_relay_status(reference_url, new_status):
    try:
        # Define the new status
        # new_status = "true"
        
        # Create the data payload for the PUT request
        # data = {"Relay": new_status}
        
        # Send the PUT request to update the relay status
        response = requests.put(reference_url + '/Relay.json', json=new_status)
        
        # Check the response status code
        if response.status_code == 200:
            print("Relay status updated successfully!")
        else:
            print("Failed to update relay status.")
            
    except Exception as e:
        print(f"Error occurred: {e}")

# # Function to update relay status in Firebase
# def update_relay_status(reference_url, new_status):
#     try:
#         # Convert boolean value to string ("true" or "false")
#         new_status_str = "true" if new_status else "false"
        
#         response = requests.put(reference_url + '/Relay.json', json=new_status_str)
#         if response.status_code == 200:
#             st.success("Relay status updated successfully!")
#         else:
#             st.error("Failed to update relay status.")
#     except Exception as e:
#         st.error(f"Error occurred: {e}")
def update_motor_limit(reference_url, high_limit, low_limit):
    try:
        # Create the data payload for the PUT request
        data = {"high": high_limit, "low": low_limit}
        
        # Send the PUT request to update the motor limit
        response = requests.put(reference_url + '/Motor_limit.json', json=data)
        
        # Check the response status code
        if response.status_code == 200:
            st.success("Motor limit updated successfully!")
        else:
            st.error("Failed to update motor limit.")
            
    except Exception as e:
        st.error(f"Error occurred: {e}")

def stats():
    # Firebase reference URL
    reference_url = "https://samiksha-fda98-default-rtdb.firebaseio.com/"

    if reference_url:
        # Fetch data from Firebase
        data = get_firebase_data(reference_url)

        if data:
            # Extract data fields from JSON
            motor_limit = data.get("Motor_limit", {})
            high_limit = motor_limit.get("high", None)
            low_limit = motor_limit.get("low", None)
            humidity = data.get("Humidity", None)
            soil_moisture = data.get("Soil Moisture", None)
            temperature = data.get("Temperature", None)
            relay_status = data.get("Relay", None)

            # Display data using Streamlit columns
            st.title("Data from Firebase:")
            col1, col2 = st.columns(2)

            col1.header(f'Humidity: {humidity}')
            col1.header(f'Soil Moisture: {soil_moisture}')
            col2.header(f'Temperature: {temperature}')

        # Form to update motor limit
            st.title("Update Soil Moisture Limit:")
            col3, col4 = st.columns(2)
            high_input = col3.number_input("High Limit", value=high_limit)
            low_input = col4.number_input("Low Limit", value=low_limit)
            if st.button("Update Motor Limit"):
                update_motor_limit(reference_url, high_input, low_input)



            # col3.write(f'High Limit: {high_limit}')
            # col4.write(f'Low Limit: {low_limit}')

            # col2.write(f'Relay Status: {relay_status}')
            # Check if Relay key exists in data
            col5, col6 = st.columns(2)
            if 'Relay' in data:
                relay_status = data['Relay']
                if relay_status == 'false':
                    col5.write("Motor Satus: OFF")
                    if col6.button("Turn ON Motor"):
                        set_relay_status(reference_url, 'true')
                        st.experimental_rerun()
                else:
                    col5.write("Motor Satus: ON")
                    if col6.button("Turn OFF Motor"):
                        set_relay_status(reference_url, 'false')
                        st.experimental_rerun()

                # Convert string relay status to boolean
                # relay_status_bool = relay_status == "true"

                # # Button to toggle relay status
                # new_relay_status = not relay_status_bool
                # if st.button("Toggle Relay"):
                #     update_relay_status(reference_url, new_relay_status)
        else:
            st.warning("No data found in Firebase.")

        if st.button('Refresh', type="primary"):
            st.experimental_rerun()


if __name__ == "__main__":
    main()
