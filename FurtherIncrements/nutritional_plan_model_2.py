import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt

# Load the CSV file
df = pd.read_csv('nutrient_food_with_dietary_category.csv')

# Select relevant nutritional columns
nutrition_cols = [
    'Data.Carbohydrate', 'Data.Protein', 'Data.Fat.Total Lipid',
    'Data.Fiber', 'Data.Major Minerals.Calcium', 'Data.Major Minerals.Iron',
    'Data.Vitamins.Vitamin A - RAE', 'Data.Vitamins.Vitamin C'
]

# Clean and prepare the data
df_nutrition = df[nutrition_cols].fillna(0)
df_nutrition = df_nutrition.apply(pd.to_numeric, errors='coerce').fillna(0)

# Standardize the nutritional values
scaler = StandardScaler()
scaled_data = scaler.fit_transform(df_nutrition)

# Determine optimal number of clusters
inertia = []
for k in range(1, 10):
    kmeans = KMeans(n_clusters=k, random_state=42)
    kmeans.fit(scaled_data)
    inertia.append(kmeans.inertia_)

# Apply K-means clustering
optimal_clusters = 5  # Based on elbow method
kmeans = KMeans(n_clusters=optimal_clusters, random_state=42)
df['Food_Cluster'] = kmeans.fit_predict(scaled_data)

