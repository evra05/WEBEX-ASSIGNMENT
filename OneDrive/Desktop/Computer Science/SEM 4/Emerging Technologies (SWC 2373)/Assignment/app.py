from flask import Flask, render_template, request, redirect, url_for
import requests

app = Flask(__name__)

# Webex API base URL
WEBEX_BASE_URL = "https://webexapis.com/v1"

# Route for the home page where the user enters the Webex token
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        access_token = request.form['access_token']
        return redirect(url_for('menu', access_token=access_token))
    return render_template('index.html')

# Route for the main menu
@app.route('/menu/<access_token>', methods=['GET'])
def menu(access_token):
    return render_template('menu.html', access_token=access_token)

# Test connection to the Webex server
@app.route('/test_connection/<access_token>', methods=['GET'])
def test_connection(access_token):
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    response = requests.get(f"{WEBEX_BASE_URL}/people/me", headers=headers)
    
    # Check if the request was successful
    if response.status_code == 200:
        message = "Connection to Webex server successful!"
    else:
        message = "Failed to connect to Webex server."
    
    # Render the template and pass both the message and access_token
    return render_template('test_connection.html', message=message, access_token=access_token)

# Display user information with avatar
@app.route('/user_info/<access_token>', methods=['GET'])
def user_info(access_token):
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    # Make API request to get user info
    response = requests.get(f"{WEBEX_BASE_URL}/people/me", headers=headers)
    
    if response.status_code == 200:
        user_info = response.json()
        # Safely access 'emails' and other fields to prevent KeyError or NoneType errors
        user_email = user_info.get('emails', ['No email available'])[0]  # Get the first email, or a default message
        display_name = user_info.get('displayName', 'No name available')
        avatar_url = user_info.get('avatar', None)
    else:
        user_info = None
        user_email = 'Error retrieving email'
        display_name = 'Error retrieving name'
        avatar_url = None
    
    # Pass the data to the template
    return render_template(
        'user_info.html', 
        user_info=user_info, 
        user_email=user_email, 
        display_name=display_name, 
        avatar_url=avatar_url,
        access_token=access_token
    )


# Display Rooms
@app.route('/rooms/<access_token>', methods=['GET', 'POST'])
def rooms(access_token):
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    response = requests.get(f"{WEBEX_BASE_URL}/rooms", headers=headers)
    
    # Get rooms and limit to 5 for demonstration
    rooms = response.json().get('items', [])[:5] if response.status_code == 200 else []
    
    if request.method == 'POST':
        room_id = request.form['room_id']
        message = request.form['message']
        message_response = send_message_to_room(access_token, room_id, message)
        return render_template('rooms.html', rooms=rooms, access_token=access_token, message=message_response)
    
    return render_template('rooms.html', rooms=rooms, access_token=access_token)

# Room Info Page with Delete Room Functionality
@app.route('/room_info/<access_token>/<room_id>', methods=['GET', 'POST'])
def room_info(access_token, room_id):
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    # Retrieve room details
    room_response = requests.get(f"{WEBEX_BASE_URL}/rooms/{room_id}", headers=headers)
    if room_response.status_code == 200:
        room = room_response.json()  # Get room details as JSON
    else:
        room = None

    # Handle delete room request
    if request.method == 'POST' and 'delete_room' in request.form:
        delete_response = requests.delete(f"{WEBEX_BASE_URL}/rooms/{room_id}", headers=headers)
        if delete_response.status_code == 204:
            message = "Room deleted successfully!"
            return redirect(url_for('rooms', access_token=access_token))  # Redirect back to rooms list
        else:
            message = "Failed to delete room."
            
    return render_template('room_info.html', room=room, access_token=access_token)




# Create a room
@app.route('/create_room/<access_token>', methods=['GET', 'POST'])
def create_room(access_token):
    if request.method == 'POST':
        room_title = request.form['room_title']
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        payload = {"title": room_title}
        response = requests.post(f"{WEBEX_BASE_URL}/rooms", headers=headers, json=payload)
        if response.status_code == 200:
            message = "Room created successfully!"
        else:
            message = "Failed to create room."
        return render_template('create_room.html', access_token=access_token, message=message)
    
    return render_template('create_room.html', access_token=access_token)

# Send message to a room
def send_message_to_room(access_token, room_id, message):
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    payload = {"roomId": room_id, "text": message}
    response = requests.post(f"{WEBEX_BASE_URL}/messages", headers=headers, json=payload)
    if response.status_code == 200:
        return "Message sent successfully!"
    else:
        return "Failed to send message."
    
    # Logout route
@app.route('/logout')
def logout():
    # Redirect to the homepage (index) after logout
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
