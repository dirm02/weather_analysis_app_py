import sys
import requests
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QLineEdit, QPushButton, QMessageBox,QListWidget)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from datetime import datetime
import random
import numpy as np  # Import numpy for numerical operations
import matplotlib.pyplot as plt

# API key - replace 'YOUR_API_KEY' with your actual Visual Crossing Weather API key
API_KEY = '3KAJKHWT3UEMRQWF2ABKVVVZE'

class WeatherAnalysisApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.current_canvas = None  # This will hold the current canvas widget


    def initUI(self):
        self.setWindowTitle('Weather Data Viewer')
        self.setGeometry(100, 100, 800, 600)  # Adjust window size and position

        # Layouts
        layout = QVBoxLayout()
        form_layout = QHBoxLayout()
        button_layout = QHBoxLayout()
        list_layout = QVBoxLayout()

        # Weather data form
        self.location_label = QLabel('Location:')
        self.location_entry = QLineEdit()
        self.start_date_label = QLabel('Start Date (yyyy-mm-dd):')
        self.start_date_entry = QLineEdit()
        self.end_date_label = QLabel('End Date (yyyy-mm-dd, optional):')
        self.end_date_entry = QLineEdit()
        self.submit_button = QPushButton('Submit')
        self.submit_button.clicked.connect(self.on_submit)

        # Assemble form layout
        form_layout.addWidget(self.location_label)
        form_layout.addWidget(self.location_entry)
        form_layout.addWidget(self.start_date_label)
        form_layout.addWidget(self.start_date_entry)
        form_layout.addWidget(self.end_date_label)
        form_layout.addWidget(self.end_date_entry)

        # Assemble button layout
        button_layout.addWidget(self.submit_button)

        # List widget for displaying weather data history
        self.list_widget = QListWidget()
        list_layout.addWidget(self.list_widget)

        # Add layouts to the main layout
        layout.addLayout(form_layout)
        layout.addLayout(button_layout)
        layout.addLayout(list_layout)

        self.setLayout(layout)
        

    def fetch_weather_data(self, location, start_date, end_date=None):
        base_url = "https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/"
        if end_date:
            url = f"{base_url}{location}/{start_date}/{end_date}?key={API_KEY}"
        elif start_date:
            url = f"{base_url}{location}/{start_date}?key={API_KEY}"
        else:
            url = f"{base_url}{location}?key={API_KEY}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            QMessageBox.critical(self, 'Error', f'Failed to fetch data: {str(e)}')
            return None

    def on_submit(self):
        location = self.location_entry.text()
        start_date = self.start_date_entry.text()
        end_date = self.end_date_entry.text() or None

        if not location:
            QMessageBox.critical(self, 'Error', 'Location are required!')
            return

        weather_data = self.fetch_weather_data(location, start_date, end_date)
        if weather_data:
            results = self.plot_weather_data(weather_data)
            self.update_list_widget(start_date, end_date, *results)
            self.showMaximized()

    def update_list_widget(self, startdate, enddate, max_temp, min_temp, avg_temp, max_humidity, min_humidity, avg_humidity, max_precip, min_precip, avg_precip, max_wind, min_wind, avg_wind):
        # Generate entry string as before and add to the list widget
        entry = f"From: {startdate} To: {enddate} Max Temperature: {max_temp}°C, Min Temperature: {min_temp}°C, Avg Temperature: {avg_temp}°C, " \
                f"Max Humidity: {max_humidity}%, Min Humidity: {min_humidity}%, Avg Humidity: {avg_humidity}%, " \
                f"Max Precipitation: {max_precip}mm, Min Precipitation: {min_precip}mm, Avg Precipitation: {avg_precip}mm, " \
                f"Max Wind Speed: {max_wind}km/h, Min Wind Speed: {min_wind}km/h, Avg Wind Speed: {avg_wind}km/h"
        self.list_widget.addItem(entry)

    def plot_weather_data(self, weather_data):
        try:       
            if self.current_canvas:  # Check if there is a canvas already displayed
                self.layout().removeWidget(self.current_canvas)  # Remove the old canvas from the layout
                self.current_canvas.deleteLater()  # Ensure it's deleted properly
     
            days = weather_data['days']
            dates = [datetime.strptime(day['datetime'], '%Y-%m-%d') for day in days]
            temperatures = [day.get('temp', None) for day in days]
            humidities = [day.get('humidity', None) for day in days]
            precipitations = [day.get('precip', None) for day in days]
            wind_speeds = [day.get('windspeed', None) for day in days]
            
            max_temp = max(temperatures)
            min_temp = min(temperatures)
            avg_temp = np.mean(temperatures)

            max_humidity = max(humidities)
            min_humidity = min(humidities)
            avg_humidity = np.mean(humidities)

            max_precip = max(precipitations)
            min_precip = min(precipitations)
            avg_precip = np.mean(precipitations)

            max_wind = max(wind_speeds)
            min_wind = min(wind_speeds)
            avg_wind = np.mean(wind_speeds)
            
            # Create a figure with multiple subplots
            fig = Figure(figsize=(10, 8))  # Adjust size as needed

            # Temperature Plot
            ax1 = fig.add_subplot(221)  # 4 rows, 1 column, 1st subplot
            ax1.plot(dates, temperatures, 'r-')
            ax1.set_title('Daily Temperatures')
            ax1.set_ylabel('Temperature (°C)')
            ax1.grid(True)

            ax1.axhline(y=max_temp, color='r', linestyle='--', label=f'Max Temp: {max_temp}°C')
            ax1.axhline(y=min_temp, color='b', linestyle='--', label=f'Min Temp: {min_temp}°C')
            ax1.axhline(y=avg_temp, color='g', linestyle='--', label=f'Avg Temp: {avg_temp:.2f}°C')
            ax1.legend()

            # Humidity Plot
            ax2 = fig.add_subplot(222)  # 4 rows, 1 column, 2nd subplot
            ax2.plot(dates, humidities, 'b-')
            ax2.set_title('Daily Humidity')
            ax2.set_ylabel('Humidity (%)')
            ax2.grid(True)

            ax2.axhline(y=max_humidity, color='r', linestyle='--', label=f'Max Humidity: {max_humidity}%')
            ax2.axhline(y=min_humidity, color='b', linestyle='--', label=f'Min Humidity: {min_humidity}%')
            ax2.axhline(y=avg_humidity, color='g', linestyle='--', label=f'Avg Humidity: {avg_humidity:.2f}%')
            ax2.legend()

            # Precipitation Plot
            ax3 = fig.add_subplot(223)  # 4 rows, 1 column, 3rd subplot
            ax3.plot(dates, precipitations, 'g-')
            ax3.set_title('Daily Precipitation')
            ax3.set_ylabel('Precipitation (mm)')
            ax3.grid(True)
            
            ax3.axhline(y=max_precip, color='r', linestyle='--', label=f'Max Precipitation: {max_precip}mm')
            ax3.axhline(y=min_precip, color='b', linestyle='--', label=f'Min Precipitation: {min_precip}mm')
            ax3.axhline(y=avg_precip, color='g', linestyle='--', label=f'Avg Precipitation: {avg_precip:.2f}mm')
            ax3.legend()

            # Wind Speed Plot
            ax4 = fig.add_subplot(224)  # 4 rows, 1 column, 4th subplot
            ax4.plot(dates, wind_speeds, 'm-')
            ax4.set_title('Daily Wind Speed')
            ax4.set_ylabel('Wind Speed (km/h)')
            ax4.grid(True)

            ax4.axhline(y=max_wind, color='r', linestyle='--', label=f'Max Wind Speed: {max_temp}km/h')
            ax4.axhline(y=min_wind, color='b', linestyle='--', label=f'Min Wind Speed: {min_temp}km/h')
            ax4.axhline(y=avg_wind, color='g', linestyle='--', label=f'Avg Wind Speed: {avg_temp:.2f}km/h')
            ax4.legend()

            # Layout adjustment to prevent overlap
            fig.tight_layout()

            # Embed the plot in the PyQt5 window
            self.current_canvas = FigureCanvas(fig)  # Create a new canvas
            self.layout().addWidget(self.current_canvas)  # Add new canvas to the layout
            self.current_canvas.draw()
            
            return max_temp, min_temp, avg_temp, max_humidity, min_humidity, avg_humidity, max_precip, min_precip, avg_precip, max_wind, min_wind, avg_wind

        except KeyError:
            QMessageBox.critical(self, 'Error', 'Error processing weather data. Please check the data format and dates.')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = WeatherAnalysisApp()
    ex.show()
    sys.exit(app.exec_())