class NutritionalPlanGenerator:
    def __init__(self, df):
        self.df = df
        self.cluster_centers = kmeans.cluster_centers_
        
    def calculate_bmi_category(self, height, weight):
        """Calculate BMI and return category"""
        bmi = weight / ((height / 100) ** 2)
        if bmi < 18.5:
            return 'Underweight', bmi
        elif 18.5 <= bmi < 25:
            return 'Normal', bmi
        elif 25 <= bmi < 30:
            return 'Overweight', bmi
        else:
            return 'Obese', bmi
    
    def calculate_daily_calories(self, bmi_category, weight, activity_level='moderate'):
        """Calculate daily calorie needs based on BMI category and activity level"""
        # Base calorie multipliers
        activity_multipliers = {
            'sedentary': 1.2,
            'light': 1.375,
            'moderate': 1.55,
            'active': 1.725,
            'very_active': 1.9
        }
        
        # Adjust calorie targets based on BMI category
        if bmi_category == 'Underweight':
            # Aim for weight gain: calories above maintenance
            base_calories = weight * 35
        elif bmi_category == 'Normal':
            # Aim for weight maintenance
            base_calories = weight * 30
        elif bmi_category == 'Overweight':
            # Aim for mild weight loss
            base_calories = weight * 25
        else:  # Obese
            # Aim for weight loss
            base_calories = weight * 20
            
        return base_calories * activity_multipliers.get(activity_level.lower(), 1.55)
    
    def get_macronutrient_distribution(self, bmi_category, nutrition_model=None):
        """Get macronutrient distribution based on BMI category and optional nutrition model"""
        # Default distributions based on BMI category
        if bmi_category == 'Underweight':
            base_dist = {'carb': 0.4, 'protein': 0.3, 'fat': 0.3}
        elif bmi_category == 'Normal':
            base_dist = {'carb': 0.4, 'protein': 0.3, 'fat': 0.3}
        elif bmi_category == 'Overweight':
            base_dist = {'carb': 0.3, 'protein': 0.4, 'fat': 0.3}
        else:  # Obese
            base_dist = {'carb': 0.25, 'protein': 0.45, 'fat': 0.3}
        
        # Adjust based on nutrition model keywords if provided
        if nutrition_model:
            model = nutrition_model.lower()
            
            # Carb adjustments
            if 'low carb' in model:
                base_dist['carb'] = max(0.1, base_dist['carb'] - 0.15)
                base_dist['protein'] += 0.075
                base_dist['fat'] += 0.075
            elif 'mid carb' in model:
                base_dist['carb'] = 0.35  # Set to moderate level
            elif 'high carb' in model:
                base_dist['carb'] = min(0.6, base_dist['carb'] + 0.15)
                base_dist['protein'] = max(0.15, base_dist['protein'] - 0.075)
                base_dist['fat'] = max(0.15, base_dist['fat'] - 0.075)
            
            # Protein adjustments
            if 'low protein' in model:
                base_dist['protein'] = max(0.15, base_dist['protein'] - 0.15)
                base_dist['carb'] += 0.075
                base_dist['fat'] += 0.075
            elif 'mid protein' in model:
                base_dist['protein'] = 0.3  # Set to moderate level
            elif 'high protein' in model:
                base_dist['protein'] = min(0.6, base_dist['protein'] + 0.15)
                base_dist['carb'] = max(0.15, base_dist['carb'] - 0.075)
                base_dist['fat'] = max(0.15, base_dist['fat'] - 0.075)
            
            # Fat adjustments
            if 'low fat' in model:
                base_dist['fat'] = max(0.1, base_dist['fat'] - 0.15)
                base_dist['carb'] += 0.075
                base_dist['protein'] += 0.075
            elif 'mid fat' in model:
                base_dist['fat'] = 0.3  # Set to moderate level
            elif 'high fat' in model:
                base_dist['fat'] = min(0.6, base_dist['fat'] + 0.15)
                base_dist['carb'] = max(0.15, base_dist['carb'] - 0.075)
                base_dist['protein'] = max(0.15, base_dist['protein'] - 0.075)
        
        # Normalize to ensure the sum is 1
        total = sum(base_dist.values())
        return {k: v/total for k, v in base_dist.items()}
        
    def generate_plan(self, height, weight, meals_per_day=3, diet_type='Vegetarian', 
                     activity_level='moderate', nutrition_model=None):
        """Generate a meal plan with optional nutrition model keywords"""
        # Calculate BMI and category
        bmi_category, bmi_value = self.calculate_bmi_category(height, weight)
        print(f"BMI: {bmi_value:.1f} - Category: {bmi_category}")
        
        # Calculate daily calories
        daily_calories = self.calculate_daily_calories(bmi_category, weight, activity_level)
        print(f"Recommended daily calories: {daily_calories:.0f}")
        
        # Get macronutrient distribution
        macros = self.get_macronutrient_distribution(bmi_category, nutrition_model)
        print(f"Macronutrient distribution: Carbs {macros['carb']*100:.1f}%, "
              f"Protein {macros['protein']*100:.1f}%, Fat {macros['fat']*100:.1f}%")
        
        # Calculate macronutrient grams
        daily_carbs = (daily_calories * macros['carb']) / 4  # 4 calories per gram
        daily_protein = (daily_calories * macros['protein']) / 4
        daily_fat = (daily_calories * macros['fat']) / 9  # 9 calories per gram
        
        # Filter by dietary preference
        filtered_df = self.df[self.df['Dietary category'].str.lower() == diet_type.lower()]
        
        meal_plan = []
        nutrients_remaining = {
            'carbs': daily_carbs,
            'protein': daily_protein,
            'fat': daily_fat
        }
        
        for meal in range(meals_per_day):
            # Select foods from different clusters
            cluster_selection = np.random.choice(range(optimal_clusters), 
                                               size=2, 
                                               replace=False)
            
            meal_items = []
            for cluster in cluster_selection:
                cluster_foods = filtered_df[filtered_df['Food_Cluster'] == cluster]
                if not cluster_foods.empty:
                    # Select food that best fits remaining nutrient needs
                    best_food = None
                    best_score = -1
                    
                    for _, food in cluster_foods.iterrows():
                        # Score based on how well it fits remaining needs
                        carb_score = min(food['Data.Carbohydrate'], nutrients_remaining['carbs']) / daily_carbs
                        protein_score = min(food['Data.Protein'], nutrients_remaining['protein']) / daily_protein
                        fat_score = min(food['Data.Fat.Total Lipid'], nutrients_remaining['fat']) / daily_fat
                        
                        total_score = carb_score + protein_score + fat_score
                        
                        if total_score > best_score:
                            best_score = total_score
                            best_food = food
                    
                    if best_food is not None:
                        meal_items.append(best_food)
                        # Update remaining nutrients
                        nutrients_remaining['carbs'] -= best_food['Data.Carbohydrate']
                        nutrients_remaining['protein'] -= best_food['Data.Protein']
                        nutrients_remaining['fat'] -= best_food['Data.Fat.Total Lipid']
            
            if meal_items:
                meal_plan.append(pd.DataFrame(meal_items))
        
        return pd.concat(meal_plan) if meal_plan else None

    def analyze_nutrition(self, plan):
        if plan is None:
            return None
            
        nutrition_summary = plan[nutrition_cols].sum()
        return nutrition_summary
    
