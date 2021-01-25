import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt 
from flask import Flask, jsonify
import numpy as np


engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)

Measurement = Base.classes.measurement
Station = Base.classes.station

app = Flask(__name__)

# Home page
@app.route("/")
def home():
    return (
        f'Welcome to my Home page! <br/>'
        f'<br/>'
        f'Available route: <br/>'
        f'<br/>'
        f'1): <br/>'
        f'/api/v1.0/precipitation <br/>'
        f'<br/>'
        f'2): <br/>'
        f'/api/v1.0/stations <br/>'
        f'<br/>'
        f'3): <br/>'
        f'/api/v1.0/tobs <br/>'
        f'<br/>'
        f'4): Enter the start date in the specified format <br/>'
        f'* Available period from 2010-01-01 to 2017-08-23 <br/>'
        f'/api/v1.0/yyyy-mm-dd <br/>'
        f'<br/>'
        f'5): Enter the start and end date in the specified format <br/>'
        f'* Available period from 2010-01-01 to 2017-08-23 <br/>'
        f'/api/v1.0/yyyy-mm-dd/yyyy-mm-dd'
    )

# Precipitation results
@app.route("/api/v1.0/precipitation")
def prcp():
    session = Session(engine)
    prcp_results = session.query(Measurement.date, Measurement.prcp).all()
    session.close()

    precip = {date: prcp for date, prcp in prcp_results}
    return jsonify(precip)

# List of stations
@app.route("/api/v1.0/stations")
def statn():
    session = Session(engine)
    # statn_results = session.query(Station.station, Station.name).all()
    statn_results = session.query(Station.name).all()
    session.close()

    stations = list(np.ravel(statn_results))
    return jsonify(stations=stations)

# List of temperature observations (TOBS) of the most active station for the previous year
@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)

    most_recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    last_date = dt.datetime.strptime(most_recent_date[0], '%Y-%m-%d')
    year_ago = last_date - dt.timedelta(days = 365)
    
    last_year_tobs = session.query(Measurement.tobs).\
        filter(Measurement.station == 'USC00519281').\
        filter(Measurement.date >= year_ago).order_by(Measurement.date).all()
    
    session.close()

    temps = list(np.ravel(last_year_tobs))
    return jsonify(temps=temps)

# TOBS of given start or start-end range
@app.route("/api/v1.0/<start>")
def tobs_start(start):
    session = Session(engine)
    
    results1 = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()
    
    session.close()

    list1 = []
    for min, avg, max in results1:
        dict1 = {}
        dict1['Lowest Temperature'] = min
        dict1['Average Temperature'] = avg
        dict1['Highest Temperature'] = max
        list1.append(dict1)
    return jsonify(list1)

@app.route("/api/v1.0/<start>/<end>")
def tobs_start_end(start, end):
    session = Session(engine)
    
    results2 = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    
    session.close()

    list2 = []
    for min, avg, max in results2:
        dict2 = {}
        dict2['Lowest Temperature'] = min
        dict2['Average Temperature'] = avg
        dict2['Highest Temperature'] = max
        list2.append(dict2)
    return jsonify(list2)

if __name__ == "__main__":
    app.run(debug=True)