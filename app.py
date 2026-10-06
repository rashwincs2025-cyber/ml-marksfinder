import numpy as np
from flask import Flask, request, render_template
import pickle

app = Flask(__name__, template_folder="templates")

# CORRECT WAY to load the models (Removed the 'import model' lines)
with open('model.pkl', 'rb') as file:
    model = pickle.load(file)

with open('model1.pkl', 'rb') as file:
    model1 = pickle.load(file)

@app.route('/')
def h():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/index')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['GET'])
def predict():
    # Retrieve data from URL parameters
    cgpa = request.args.get('cgpa')
    projects = request.args.get('projects')
    workshops = request.args.get('workshops')
    mini_projects = request.args.get('mini_projects')
    skills = request.args.get('skills')
    communication_skills = request.args.get('communication_skills')
    internship = request.args.get('internship')
    hackathon = request.args.get('hackathon')
    tw_percentage = request.args.get('tw_percentage')
    te_percentage = request.args.get('te_percentage')
    backlogs = request.args.get('backlogs')
    name = request.args.get('name')

    # Fix: Make sure none of the values are None type before checking for empty strings
    if not skills: skills = ""
    if not name: name = "Student"
    
    # Handle empty string submissions
    if cgpa == '' or cgpa is None: cgpa = '0'
    if projects == '' or projects is None: projects = '0'
    if workshops == '' or workshops is None: workshops = '0'
    if mini_projects == '' or mini_projects is None: mini_projects = '0'
    if communication_skills == '' or communication_skills is None: communication_skills = '0'
    if internship == '' or internship is None: internship = '0'
    if hackathon == '' or hackathon is None: hackathon = '0'
    if tw_percentage == '' or tw_percentage is None: tw_percentage = '0'
    if te_percentage == '' or te_percentage is None: te_percentage = '0'
    if backlogs == '' or backlogs is None: backlogs = '0'

    # Count skills based on commas
    s = 1 if skills != "" else 0
    for i in skills:
        if i == ',':
            s = s + 1
    
    # First model prediction (Placement Status)
    arr = np.array([cgpa, projects, workshops, mini_projects, s, communication_skills, internship, hackathon, tw_percentage, te_percentage, backlogs])
    brr = np.asarray(arr, dtype=float)
    output = model.predict([brr])
    
    # Check if the output is 'Placed' or placed inside a list like ['Placed']
    is_placed = output == 'Placed' or (len(output) > 0 and output[0] == 'Placed')
    
    if is_placed:
        p = '1'
    else:
        p = '0'
        
    # Second model prediction (Expected Salary)
    arr1 = np.array([cgpa, projects, workshops, mini_projects, s, communication_skills, internship, hackathon, tw_percentage, te_percentage, backlogs, p])
    brr1 = np.asarray(arr1, dtype=float)
    salary = model1.predict([brr1])
    
    # Fix: Convert salary to integer first to drop decimals, then to string for formatting
    k = str(int(salary[0])) 
    l = len(k)
    
    # Salary comma formatting logic
    if l == 6:
        k = k[0] + ',' + k[1] + k[2] + ',' + k[3] + k[4] + k[5]
    elif l == 7:
        k = k[0] + k[1] + ',' + k[2] + k[3] + ',' + k[4] + k[5] + k[6]
        
    # Result generation (Fixed Spelling Errors here)
    if is_placed:
        out = f'Congratulations {name} !! You have high chances of getting placed!!!'
        out2 = f'Your Expected Salary will be INR {k} per annum'
        return render_template('output.html', output=out, output2=out2)
    else:
        out = f'Sorry {name} !! You have low chances of getting placed. All the best!!!!'
        out2 = 'Improve your skills...'
        return render_template('output.html', output=out, output2=out2)

if __name__ == "__main__":
    app.run(debug=True)