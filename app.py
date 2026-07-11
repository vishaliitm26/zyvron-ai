from reportlab.lib.utils import ImageReader
from flask import send_file
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io
from datetime import datetime

from flask import Flask, render_template, request
import sqlite3
import joblib

app = Flask(__name__)

# Load trained model
model = joblib.load("models/diabetes_model.pkl")


@app.route("/")
def home():
    return render_template(
        "index.html",
        prediction=None,
        risk=None,
        risk_color=None
    )


@app.route("/predict", methods=["POST"])
def predict():

    pregnancies = float(request.form["Pregnancies"])
    glucose = float(request.form["Glucose"])
    blood_pressure = float(request.form["BloodPressure"])
    skin_thickness = float(request.form["SkinThickness"])
    insulin = float(request.form["Insulin"])
    bmi = float(request.form["BMI"])
    dpf = float(request.form["DiabetesPedigreeFunction"])
    age = float(request.form["Age"])

    patient = [[
        pregnancies,
        glucose,
        blood_pressure,
        skin_thickness,
        insulin,
        bmi,
        dpf,
        age
    ]]

    prediction = model.predict(patient)
    probability = model.predict_proba(patient)

    risk = round(probability[0][1] * 100, 2)

    if prediction[0] == 1:
        result = "🔴 High Risk of Diabetes"
        risk_color = "#e53935"
    else:
        result = "🟢 Low Risk of Diabetes"
        risk_color = "#43a047"

    global latest_report

    latest_report = {
        "Pregnancies": pregnancies,
        "Glucose": glucose,
        "BloodPressure": blood_pressure,
        "SkinThickness": skin_thickness,
        "Insulin": insulin,
        "BMI": bmi,
        "DPF": dpf,
        "Age": age,
        "Prediction": result,
        "Risk": risk
    }
    conn = sqlite3.connect("zyvron.db")
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO predictions (
        date,
        time,
        pregnancies,
        glucose,
        blood_pressure,
        skin_thickness,
        insulin,
        bmi,
        dpf,
        age,
        prediction,
        risk
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        datetime.now().strftime("%d-%m-%Y"),
        datetime.now().strftime("%H:%M:%S"),
        pregnancies,
        glucose,
        blood_pressure,
        skin_thickness,
        insulin,
        bmi,
        dpf,
        age,
        result,
        risk
    ))

    conn.commit()
    conn.close()

    return render_template(
        "index.html",
        prediction=result,
        risk=risk,
        risk_color=risk_color
    )

@app.route("/download")
def download_report():

    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    logo = ImageReader("static/images/zyvron_logo.png")
    pdf.drawImage(
        logo,
        250,
        710,
        width=70,
        height=70,
        preserveAspectRatio=True,
        mask='auto'
    )

    width, height = letter

    pdf.setFont("Helvetica-Bold",22)
    pdf.drawCentredString(width/2,690,"ZYVRON AI")

    pdf.setFont("Helvetica",15)
    pdf.drawCentredString(width/2,668,"Diabetes Risk Report")

    pdf.line(50,650,550,650)

    y = 620

    pdf.setFont("Helvetica", 12)

    pdf.drawString(60, y, f"Pregnancies: {latest_report['Pregnancies']}")
    y -= 20

    pdf.drawString(60, y, f"Glucose: {latest_report['Glucose']}")
    y -= 20

    pdf.drawString(60, y, f"Blood Pressure: {latest_report['BloodPressure']}")
    y -= 20

    pdf.drawString(60, y, f"Skin Thickness: {latest_report['SkinThickness']}")
    y -= 20

    pdf.drawString(60, y, f"Insulin: {latest_report['Insulin']}")
    y -= 20

    pdf.drawString(60, y, f"BMI: {latest_report['BMI']}")
    y -= 20

    pdf.drawString(60, y, f"Diabetes Pedigree Function: {latest_report['DPF']}")
    y -= 20

    pdf.drawString(60, y, f"Age: {latest_report['Age']}")
    y -= 40

    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(60, y, f"Prediction: {latest_report['Prediction']}")
    y -= 25

    pdf.drawString(60, y, f"Risk Score: {latest_report['Risk']}%")
    y -= 40

    pdf.setFont("Helvetica", 10)
    pdf.drawString(
        60,
        y,
        "Generated on: " + datetime.now().strftime("%d %B %Y %I:%M %p")
    )
    y -= 30

    pdf.drawString(
        60,
        y,
        "Developed by Vishal S | IIT Madras"
    )
    y -= 20

    pdf.drawString(
        60,
        y,
        "For educational purposes only. Not a medical diagnosis."
    )

    pdf.save()
    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name="Zyvron_AI_Report.pdf",
        mimetype="application/pdf"
    )

@app.route("/history")
def history():

    conn = sqlite3.connect("zyvron.db")

    cursor = conn.cursor()

    cursor.execute("""
    SELECT * FROM predictions
    ORDER BY id DESC
    """)

    records = cursor.fetchall()

    conn.close()

    return render_template(
        "history.html",
        records=records
    )

if __name__ == "__main__":
    app.run(debug=True)