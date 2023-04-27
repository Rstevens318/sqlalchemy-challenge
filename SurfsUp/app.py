# Import the dependencies.
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import numpy as np
import datetime as dt
from flask import Flask, jsonify, render_template


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///../Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
measurement = Base.classes.measurement
station = Base.classes.station

# Create our session (link) from Python to the DB


#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    """List all available API routes."""
    return (
    #return render_template('home.html')
    f"Welcome to the Hawaii Climate Analysis API!<br/>"
    f"Available Routes:<br/>"
    f"/api/v1.0/precipitation<br/>"
    f"/api/v1.0/stations<br/>"
    f"/api/v1.0/tobs<br/>"
    f"/api/v1.0/<start>enter start date<br/>"
    f"/api/v1.0/<start>/<end> enter start and end date")



@app.route('/api/v1.0/precipitation')
def precipitation():
    session = Session(engine)

    recent_date = session.query(func.max(measurement.date)).scalar()
    recent_date = dt.datetime.strptime(recent_date, "%Y-%m-%d").date()
    year_ago = recent_date - dt.timedelta(days=365)
    results = session.query(measurement.date, measurement.prcp).filter(measurement.date >= year_ago).all()
    
    session.close()

    all_prcp = []
    for date, prcp in results:
        prcp_dict = {}
        prcp_dict[date] = prcp
        all_prcp.append(prcp_dict)

    return jsonify(all_prcp)

@app.route('/api/v1.0/stations')
def stations():
    session = Session(engine)

    results = session.query(station.station).all()

    session.close()

    all_stations = list(np.ravel(results))

    return jsonify(all_stations)

@app.route('/api/v1.0/tobs')
def tobs():
    session = Session(engine)

    recent_date = session.query(func.max(measurement.date)).scalar()
    recent_date = dt.datetime.strptime(recent_date, "%Y-%m-%d").date()
    year_ago = recent_date - dt.timedelta(days=365)

    active_station = session.query(measurement.station, func.count(measurement.station)).group_by(measurement.station).order_by(func.count(measurement.station).desc()).all()

    results = session.query(measurement.date, measurement.tobs).filter(measurement.station == active_station[0][0]).filter(measurement.date >= year_ago).all()

    session.close()

    all_tobs = []
    for date, tobs in results:
        tobs_dict = {}
        tobs_dict[date] = tobs
        all_tobs.append(tobs_dict)

    return jsonify(all_tobs)

@app.route('/api/v1.0/<start>')
def start(start):
    session = Session(engine)

    results = session.query(func.min(measurement.tobs), func.max(measurement.tobs), func.avg(measurement.tobs)).filter(measurement.date >= start).all()

    session.close()

    all_start = []
    data = True
    for min, max, avg in results:
        start_dict = {}
        start_dict["min"] = min
        start_dict["max"] = max
        start_dict["avg"] = avg
        all_start.append(start_dict)

    if data == False:
        return f"Data not found for the given date range. Please enter a new date range."
    else:
        return jsonify(all_start)

@app.route('/api/v1.0/<start>/<end>')
def start_end(start, end):
    session = Session(engine)
    results = session.query(func.min(measurement.tobs), func.max(measurement.tobs), func.avg(measurement.tobs)).filter(measurement.date >= start).filter(measurement.date <= end).all()
    session.close

    from_start_end = []
    data = True
    for min, max, avg in results:
        start_end_dict = {}
        start_end_dict["min"] = min
        start_end_dict["max"] = max
        start_end_dict["avg"] = avg
        from_start_end.append(start_end_dict)

    if data == False:
        return f"Data not found for the given date range. Please enter a new date range."
    else:
        return jsonify(from_start_end)

if __name__ == '__main__':
    app.run(debug=True)