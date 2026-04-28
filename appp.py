from flask import Flask, request, render_template_string
import matplotlib
matplotlib.use('Agg')
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LogisticRegression
from sklearn.cluster import KMeans
import os

app = Flask(__name__)

# ---------------- QUESTIONS ----------------

questions = [

# Childhood Trauma
("Did you experience emotional neglect during childhood?", "Childhood Trauma"),
("Did you grow up in a household with frequent conflict?", "Childhood Trauma"),
("Did you feel unsafe or unsupported as a child?", "Childhood Trauma"),
("Did caregivers dismiss your emotions when you were young?", "Childhood Trauma"),
("Do childhood memories still cause emotional pain?", "Childhood Trauma"),

# Relationship Issues
("Do you fear abandonment in relationships?", "Relationship Issues"),
("Do you struggle with trusting partners?", "Relationship Issues"),
("Do arguments trigger intense emotional reactions?", "Relationship Issues"),
("Do you feel insecure in close relationships?", "Relationship Issues"),
("Do you find it difficult to communicate your needs?", "Relationship Issues"),

# Medical Trauma
("Have you experienced a frightening medical emergency?", "Medical Trauma"),
("Do hospital environments trigger anxiety?", "Medical Trauma"),
("Do medical procedures cause extreme fear?", "Medical Trauma"),
("Do you relive past medical experiences negatively?", "Medical Trauma"),
("Do health-related situations make you panic?", "Medical Trauma"),

# Career Anxiety
("Do you constantly worry about job stability?", "Career Anxiety"),
("Do workplace pressures cause sleep disturbance?", "Career Anxiety"),
("Do you fear losing your job or failing professionally?", "Career Anxiety"),
("Do performance reviews cause high anxiety?", "Career Anxiety"),
("Do you compare your career growth negatively with others?", "Career Anxiety"),

# Loss and Grief
("Have you lost someone close and struggle to cope?", "Loss and Grief"),
("Do memories of loss trigger emotional breakdowns?", "Loss and Grief"),
("Do you avoid reminders of someone you lost?", "Loss and Grief"),
("Do you feel persistent sadness due to past loss?", "Loss and Grief"),
("Do you struggle accepting a significant loss?", "Loss and Grief"),

# Low Self-Esteem
("Do you often feel not good enough?", "Low Self-Esteem"),
("Do you doubt your abilities even after success?", "Low Self-Esteem"),
("Do you criticize yourself harshly?", "Low Self-Esteem"),
("Do you feel inferior in social situations?", "Low Self-Esteem"),
("Do you avoid opportunities due to fear of failure?", "Low Self-Esteem"),

]

options = [("Never",0),("Rarely",1),("Sometimes",2),("Often",3)]

# ---------------- ML MODEL ----------------

X_train = np.random.randint(0,4,(500,30))
y_train = np.sum(X_train,axis=1)
y_train = np.where(y_train<35,0,np.where(y_train<70,1,2))

model = LogisticRegression(max_iter=1000)
model.fit(X_train,y_train)

# ---------------- HOME PAGE ----------------

home_html = """
<!DOCTYPE html>
<html>
<head>
<title>Psychological Trauma Assessment</title>
<style>
body{
margin:0;
font-family:'Segoe UI';
background:linear-gradient(135deg,#0f2027,#203a43,#2c5364);
color:white;
}
.container{
width:80%;
margin:auto;
padding:40px;
}
h1{text-align:center;margin-bottom:30px;}
.card{
background:rgba(255,255,255,0.08);
backdrop-filter: blur(10px);
padding:20px;
margin-bottom:15px;
border-radius:15px;
transition:0.3s;
}
.card:hover{
transform:scale(1.02);
}
button{
background:linear-gradient(to right,#0072ff,#00c6ff);
border:none;
padding:15px 35px;
font-size:18px;
border-radius:30px;
color:white;
cursor:pointer;
transition:0.3s;
}
button:hover{
transform:scale(1.1);
}
.progress{
width:100%;
background:#333;
height:10px;
border-radius:5px;
margin-bottom:30px;
}
.progress-bar{
height:10px;
width:100%;
background:linear-gradient(to right,#00c6ff,#0072ff);
border-radius:5px;
}
</style>
</head>
<body>

<div class="container">
<h1>Psychological Trauma Self-Assessment</h1>

<div class="progress">
<div class="progress-bar"></div>
</div>

<form method="POST">

{% for i in range(questions|length) %}
<div class="card">
<b>{{i+1}}. {{questions[i][0]}}</b><br><br>
{% for opt,val in options %}
<input type="radio" name="q{{i}}" value="{{val}}" required> {{opt}}<br>
{% endfor %}
</div>
{% endfor %}

<center><button type="submit">Analyze My Mental State</button></center>
</form>

</div>
</body>
</html>
"""

# ---------------- RESULT PAGE ----------------

result_html = """
<!DOCTYPE html>
<html>
<head>
<title>Result</title>
<style>
body{
margin:0;
font-family:'Segoe UI';
background:linear-gradient(135deg,#141e30,#243b55);
color:white;
text-align:center;
}
.container{
padding:40px;
}
.result-box{
background:rgba(255,255,255,0.1);
padding:30px;
border-radius:20px;
display:inline-block;
}
.highlight{
color:#00ffcc;
font-size:22px;
font-weight:bold;
}
img{
margin-top:20px;
border-radius:15px;
}
a{
color:#00ffcc;
font-size:18px;
}
</style>
</head>
<body>

<div class="container">

<h1>Your Psychological Analysis</h1>

<div class="result-box">
<h2>Overall Trauma Level: <span class="highlight">{{level}}</span></h2>
<p><b>Dominant Area:</b> <span class="highlight">{{dominant}}</span></p>
<p>{{explanation}}</p>

<img src="/static/result.png" width="500">
</div>

<br><br>
<a href="/">Take Test Again</a>

</div>
</body>
</html>
"""

# ---------------- ROUTE ----------------

@app.route("/",methods=["GET","POST"])
def index():

    if request.method=="POST":

        responses=[]
        trauma_map={
            "Childhood Trauma":0,
            "Relationship Issues":0,
            "Medical Trauma":0,
            "Career Anxiety":0,
            "Loss and Grief":0,
            "Low Self-Esteem":0
        }

        for i in range(30):
            val=int(request.form.get(f"q{i}",0))
            responses.append(val)
            trauma_map[questions[i][1]]+=val

        X_user=np.array(responses).reshape(1,-1)
        prediction=model.predict(X_user)[0]
        level=["LOW","MODERATE","HIGH"][prediction]

        dominant=max(trauma_map,key=trauma_map.get)

        explanations={
            "LOW":"Your responses indicate relatively stable emotional well-being.",
            "MODERATE":"You show moderate stress indicators. Emotional awareness and support may help.",
            "HIGH":"High psychological distress detected. Consider speaking with a mental health professional."
        }

        kmeans=KMeans(n_clusters=6,n_init=10)
        kmeans.fit(X_train)
        kmeans.predict(X_user)

        if not os.path.exists("static"):
            os.mkdir("static")

        plt.figure(figsize=(6,6))
        plt.pie(trauma_map.values(),labels=trauma_map.keys(),autopct='%1.1f%%')
        plt.title("Trauma Distribution")
        plt.tight_layout()
        plt.savefig("static/result.png")
        plt.close()

        return render_template_string(result_html,
                                      level=level,
                                      dominant=dominant,
                                      explanation=explanations[level])

    return render_template_string(home_html,
                                  questions=questions,
                                  options=options)

if __name__=="__main__":
    app.run(debug=True)