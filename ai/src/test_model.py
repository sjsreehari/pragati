import pandas as pd
import joblib
from preprocess import preprocess_dataframe, load_vectorizer, load_encoder

# Load the trained model and preprocessing components
print("Loading trained model and preprocessing components...")
model = joblib.load("models/dpr_model.pkl")
tfidf = load_vectorizer()
encoder = load_encoder()

print("✅ Model loaded successfully!")
print(f"Model classes: {encoder.classes_}")

def predict_dpr_feasibility(text_description):
    """
    Predict if a DPR project is feasible or risky
    
    Args:
        text_description (str): Project description with budget and timeline
    
    Returns:
        dict: Prediction result with label, probability, and confidence
    """
    # Create a temporary DataFrame for preprocessing
    temp_df = pd.DataFrame({
        'text': [text_description],
        'label': ['unknown']  # Placeholder, not used for prediction
    })
    
    # Preprocess the data (extract features)
    X_test, _ = preprocess_dataframe(temp_df, fit_vectorizer=False, tfidf=tfidf)
    
    # Get prediction and probability
    prediction = model.predict(X_test)
    probabilities = model.predict_proba(X_test)
    
    # Convert prediction back to label
    predicted_label = encoder.inverse_transform(prediction)[0]
    
    # Get confidence (max probability)
    confidence = max(probabilities[0]) * 100
    
    # Get probabilities for both classes
    prob_dict = {}
    for i, class_name in enumerate(encoder.classes_):
        prob_dict[class_name] = probabilities[0][i] * 100
    
    return {
        'prediction': predicted_label,
        'confidence': round(confidence, 2),
        'probabilities': {k: round(v, 2) for k, v in prob_dict.items()}
    }

# Test cases with synthetic data
test_cases = [
    {
        "name": "Test 1 - Realistic Hospital Project",
        "description": "Hospital project with 150 beds in Guwahati. Budget ₹120 crore. Timeline 30 months. Includes equipment procurement and staff training."
    },
    {
        "name": "Test 2 - Unrealistic Bridge Timeline",
        "description": "Bridge construction of 8 km over major river in Assam. Budget ₹15 crore. Timeline 1 month."
    },
    {
        "name": "Test 3 - Environmental Issues",
        "description": "Tourism lodge in protected forest area of Kaziranga. Budget ₹12 crore. Timeline 12 months. No environmental clearance obtained."
    },
    {
        "name": "Test 4 - Reasonable School Project",
        "description": "Primary school building with 15 classrooms in rural Manipur. Budget ₹8 crore. Timeline 18 months. Earthquake resistant design."
    },
    {
        "name": "Test 5 - Impossible Hospital Scale",
        "description": "Super specialty hospital with 2000 beds in small town of Nagaland. Budget ₹50 crore. Timeline 12 months."
    },
    {
        "name": "Test 6 - Good Road Project",
        "description": "Highway upgrade of 25 km in Arunachal Pradesh. Budget ₹40 crore. Timeline 24 months. Includes landslide mitigation measures."
    },
    {
        "name": "Test 7 - Unrealistic IT Hub",
        "description": "Major IT park development covering 50,000 sq ft in Shillong. Budget ₹8 crore. Timeline 6 months."
    },
    {
        "name": "Test 8 - Feasible Solar Project",
        "description": "Solar power plant installation of 10 MW capacity in Tripura. Budget ₹60 crore. Timeline 20 months. Grid connectivity planned."
    }
]

print("\n" + "="*80)
print("🧪 TESTING DPR FEASIBILITY MODEL")
print("="*80)

for i, test_case in enumerate(test_cases, 1):
    print(f"\n{test_case['name']}")
    print("-" * 60)
    print(f"📋 Description: {test_case['description']}")
    
    # Get prediction
    result = predict_dpr_feasibility(test_case['description'])
    
    # Display results with color-coded output
    prediction = result['prediction']
    confidence = result['confidence']
    
    if prediction == 'feasible':
        status_icon = "✅"
        status_color = "FEASIBLE"
    else:
        status_icon = "⚠️"
        status_color = "RISKY"
    
    print(f"🎯 Prediction: {status_icon} {status_color}")
    print(f"📊 Confidence: {confidence}%")
    print(f"📈 Probabilities:")
    for label, prob in result['probabilities'].items():
        print(f"   - {label.capitalize()}: {prob}%")

print("\n" + "="*80)
print("🎉 Testing completed!")
print("="*80)

# Interactive testing option
print("\n💡 Want to test your own project description?")
print("You can modify the test_cases list above or create a new test:")
print("""
# Example usage:
custom_description = "Your project description here with Budget ₹X crore. Timeline Y months."
result = predict_dpr_feasibility(custom_description)
print(f"Prediction: {result['prediction']} (Confidence: {result['confidence']}%)")
""")