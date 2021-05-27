import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine,func

from flask import Flask, jsonify

#create engine
engine=create_engine("sqlite:///Resources/hawaii.sqlite")

#map engine
Base=automap_base()
Base.prepare(engine,reflect=True)

#table reference
Station=Base.classes.station
Measurement=Base.classes.measurement

#create app
app=Flask(__name__)

#Use Flask to define my routes
@app.route("/")
def home():
    return "/api/v1.0/precipitation"

@app.route("/api/v1.0/precipitation")
def prec():
    #create engine and query
    session=Session(engine)
    prec_query=session.query(Measurement.date,Measurement.prcp).all()    
    session.close()
    
    #generate dictionary
    prec_dict={}
    for date,prcp in prec_query:
        prec_dict[date]=prcp
    
    return jsonify(prec_dict)
    
#@app.route("/api/v1.0/stations")
#def home():
 #   print("api instructions")
    
    
#@app.route("/api/v1.0/tobs")
#def home():
 #   print("api instructions")
    
    
#@app.route("/api/v1.0/<start> and /api/v1.0/<start>/<end>")
#def home():
    #print("api instructions")
    
if __name__=="__main__":
    app.run(debug=True)