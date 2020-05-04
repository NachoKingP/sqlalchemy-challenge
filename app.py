from flask import Flask, jsonify
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect
import datetime as dt

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///hawaii.sqlite", echo=True)

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to tables
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)


#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    return (
        f"Welcome to the Hawaii Weather API!<br/>"
        f"Available Routes:<br/>"
        f"To return a list of precipitation from the past year, append: /api/v1.0/precipitation<br/>"
        f"To return a JSON list of weather stations, append: /api/v1.0/stations<br/>"
        f"To return a JSON list of weather observations, append: /api/v1.0/tobs<br/>"
        f"To return a JSON list of the tmin, tmax, and tavg for the dates greater than the value specified, append: /api/v1.0/<start><br/>"
        f"To return a JSON list of the tmin, tmax, and tavg for a date range, append: /api/v1.0/<start>/<end>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return the JSON representation of the precipitation data."""
    #Retreive max date data from engine into tuple and retreive first element of tuple
    max_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    max_date = max_date[0]
    
    #Calculate the date 1 year ago from today
    year_ago = dt.datetime.strptime(max_date, "%Y-%m-%d") - dt.timedelta(days=366)
    
    #Return the precipitation and put it into a dictionary for returning
    results_precipitation = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= year_ago).all()
    precipitation_dict = dict(results_precipitation)
    
    #Return JSONified data from dictionary
    return jsonify(precipitation_dict)


@app.route("/api/v1.0/stations")
def stations():
    """Return a JSON list of stations from the dataset."""
    #Pull station data from engine
    results_stations = session.query(Measurement.station).group_by(Measurement.station).all()
    
    #Convert data into list for returning
    stations_list = list(np.ravel(results_stations))
    
    #Return JSONified data from list
    return jsonify(stations_list)


@app.route("/api/v1.0/tobs")
def tobs():
    """Return a JSON list of temperature observations (TOBS) for the previous year."""
    #Retreive max date data from engine into tuple and retreive first element of tuple
    max_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    max_date = max_date[0]
    
    #Calculate the date 1 year ago from today
    year_ago = dt.datetime.strptime(max_date, "%Y-%m-%d") - dt.timedelta(days=366)
    
    #Return the observation data
    results_tobs = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= year_ago).all()
    
    #Convert data into list for returning
    tobs_list = list(results_tobs)
    
    #Return JSONified data from list
    return jsonify(results_tobs)


@app.route("/api/v1.0/<start>")
def start(start=None):
    """Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start date."""
    
    #Pull data from engine for dates after start date specified
    start_data = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).group_by(Measurement.date).all()
    
    #Convert data into list for returning
    start_list=list(start_data)
    
    #Return JSONified data from list
    return jsonify(start_list)


@app.route("/api/v1.0/<start>/<end>")
def start_end(start=None, end=None):
    """Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given date range."""
    
    #Pull data from engine for dates range specified
    range_data = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).group_by(Measurement.date).all()
    
    #Convert data into list for returning
    range_list=list(range_data)
    
    #Return JSONified data from list
    return jsonify(range_list)


if __name__ == "__main__":
    app.run(debug=True)
