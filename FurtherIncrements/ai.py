import tensorflow as tf 
from tensorflow.keras import layers, models
import pandas as pd 
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import numpy as np
def exercise():
    df = pd.read_excel("gym.xlsx")
    df["BMI"] = df["BMI"].astype(float)
    classes = df["Exercises"].unique()

    dummies = pd.get_dummies(df, columns=["Diabetes", "Level", "Fitness Goal", 
                                        "Fitness Type", "Hypertension", "Sex"],
                            drop_first=True)


    for col in dummies.columns:
        if dummies[col].dtype == 'object':
            dummies[col] = pd.factorize(dummies[col])[0] 
        elif dummies[col].dtype == 'bool':
            dummies[col] = dummies[col].astype(int)  
    

    features = ["Age", "Height", "Weight", "BMI" , "Level_Obuse" , "Level_Overweight" , "Level_Underweight", "Fitness Goal_Weight Loss", "Fitness Type_Muscular Fitness"] 
    target = "Exercises"
    X_train, y_train = dummies[features] , dummies[target]
    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)

    
    age= 19 
    height = 1.72 
    weight = 75
    bmi  = (weight/(height**2))
    if bmi <= 18.5:
        levelunder = 1
        levelover = 0
        levelobuse = 0 
    elif bmi > 30:
        levelunder = 0
        levelover = 0
        levelobuse = 1 
    elif bmi >25 :
        levelobuse = 0 
        levelunder = 0
        levelover = 1
    else:
        levelobuse = 0 
        levelunder = 0
        levelover = 0
    fitnessgoalloss = 1
    fitnessmuscular = 1
    values = [age , height , weight , bmi ,levelobuse , levelover , levelunder,fitnessgoalloss, fitnessmuscular]
    # Correct way to create a single-row DataFrame
    model = models.load_model("final.keras")
    x = pd.DataFrame([values], columns=features)  # Shape: (1, n_features)
    x_scaled = scaler.transform(x[features])  # Use the same scaler as training
    x_scaled = x_scaled.astype(np.float32)
    print(df["Exercises"].unique()[np.argmax(model.predict(x_scaled)[0])])

exercise()