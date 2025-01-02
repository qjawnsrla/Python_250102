from flask import Flask
from routes.sample import subway_info, root_print
from routes.weather import get_sample_weather, get_short_term_weather, get_multiple_locations_weather

app = Flask(__name__)

app.add_url_rule("/", 'root_print', root_print, methods=['GET'])
app.add_url_rule("/api/subway-data",'subway_info',subway_info, methods=['GET'])
app.add_url_rule("/api/weather-sample",'get_sample_weather',get_sample_weather, methods=['GET'])
app.add_url_rule("/api/short-term-weather",'get_short_term_weather',get_short_term_weather, methods=['GET'])
app.add_url_rule("/api/multiple-locations-weather",'get_multiple_locations_weather',get_multiple_locations_weather, methods=['GET'])


if __name__ == '__main__':
    app.run()