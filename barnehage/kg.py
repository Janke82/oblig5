from flask import Flask
from flask import url_for
from flask import render_template
from flask import request
from flask import redirect
from flask import session
from kgmodel import (Foresatt, Barn, Soknad, Barnehage)
from kgcontroller import (form_to_object_soknad, insert_soknad, commit_all, select_alle_barnehager, check_availability, select_alle_soknader, select_alle_foresatte, select_alle_barn, update_soknad)

app = Flask(__name__)
app.secret_key = 'BAD_SECRET_KEY' # nødvendig for session

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/barnehager')
def barnehager():
    information = select_alle_barnehager()
    return render_template('barnehager.html', data=information)

@app.route('/behandle', methods=['GET', 'POST'])
def behandle():
    if request.method == 'POST':
        sd = request.form
        print(sd)
        log = insert_soknad(form_to_object_soknad(sd))
        print(log)
        session['information'] = sd
        return redirect(url_for('svar')) #[1]
    else:
        return render_template('soknad.html')

@app.route('/svar')
def svar():
    update_soknad()
    request_answer = check_availability()
    information = session['information']
    return render_template('svar.html', data=information, answer=request_answer) 

@app.route('/commit')
def commit():
    barnehager = select_alle_barnehager()
    soknader = select_alle_soknader()
    barn = select_alle_barn()
    foresatte = select_alle_foresatte()
    commit_all()
    return render_template('commit.html', kg=barnehager, applicants=soknader, foresatte=foresatte, barn=barn)

@app.route('/soknader')
def soknader():
    information = select_alle_soknader()
    return render_template('soknader.html', data=information)

@app.route('/statestikk')
def statestikk():
    import pandas as pd
    kgdata = pd.read_excel("C:/Users/user/Downloads/IS114/ssb-barnehager-2015-2023-alder-1-2-aar.xlsm", sheet_name="KOSandel120000",
                       header=3,
                       names=["kom","y15","y16","y17","y18","y19","y20","y21","y22","y23"],
                       na_values=[".", ".."])

    import matplotlib.pyplot as plt


#hvilken kommune
    valgt_kommune = "4203 Arendal" 
    data_for_kommune = kgdata[kgdata["kom"] == valgt_kommune]

# Beregn prosentandel av barn 1 -2 år
    prosent_barn = data_for_kommune[["y15", "y16", "y17", "y18", "y19", "y20", "y21", "y22", "y23"]].values.flatten()

# År
    år = ["2015", "2016", "2017", "2018", "2019", "2020", "2021", "2022", "2023"]

# Lag søylediagram
    plt.figure(figsize=(10, 5))
    plt.bar(år, prosent_barn, color="pink")
    plt.title("Prosent av barn i ett- og to-årsalderen i barnehagen for Arendal (2020-2023)")
    plt.xlabel("År")
    plt.ylabel("Prosent")
    plt.xticks(rotation=45)
    plt.grid(axis="y")
    plt.tight_layout()
    plt.show()
    return render_template('statestikk.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)  


"""
Referanser
[1] https://stackoverflow.com/questions/21668481/difference-between-render-template-and-redirect
"""

"""
Søkeuttrykk

"""