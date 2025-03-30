import pandas as pd
import numpy as np
import json
import re
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
from openai import OpenAI  # Assumes you have an OpenAI client library installed

import mysql.connector

# Connect to MySQL
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="samarth@2006",
    database="users"
)
cursor = conn.cursor()
cursor.execute("SELECT weight, height FROM users")
rows = cursor.fetchall()
users_list = [{"weight": row[0], "height": row[1]} for row in rows]

# ---------------------------
# Data Loading and Preprocessing
# ---------------------------
df = pd.read_csv('nutrient.csv')

# Specify the nutritional columns to use
nutrition_cols = [
    'Data.Carbohydrate', 'Data.Protein', 'Data.Fat.Total Lipid',
    'Data.Fiber', 'Data.Major Minerals.Calcium', 'Data.Major Minerals.Iron',
    'Data.Vitamins.Vitamin A - RAE', 'Data.Vitamins.Vitamin C'
]

# Clean and prepare the nutritional data
df_nutrition = df[nutrition_cols].fillna(0)
df_nutrition = df_nutrition.apply(pd.to_numeric, errors='coerce').fillna(0)

# Standardize the data
scaler = StandardScaler()
scaled_data = scaler.fit_transform(df_nutrition)

# Cluster foods using K-means (assuming optimal_clusters is 5 based on elbow method)
optimal_clusters = 5  
kmeans = KMeans(n_clusters=optimal_clusters, random_state=42)
df['Food_Cluster'] = kmeans.fit_predict(scaled_data)

# ---------------------------
# Nutritional Plan Generator Class
# ---------------------------
class NutritionalPlanGenerator:
    def __init__(self, df):
        self.df = df
        self.cluster_centers = kmeans.cluster_centers_
        
    def generate_plan(self, daily_calories=2000, meals_per_day=3, diet_type='Vegetarian'):
        # Filter the DataFrame based on dietary preference
        filtered_df = self.df[self.df['Dietary category'].str.lower() == diet_type.lower()]
        
        # Macronutrient distribution (calculated here for possible use)
        carb_percent = 0.3
        protein_percent = 0.5
        fat_percent = 0.2
        
        # daily_carbs = (daily_calories * carb_percent) / 4  # 4 calories per gram
        # daily_protein = (daily_calories * protein_percent) / 4
        # daily_fat = (daily_calories * fat_percent) / 9     # 9 calories per gram
        
        meal_plan = []
        
        # For each meal, randomly select foods from different clusters
        for meal in range(meals_per_day):
            cluster_selection = np.random.choice(range(optimal_clusters), size=2, replace=False)
            meal_items = []
            for cluster in cluster_selection:
                cluster_foods = filtered_df[filtered_df['Food_Cluster'] == cluster]
                if not cluster_foods.empty:
                    selected_food = cluster_foods.sample(1)
                    meal_items.append(selected_food)
            if meal_items:
                meal_plan.append(pd.concat(meal_items))
        
        return pd.concat(meal_plan) if meal_plan else None

    def analyze_nutrition(self, plan):
        if plan is None:
            return None
        nutrition_summary = plan[nutrition_cols].sum()
        return nutrition_summary

# Initialize the nutritional plan generator with the data
nutrition_planner = NutritionalPlanGenerator(df)

# ---------------------------
# OpenAI Client and NLP Helper
# ---------------------------
client = OpenAI(
    api_key="IITM-hackday",
    base_url="https://llm-gateway.heurist.xyz"
)

def generateResp(text, system_prompt):
    """
    Send a text prompt to the NLP service with the given system instruction.
    """
    response = client.chat.completions.create(
        model="mistralai/mistral-small-24b-instruct",
        messages=[
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': text}
        ],
        temperature=0.01
    )
    return response

def extract_json(text):
    match = re.search(r"\{.*\}", text, re.DOTALL)  # Find JSON-like structure
    if match:
        json_str = match.group(0)  # Extract matched JSON portion
        return json_str


# ---------------------------
# Main Integrated Pipeline
# ---------------------------
def nutriBot(user_input):
    # Step 1: User inputs their dietary requirements in natural language.    
    # Step 2: Use NLP to extract structured parameters from the user input.
    extraction_prompt = (
        "Extract dietary details from user input and return a valid JSON object ONLY. "
        "Ensure the JSON has the following keys: daily_calories (int), meals_per_day (int), "
        "diet_type (string). If a value is missing, default to {'daily_calories': 2000, "
        "'meals_per_day': 3, 'diet_type': 'Vegetarian'}. STRICTLY return JSON, no extra text."
    )    
    extraction_response = generateResp(user_input, extraction_prompt)
    print(extraction_response)
    try:
        # Parse the response (assumed to be a JSON formatted dictionary)
        params = extraction_response.choices[0].message.content
    except Exception as e:
        print("Error parsing NLP extraction output:", e)
        return
    print("---------")
    print(params,type(params))
    # x = params.find("'''json")
    # params = params[x+8:]
    # y = params.rfind("'''")
    # params = params[:y-2]
    print("--------")
    params = extract_json(params)
    print(params,type(params))
    params = json.loads(params)
    
    daily_calories = params.get("daily_calories", 2000)
    meals_per_day = params.get("meals_per_day", 3)
    diet_type = params.get("diet_type", "Vegetarian")
    
    print(f"\nExtracted Parameters:\n Daily Calories: {daily_calories}, Meals per Day: {meals_per_day}, Diet Type: {diet_type}")
    
    # Step 3: Generate the meal plan using the extracted parameters.
    plan = nutrition_planner.generate_plan(daily_calories, meals_per_day, diet_type)
    
    if plan is None:
        print("No suitable foods found for the specified dietary requirements.")
        return
    
    # Analyze the nutritional content of the generated plan.
    nutrition_summary = nutrition_planner.analyze_nutrition(plan)
    
    # Prepare a string representation of the plan and its nutritional summary.
    # (Assumes the dataset contains columns 'Description' and 'Category' for each food item.)
    plan_str = plan[['Description', 'Category'] + nutrition_cols].to_string(index=False)
    summary_str = nutrition_summary.to_string()
    
    combined_output = f"Meal Plan:\n{plan_str}\n\nNutritional Summary:\n{summary_str}"
    
    # Step 4: Convert the combined food data and summary into natural language.
    conversion_prompt = ("Convert the following food data and nutritional summary into a natural language description:")
    final_response = generateResp(combined_output, conversion_prompt)
    
    # Output the final natural language description.
    print("\nGenerated Diet Description:")
    result = final_response.choices[0].message.content
    return result
# nutriBot('Generate a Vegetarian Diet of 2100 calories')