class InteractiveNutritionalPlanner(NutritionalPlanGenerator):
    def __init__(self, df):
        super().__init__(df)
    
    def interactive_planning(self):
        """Interactive loop for generating and refining meal plans"""
        print("Welcome to the Interactive Meal Planner!")
        print("Let's start with some basic information about you.")
        
        # Get user information
        while True:
            try:
                height = float(input("Enter your height in cm: "))
                weight = float(input("Enter your weight in kg: "))
                if height <= 0 or weight <= 0:
                    raise ValueError
                break
            except ValueError:
                print("Please enter valid positive numbers for height and weight.")
        
        meals_per_day = 3
        diet_type = 'Vegetarian'
        activity_level = 'moderate'
        nutrition_model = None
        
        # Initial plan generation
        current_plan = None
        while current_plan is None:
            current_plan = self.generate_plan(
                height=height,
                weight=weight,
                meals_per_day=meals_per_day,
                diet_type=diet_type,
                activity_level=activity_level,
                nutrition_model=nutrition_model
            )
            if current_plan is None:
                print("Couldn't generate a plan with current parameters. Trying different options...")
                diet_type = 'Non-Vegetarian' if diet_type == 'Vegetarian' else 'Vegetarian'
        
        # Interactive loop
        while True:
            print("\nCurrent Meal Plan:")
            print(current_plan[['Description', 'Category'] + nutrition_cols].to_string(index=False))
            
            print("\nNutritional Summary:")
            print(self.analyze_nutrition(current_plan))
            
            print("\nOptions:")
            print("1. Change diet type (current: {})".format(diet_type))
            print("2. Change nutrition model (current: {})".format(nutrition_model or 'default'))
            print("3. Replace a specific food")
            print("4. Regenerate entire plan")
            print("5. Save and exit")
            
            choice = input("\nWhat would you like to adjust? (1-5): ")
            
            if choice == '1':
                # Change diet type
                new_diet = input("Enter new diet type (e.g., Vegetarian, Non-Vegetarian, Vegan): ").strip()
                if new_diet.lower() in ['vegetarian', 'non-vegetarian', 'vegan']:
                    diet_type = new_diet
                    print(f"Diet type changed to {diet_type}")
                else:
                    print("Invalid diet type. Keeping current setting.")
            
            elif choice == '2':
                # Change nutrition model
                print("Available nutrition models (can combine with spaces):")
                print("- low/mid/high carb")
                print("- low/mid/high protein")
                print("- low/mid/high fat")
                new_model = input("Enter new nutrition model (or leave blank for default): ").strip()
                if new_model:
                    nutrition_model = new_model
                    print(f"Nutrition model changed to {nutrition_model}")
                else:
                    nutrition_model = None
                    print("Using default nutrition model")
            
            elif choice == '3':
                # Replace specific food
                print("\nCurrent foods in plan:")
                for i, food in enumerate(current_plan['Description']):
                    print(f"{i+1}. {food}")
                
                try:
                    food_num = int(input("Enter the number of the food you want to replace (1-{}): ".format(len(current_plan))))
                    if 1 <= food_num <= len(current_plan):
                        # Find similar foods from same cluster
                        food_to_replace = current_plan.iloc[food_num-1]
                        cluster = food_to_replace['Food_Cluster']
                        same_cluster_foods = self.df[
                            (self.df['Food_Cluster'] == cluster) & 
                            (self.df['Dietary category'].str.lower() == diet_type.lower()) &
                            (self.df['Description'] != food_to_replace['Description'])]
                        
                        if not same_cluster_foods.empty:
                            print(f"\nSuggested alternatives for {food_to_replace['Description']}:")
                            alternatives = same_cluster_foods.sample(min(5, len(same_cluster_foods)))
                            for i, alt in enumerate(alternatives.itertuples()):
                                print(f"{i+1}. {alt.Description} (Carbs: {getattr(alt, 'Data.Carbohydrate'):.1f}g, Protein: {getattr(alt, 'Data.Protein'):.1f}g, Fat: {getattr(alt, 'Data.Fat.Total Lipid'):.1f}g)")
                            
                            alt_choice = input("Enter the number of the alternative you want (or 0 to cancel): ")
                            if alt_choice.isdigit() and 1 <= int(alt_choice) <= len(alternatives):
                                # Replace the food
                                new_food = alternatives.iloc[int(alt_choice)-1]
                                current_plan.iloc[food_num-1] = new_food
                                print(f"Replaced {food_to_replace['Description']} with {new_food['Description']}")
                            else:
                                print("No changes made.")
                        else:
                            print("No suitable alternatives found in the same category.")
                    else:
                        print("Invalid food number.")
                except ValueError:
                    print("Please enter a valid number.")
            
            elif choice == '4':
                # Regenerate entire plan
                print("Generating a new plan with current settings...")
                new_plan = self.generate_plan(
                    height=height,
                    weight=weight,
                    meals_per_day=meals_per_day,
                    diet_type=diet_type,
                    activity_level=activity_level,
                    nutrition_model=nutrition_model
                )
                if new_plan is not None:
                    current_plan = new_plan
                    print("New plan generated!")
                else:
                    print("Couldn't generate a new plan with current settings.")
            
            elif choice == '5':
                # Save and exit
                save = input("Would you like to save this plan? (y/n): ").lower()
                if save == 'y':
                    filename = input("Enter filename to save (e.g., 'my_meal_plan.csv'): ")
                    try:
                        current_plan.to_csv(filename, index=False)
                        print(f"Plan saved to {filename}")
                    except:
                        print("Couldn't save the file.")
                print("Thank you for using the Interactive Meal Planner!")
                break
            
            else:
                print("Invalid choice. Please enter a number between 1-5.")

# Initialize the interactive planner
interactive_planner = InteractiveNutritionalPlanner(df)

# Start the interactive session
interactive_planner.interactive_planning()