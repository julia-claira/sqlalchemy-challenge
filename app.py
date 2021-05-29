import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine,func
import datetime as dt

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
    return (
        f"Welcome To Julia's SQLAlchemy Weather API<br>"
        f"<br>"
        f"Available Routes:<br>"
        f"----------------<br>"
        f"/api/v1.0/precipitation<br>"
        f"/api/v1.0/stations<br>"
        f"/api/v1.0/tobs<br>"
        f"/api/v1.0/start_date"
        f"/api/v1.0/start_date/end_date<br>"
        f"<br>"
        f"example date search: /api/v1.0/2014-01-30/2016-12-01")

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
    
@app.route("/api/v1.0/stations")
def stations():
    session=Session(engine)
    station_query=session.query(Station.station).distinct().all()
    session.close()
 
    # return list
    station_list=[]
    
    for station in station_query:
        station_list.append(station[0])
        
    return jsonify(station_list)

       
@app.route("/api/v1.0/tobs")
def Tobs():
    
    #sets up the year range that was found in my jupyter notebook query
    oneYearAgoDate=dt.date(2017,8,23)-dt.timedelta(days=365)
    mostRecentDate=dt.date(2017,8,23)
    
    #finds most active station
    session=Session(engine)
    mostactive=session.query(Measurement.station)\
    .group_by('station').order_by(func.count(Measurement.id).desc()).all()[0][0]                            
    #filters for most active between the year set
    mostactiveYearlyTemp=session.query(Measurement.date,Measurement.tobs)\
    .filter(Measurement.station==mostactive)\
    .filter(Measurement.date>=oneYearAgoDate)\
    .filter(Measurement.date<=mostRecentDate).all()

    session.close()
    

    return jsonify(mostactiveYearlyTemp)
    
@app.route("/api/v1.0/<start>")
def startdate(start):
    

    #start session and query from start date
    session=Session(engine)   
    
    #checks for the latest date to make sure query is within bounds
    highest_date=session.query(func.max(Measurement.date)).all()[0][0]
    
    if (start<=highest_date):
    
        summary_by_start=session.query(func.min(Measurement.tobs),\
        func.max(Measurement.tobs),func.avg(Measurement.tobs))\
        .filter(Measurement.date>=start).all()
    
        session.close()
    
        #create dictionary for output
        summary={
            "_Start Date":start,
            "Min Temp":summary_by_start[0][0],
            "Max Temp":summary_by_start[0][1],
            "Avg Temp":round(summary_by_start[0][2],2)}
   
    else:
        #if query is out of bounds return this warning
        summary=[f"You're query is out of bounds. This API only goes to {highest_date}."]
        
    return jsonify(summary)
           
@app.route("/api/v1.0/<start>/<end>")
def startenddate(start,end):
    

    #start session and query from start date and end date
    session=Session(engine)   

    #checks for the latest date to make sure query is within bounds
    highest_date=session.query(func.max(Measurement.date)).all()[0][0]
    
    #if the end query is higher the latest date, reset to latest date
    if end>=highest_date:
        end=highest_date
    
    if (start<=highest_date) and start<end:
    
        summary_by_start=session.query(func.min(Measurement.tobs),\
        func.max(Measurement.tobs),func.avg(Measurement.tobs))\
        .filter(Measurement.date>=start).filter(Measurement.date<=end).all()
    
        session.close()
   
        #create dictionary for output
        summary={
        "_Start Date":start,
        "_End Date":end,
        "Min Temp":summary_by_start[0][0],
        "Max Temp":summary_by_start[0][1],
        "Avg Temp":round(summary_by_start[0][2],2)}
   

    else:
        if start>highest_date:
            #if start query is out of bounds return this warning
            summary=[f"Warning: your start query is out of bounds. This API only goes to {highest_date}."]
        else:
            #warns that the start date is higher than end date
            summary=[f"Warning: your start date {start} is greater than your end date {end}"]
        
    return jsonify(summary)
    
                
if __name__=="__main__":
    app.run(debug=True)