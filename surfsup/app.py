# Import the dependencies.
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, and_
import datetime as dt
from flask import Flask, jsonify
import pandas as pd
import os

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///surfsup/Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect = True)

# Save references to each table
measurement = Base.classes.get('measurement')
station = Base.classes.get('station')


# Create our session (link) from Python to the DB
session = Session(engine)
station = session.query(station.station).all()
print(station)
#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    """Welcome to my API webpage."""
    return (
        "Available Routes:<br/>"
        "/api/v1.0/precipitation<br/>"
        "/api/v1.0/stations<br/>"
        "/api/v1.0/tobs<br/>"
        "/api/v1.0/<start>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return 12 months of prcp data"""
    recent = session.query(func.max(measurement.date)).scalar()

    year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    query = session.query(measurement.date, measurement.prcp).filter(
        and_(measurement.date >= year, measurement.date <= recent))
    r = query.all()

    precip = {date: prcp for date, prcp in r}

    return jsonify(precipitation=precip)

@app.route("/api/v1.0/stations")
def stations_list():
    """Return a list of stations"""
    r = session.query(station.station).all()
    s = [station[0] for station in r]  

    return jsonify(stations=s)

@app.route("/api/v1.0/tobs/<station_id>")
def tobs(station_id):

    """Return a JSON list of temperature observations for the previous year."""
    recent = session.query(func.max(measurement.date)).scalar()
    e_date = dt.date.today()
    s_date = e_date - dt.timedelta(days=365)
    query = session.query(measurement.tobs).filter(
    and_(measurement.station == station_id, measurement.date >= s_date, measurement.date <= recent)
       )
    temps = query.all()

    val  = [temp[0] for temp in temps]

    return jsonify({station_id: val})
    
@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end=None):
    """Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start or start-end range."""


    if end is None:
        end = dt.date.today()


    try:
        start_date = dt.datetime.strptime(start, '%Y-%m-%d').date()
        end_date = dt.datetime.strptime(end, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({"error": "Invalid date format. Please use YYYY-MM-DD."}), 400

   
    t_query = session.query(
        func.min(measurement.tobs),
        func.avg(measurement.tobs),
        func.max(measurement.tobs)
    ).filter(and_(measurement.date >= start_date, measurement.date <= end_date)).all()


    if not t_query:
        return jsonify({"error": f"No data found for the specified date range from {start} to {end}."}), 404


    tmin, tavg, tmax = t_query[0]

    return jsonify({
        "start_date": start,
        "end_date": end,
        "TMIN": tmin,
        "TAVG": tavg,
        "TMAX": tmax
    })
if __name__ == '__main__':
    app.run(debug=True)

