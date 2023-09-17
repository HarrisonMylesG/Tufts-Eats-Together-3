from application import app
from application.imports import (login_required, connect_db, request, session, apology, generate_password_hash, check_password_hash, render_template, redirect, os)
from application import app
import sched, time
from datetime import datetime 
import threading

@app.route("/", methods=["GET", "POST"])
@app.route("/home", methods=["GET", "POST"])
@app.route("/index.html", methods=["GET", "POST"])
def home():
    if len(session): #if we are logged in
        db = connect_db()

        def updateList():
            result = db.execute("SELECT name, location, time_start, time_end FROM billboard ORDER BY time_start DESC")
            new=""
            print(len(result))
            for row in result: #format list data into html table to be injected in javascript file
                # new += "<tr class='strikethrough'>" if row["checked"] > 0 else "<tr>"
                # new += "<td class='skinny-brand'><div class='skinny-brand'>" + str(row["brand"]) + "</div></td>"
                new += "<tr>"
                new += "<td>" + str(row["name"]) + "</td>"
                new += "<td class='skinny'>" + str(row["location"]) + "</td>"
                new += "<td class='skinny'>" + str(row["time_start"]) + "</td>"
                new += "<td class='skinny'>" + str(row["time_end"]) + "</td>"
                new += "</tr>"
                # new += "<td class='skinny checkbox'><label class='container'><input type='checkbox' id='checkItem' class='product_id=" + str(row["product_id"]) + "'"
                # new += "checked" if row["checked"] > 0 else ""
                # new += "><span class='checkmark'></span></label></td></tr>"
                # new += "</tr>"

            print("NEW LIST IS READY")
            return new


        if request.method == "POST":

            user = db.execute("SELECT username, first_name, last_name FROM users WHERE id = :myID", myID=session["user_id"])[0]
            username = user["username"]
            full_name = user["first_name"] + " " + user["last_name"]
            print(request.get_json())
            key = next(iter(request.get_json().keys()))
            data = request.get_json()[key]
            if key=="location_selection":
                db.execute("INSERT INTO billboard (username, name, location, time_start, time_end) VALUES (?,?,?,?,?)",
                username, full_name, data["location"], data["time_start"], data["time_end"])
                entry_id = db.execute("SELECT seq FROM sqlite_sequence WHERE name=?", "billboard")[0]["seq"]


                def delay_run():
                    def action():
                        db2 = connect_db()
                        db2.execute("DELETE FROM billboard WHERE id=? AND username=? AND location=? AND time_start=? AND time_end=?", entry_id, username, data["location"], data["time_start"], data["time_end"])
                    # Set up scheduler https://stackoverflow.com/questions/50121539/run-function-at-a-specific-time-in-python
                    s = sched.scheduler(time.time, time.sleep)
                    now = datetime.now()
                    task_time = datetime.strptime(data["time_end"], "%H:%M")
                    # Combine the date from 'now' with the time from 'task_time'
                    scheduled_time = now.replace(hour=task_time.hour, minute=task_time.minute, second=0, microsecond=0)
                    # Calculate the time delay in seconds
                    time_delay = (scheduled_time - now).total_seconds()
                    if time_delay <= 0:
                        # The scheduled time has already passed for today
                        print("Scheduled time has already passed for today.")
                    else:
                        # Schedule the task
                        s.enter(time_delay, 1, action, ())
                        print(f"Task scheduled to run at {data['time_end']} on the current date.")
                        # Run the scheduler
                        s.run()

                # delay_run()
                thread = threading.Thread(target=delay_run)
                thread.start()

                print("Going to update list")
                return updateList()

            result = db.execute("SELECT name, location, time_start, time_end FROM billboard ORDER BY time_start DESC")
            return render_template("index.html", table=result, username=full_name)

        else:
            user = db.execute("SELECT username, first_name, last_name FROM users WHERE id = :myID", myID=session["user_id"])[0]
            username = user["username"]
            full_name = user["first_name"] + " " + user["last_name"]
            result = db.execute("SELECT name, location, time_start, time_end FROM billboard ORDER BY time_start DESC")
            return render_template("index.html", table=result, username=full_name)


    return render_template("index.html")
