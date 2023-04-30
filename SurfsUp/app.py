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

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

#Define Homepage Route with a list of all available routes
#Use a function to return a homepage .html template file
@app.route("/", methods=['GET', 'POST'])
def welcome():
    """List all available API routes."""
    return render_template('home.html')


@app.route('/api/v1.0/precipitation')
def precipitation():

    # Create our session (link) from Python to the DB
    session = Session(engine)

    #Find the most recent date in our DB and convert to string format
    recent_date = session.query(func.max(measurement.date)).scalar()
    recent_date = dt.datetime.strptime(recent_date, "%Y-%m-%d").date()

    #Calculate the date 1 year ago from the most recent date
    year_ago = recent_date - dt.timedelta(days=365)

    #Query for the date and precipitation for the last year of data
    results = session.query(measurement.date, measurement.prcp).filter(measurement.date >= year_ago).all()
    
    #Close the session
    session.close()

    #Create a dictionary from the provided data and append to a list of the precipitation data
    all_prcp = []

    for date, prcp in results:
        prcp_dict = {}
        prcp_dict[date] = prcp
        all_prcp.append(prcp_dict)

    #Return the JSON representation of your dictionary.
    return jsonify(all_prcp)

@app.route('/api/v1.0/stations')
def stations():

    # Create our session (link) from Python to the DB
    session = Session(engine)

    #Query all stations
    results = session.query(station.station).all()

    #Close the session
    session.close()

    #Convert to flattened array
    all_stations = list(np.ravel(results))

    #Return a JSON list of stations from the dataset.
    return jsonify(all_stations)

@app.route('/api/v1.0/tobs')
def tobs():

    # Create our session (link) from Python to the DB
    session = Session(engine)

    #Find the most recent date in our DB and convert to string format
    recent_date = session.query(func.max(measurement.date)).scalar()
    recent_date = dt.datetime.strptime(recent_date, "%Y-%m-%d").date()

    #Calculate the date 1 year ago from the most recent date
    year_ago = recent_date - dt.timedelta(days=365)

    #Find the most active station
    active_station = session.query(measurement.station, func.count(measurement.station)).group_by(measurement.station).order_by(func.count(measurement.station).desc()).all()

    #Query the dates and temperature observations of the most active station for the last year of data.
    results = session.query(measurement.date, measurement.tobs).filter(measurement.station == active_station[0][0]).filter(measurement.date >= year_ago).all()

    #Close the session
    session.close()

    #Create a dictionary from the provided data and append to a list of the temperature data
    all_tobs = []

    for date, tobs in results:
        tobs_dict = {}
        tobs_dict[date] = tobs
        all_tobs.append(tobs_dict)

    #Return the JSON representation of your dictionary.
    return jsonify(all_tobs)

@app.route('/api/v1.0/<start>')
def start(start):
 
    # Create our session (link) from Python to the DB
    session = Session(engine)

    #Query for the dates and temperature observations from the start date.
    results = session.query(func.min(measurement.tobs), func.max(measurement.tobs), func.avg(measurement.tobs)).filter(measurement.date >= start).group_by(measurement.date).all()

    #Close the session
    session.close()

    #Create a dictionary from the provided start date data and append to a list of the start date data
    all_start = []
    
    for min, max, avg in results:
            start_dict = {}
            start_dict["min"] = min
            start_dict["max"] = max
            start_dict["avg"] = round(avg,2)
            all_start.append(start_dict)

    #Return the JSON representation of your dictionary.
    return jsonify(all_start)

@app.route('/api/v1.0/<start>/<end>')
def start_end(start, end):

    # Create our session (link) from Python to the DB
    session = Session(engine)

    #Query for the dates and temperature observations in the given range.
    results = session.query(func.min(measurement.tobs), func.max(measurement.tobs), func.avg(measurement.tobs)).filter(measurement.date >= start,measurement.date <= end).group_by(measurement.date).all()
    
    #Close the session
    session.close()

    #Create a dictionary from the provided range data and append to a list of the range data
    from_start_end = []
    
    for min, max, avg in results:
            start_end_dict = {}
            start_end_dict["min"] = min
            start_end_dict["max"] = max
            start_end_dict["avg"] = round(avg,2)
            from_start_end.append(start_end_dict)
    
    #Return the JSON representation of your dictionary.
    return jsonify(from_start_end)

   

if __name__ == '__main__':
    app.run(debug=True)