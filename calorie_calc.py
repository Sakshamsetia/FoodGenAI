import pandas as pd

class CalorieCalculator:
    def __init__(self, data_path):
        """
        Initialize the calculator with the nutrient database
        """
        self.df = pd.read_csv(data_path)
        
    def calculate_calories(self, food_name, serving_size=100):
        """
        Calculate calories for a given food item and serving size
        :param food_name: Name of the food item (partial match allowed)
        :param serving_size: Serving size in grams (default 100g)
        :return: Dictionary with calorie information or None if not found
        """
        # Find matching food items (case insensitive, partial match)
        matches = self.df[self.df['Category'].str.contains(food_name, case=False, na=False)]
        
        if matches.empty:
            return None
            
        # Get the first match (you could modify this to handle multiple matches)
        food = matches.iloc[0]
        
        # Get macronutrient values
        carbs = food['Data.Carbohydrate']
        protein = food['Data.Protein']
        fat = food['Data.Fat.Total Lipid']

        # Calculate calories
        calories = (carbs * 4) + (protein * 4) + (fat * 9)
        adjusted_calories = calories * (serving_size / 100)

        dict1 = {
            'food_name': food['Category'],
            'serving_size_g': serving_size,
            'calories': round(calories, 1),
            'adjusted_calories': round(adjusted_calories, 1),
            'macronutrients': {
                'carbohydrates_g': round(carbs, 1),
                'protein_g': round(protein, 1),
                'fat_g': round(fat, 1)
            }
        }

        return dict1
    
    def search_foods(self, search_term):
        """
        Search for foods matching a term
        :param search_term: Term to search for in food categories
        :return: List of matching food names
        """
        matches = self.df[self.df['Category'].str.contains(search_term, case=False, na=False)]
        return matches['Category'].tolist()

# Example usage
if __name__ == "__main__":
    # Initialize calculator with the CSV file
    calculator = CalorieCalculator('./nutrient.csv')
    
    # Search for foods based on user input
    search_term = input("Enter a food item to search for: ")
    results = calculator.calculate_calories(search_term)
    if results:
        print(f"""
    Food Information:
    - Name: {results['food_name']}
    - Serving Size: {results['serving_size_g']}g
    - Calories: {results['calories']} kcal (per 100g)
    - Adjusted Calories: {results['adjusted_calories']} kcal (for serving)
    
    Macronutrients (per 100g):
    - Carbohydrates: {results['macronutrients']['carbohydrates_g']}g
    - Protein: {results['macronutrients']['protein_g']}g
    - Fat: {results['macronutrients']['fat_g']}g
    """)
    else:
        print("No matching food items found.")