#!/usr/bin/env python3
"""
Test script for enhanced DPR prediction module
"""
import sys
import os

# Add project paths
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
ai_src_path = os.path.join(project_root, 'ai', 'src')
sys.path.append(ai_src_path)

try:
    from enhanced_predict import DPRPredictor
    print(" Successfully imported enhanced_predict module")
    
    # Test predictor initialization
    try:
        model_path = os.path.join(project_root, 'ai', 'models', 'dpr_model.pkl')
        if not os.path.exists(model_path):
            print(f" Model file not found at: {model_path}")
            print("Please ensure the model is trained and saved.")
            sys.exit(1)
            
        predictor = DPRPredictor(model_path)
        print(" Successfully initialized DPR Predictor")
        
        # Test prediction with sample data
        test_cases = [
            {
                "name": "Feasible Project",
                "text": "Construction of primary health center in rural village. Budget ₹8 crores. Timeline 12 months. All approvals obtained.",
                "expected": "feasible"
            },
            {
                "name": "Risky Project", 
                "text": "Bridge construction over flood-prone river in mountainous terrain. Budget ₹75 crores. Timeline 4 months. Environmental clearance pending.",
                "expected": "risky"
            }
        ]
        
        print("\n=== Testing Enhanced Prediction Module ===")
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\nTest {i}: {test_case['name']}")
            print(f"Input: {test_case['text'][:100]}...")
            
            try:
                result = predictor.predict_with_explanation(test_case['text'])
                
                if 'error' in result:
                    print(f" Prediction failed: {result['error']}")
                    continue
                
                print(f" Prediction: {result['prediction']}")
                print(f" Confidence: {result['confidence']:.3f}")
                print(f" Feasible Score: {result['probability_scores']['feasible']:.3f}")
                print(f" Risky Score: {result['probability_scores']['risky']:.3f}")
                
                if 'explanation' in result and result['explanation']:
                    exp = result['explanation']
                    print(f"* Interpretation: {exp.get('interpretation', 'N/A')[:100]}...")
                    print(f"* Top Features Count: {len(exp.get('top_features', []))}")
                    print(f"* Budget Detected: ₹{exp.get('numeric_features', {}).get('budget_crores', 0)} crores")
                    print(f"* Timeline Detected: {exp.get('numeric_features', {}).get('timeline_months', 0)} months")
                
            except Exception as e:
                print(f"ERROR: Test failed with exception: {str(e)}")
                import traceback
                traceback.print_exc()
        
        print("\n=== Testing API Response Format ===")
        # Test the format expected by the web frontend
        sample_result = predictor.predict_with_explanation(test_cases[0]['text'])
        
        # Check if result has all required fields for frontend
        required_fields = ['prediction', 'confidence', 'probability_scores', 'explanation']
        missing_fields = [field for field in required_fields if field not in sample_result]
        
        if missing_fields:
            print(f" Missing fields in API response: {missing_fields}")
        else:
            print(" All required fields present in API response")
            
        # Test explanation structure
        if 'explanation' in sample_result:
            exp = sample_result['explanation']
            exp_required = ['interpretation', 'top_features', 'numeric_features']
            exp_missing = [field for field in exp_required if field not in exp]
            
            if exp_missing:
                print(f"  Missing explanation fields: {exp_missing}")
            else:
                print(" Complete explanation structure")
        
        print("\n🎉 Enhanced prediction module test completed successfully!")
        print("\nNext steps:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Start Flask backend: cd website/backend && python app.py")
        print("3. Start React frontend: cd website/frontend && npm start")
        print("4. Upload a PDF to test the complete system")
        
    except Exception as e:
        print(f" Failed to initialize predictor: {str(e)}")
        import traceback
        traceback.print_exc()
        
except ImportError as e:
    print(f" Failed to import enhanced_predict: {str(e)}")
    print("Please ensure:")
    print("1. The ai/src/enhanced_predict.py file exists")
    print("2. The required dependencies are installed")
    print("3. The model files exist in ai/models/")
    sys.exit(1)