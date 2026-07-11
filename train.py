import pandas as pd
import matplotlib.pyplot as plt
import joblib
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score

# Load the dataset
df = pd.read_csv("data/diabetes.csv")

print("=" * 50)
print("DATA CLEANING")
print("=" * 50)

# Columns where 0 is invalid
columns = [
    "Glucose",
    "BloodPressure",
    "SkinThickness",
    "Insulin",
    "BMI"
]

print("\nNumber of zero values before cleaning:\n")

for column in columns:
    zeros = (df[column] == 0).sum()
    print(f"{column}: {zeros}")

print("\nReplacing zeros with median values...\n")

for column in columns:
    median = df[df[column] != 0][column].median()
    df[column] = df[column].replace(0, median)

print("\nNumber of zero values after cleaning:\n")

for column in columns:
    zeros = (df[column] == 0).sum()
    print(f"{column}: {zeros}")

print("\nFirst 10 rows after cleaning:")
print(df.head(10))

# -----------------------------
# Separate Features and Label
# -----------------------------

X = df.drop("Outcome", axis=1)
y = df["Outcome"]

print("\nFirst 5 Feature Rows:")
print(X.head())

print("\nFirst 5 Labels:")
print(y.head())

# Split the dataset

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)

print("\nTraining Data Shape:")
print(X_train.shape)

print("\nTesting Data Shape:")
print(X_test.shape)

# Create the Machine Learning Model

model = LogisticRegression(max_iter=1000)

# Train the model

model.fit(X_train, y_train)

print("\nModel trained successfully!")

# Make predictions on the test data
y_pred = model.predict(X_test)

# Calculate accuracy
accuracy = accuracy_score(y_test, y_pred)

print(f"\nModel Accuracy: {accuracy * 100:.2f}%")

# -----------------------------
# Predict a New Patient
# -----------------------------

new_patient = [[
    2,      # Pregnancies
    150,    # Glucose
    80,     # BloodPressure
    30,     # SkinThickness
    120,    # Insulin
    32.0,   # BMI
    0.50,   # DiabetesPedigreeFunction
    45      # Age
]]

prediction = model.predict(new_patient)

if prediction[0] == 1:
    print("\nPrediction: Diabetic")
else:
    print("\nPrediction: Not Diabetic")

# -----------------------------
# Save the trained model
# -----------------------------
joblib.dump(model, "models/diabetes_model.pkl")

print("\nModel saved successfully!")