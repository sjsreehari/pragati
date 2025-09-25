import pandas as pd
import joblib
import numpy as np
import os
from preprocess import preprocess_dataframe, load_vectorizer, load_encoder
import xgboost as xgb
from sklearn.feature_extraction.text import TfidfVectorizer
import warnings
warnings.filterwarnings('ignore')

class DPRPredictor:
    """Enhanced DPR Feasibility Predictor with confidence scores and explanations"""
    
    def __init__(self, model_path="models/dpr_model.pkl"):
        """Initialize the predictor with pre-trained models"""
        # Handle relative paths properly
        if not os.path.isabs(model_path) and not os.path.exists(model_path):
            # If we're in src/, go up one level to ai/
            model_path = os.path.join("..", model_path)
            
        self.model = joblib.load(model_path)
        
        # Load vectorizer and encoder with proper paths
        model_dir = os.path.dirname(model_path)
        tfidf_path = os.path.join(model_dir, "tfidf.pkl")
        encoder_path = os.path.join(model_dir, "encoder.pkl")
        
        if not os.path.exists(tfidf_path):
            tfidf_path = os.path.join("..", "models", "tfidf.pkl")
        if not os.path.exists(encoder_path):
            encoder_path = os.path.join("..", "models", "encoder.pkl")
            
        self.tfidf = joblib.load(tfidf_path)
        self.encoder = joblib.load(encoder_path)
        
        # Get feature names for explanations
        self.feature_names = (list(self.tfidf.get_feature_names_out()) + 
                             ['budget', 'timeline'])
    
    def predict_with_explanation(self, text, include_translation=False, target_lang="en"):
        """
        Predict DPR feasibility with confidence and feature explanations
        
        Args:
            text (str): DPR text to analyze
            include_translation (bool): Whether to include translation support
            target_lang (str): Target language for translation ("en", "hi", etc.)
            
        Returns:
            dict: Prediction results with confidence and explanations
        """
        try:
            # Handle translation if requested
            original_text = text
            if include_translation and target_lang != "en":
                try:
                    text = self._translate_text(text, target_lang, "en")
                except:
                    # If translation fails, use original text
                    pass
            
            # Create DataFrame for preprocessing
            df = pd.DataFrame([{"text": text}])
            
            # Preprocess the data
            X, _ = preprocess_dataframe(df, fit_vectorizer=False, tfidf=self.tfidf)
            
            # Get prediction and probabilities
            prediction = self.model.predict(X)[0]
            probabilities = self.model.predict_proba(X)[0]
            
            # Decode prediction
            prediction_label = self.encoder.inverse_transform([prediction])[0]
            
            # Calculate confidence (max probability)
            confidence = float(np.max(probabilities))
            
            # Get feature importances and explanations
            feature_explanation = self._get_feature_explanation(X, text, prediction)
            
            # Prepare result
            result = {
                "prediction": prediction_label,
                "confidence": round(confidence, 3),
                "probability_scores": {
                    "feasible": round(float(probabilities[self._get_feasible_idx()]), 3),
                    "risky": round(float(probabilities[self._get_risky_idx()]), 3)
                },
                "explanation": feature_explanation,
                "original_text": original_text,
                "processed_text": text if text != original_text else None,
                "translation_used": include_translation and text != original_text
            }
            
            return result
            
        except Exception as e:
            return {
                "error": f"Prediction failed: {str(e)}",
                "prediction": "error",
                "confidence": 0.0
            }
    
    def _get_feasible_idx(self):
        """Get the index for 'feasible' class"""
        try:
            return list(self.encoder.classes_).index('feasible')
        except:
            return 0
    
    def _get_risky_idx(self):
        """Get the index for 'risky' class"""
        try:
            return list(self.encoder.classes_).index('risky')
        except:
            return 1
    
    def _get_feature_explanation(self, X, text, prediction):
        """
        Generate feature-based explanations for the prediction
        """
        try:
            # Get feature importances from the model
            if hasattr(self.model, 'feature_importances_'):
                feature_importances = self.model.feature_importances_
            else:
                # For models without feature_importances_, use a simple approach
                feature_importances = np.abs(X.toarray()[0])
                feature_importances = feature_importances / np.sum(feature_importances)
            
            # Get top features
            top_indices = np.argsort(feature_importances)[-10:][::-1]  # Top 10 features
            
            # Extract relevant features with their values
            X_dense = X.toarray()[0] if hasattr(X, 'toarray') else X[0]
            
            top_features = []
            for idx in top_indices:
                if idx < len(self.feature_names) and X_dense[idx] > 0:
                    feature_name = self.feature_names[idx]
                    feature_value = float(X_dense[idx])
                    importance = float(feature_importances[idx])
                    
                    # Categorize feature type
                    if feature_name in ['budget', 'timeline']:
                        feature_type = "numeric"
                        readable_name = feature_name.title()
                    else:
                        feature_type = "text"
                        readable_name = f"Word: '{feature_name}'"
                    
                    top_features.append({
                        "feature": readable_name,
                        "value": round(feature_value, 3),
                        "importance": round(importance, 3),
                        "type": feature_type
                    })
            
            # Extract budget and timeline for easy interpretation
            budget_value = self._extract_budget(text)
            timeline_value = self._extract_timeline(text)
            
            # Generate interpretation
            interpretation = self._generate_interpretation(
                prediction, budget_value, timeline_value, text
            )
            
            return {
                "top_features": top_features[:5],  # Limit to top 5 for clarity
                "numeric_features": {
                    "budget_crores": budget_value,
                    "timeline_months": timeline_value
                },
                "interpretation": interpretation,
                "explanation_type": "feature_importance"
            }
            
        except Exception as e:
            return {
                "error": f"Explanation generation failed: {str(e)}",
                "top_features": [],
                "interpretation": "Unable to generate explanation"
            }
    
    def _extract_budget(self, text):
        """Extract budget value from text"""
        import re
        m = re.search(r"Budget[^\d]*(\d+)", str(text))
        return float(m.group(1)) if m else 0.0
    
    def _extract_timeline(self, text):
        """Extract timeline value from text"""
        import re
        m = re.search(r"Timeline[^\d]*(\d+)", str(text))
        return float(m.group(1)) if m else 0.0
    
    def _generate_interpretation(self, prediction, budget, timeline, text):
        """Generate human-readable interpretation of the prediction"""
        prediction_label = self.encoder.inverse_transform([prediction])[0]
        
        interpretation_parts = []
        
        # Budget analysis
        if budget > 0:
            if budget > 50:
                interpretation_parts.append("High budget project (₹{:.0f} crores) indicates significant investment".format(budget))
            elif budget > 10:
                interpretation_parts.append("Medium budget project (₹{:.0f} crores)".format(budget))
            else:
                interpretation_parts.append("Low budget project (₹{:.0f} crores)".format(budget))
        
        # Timeline analysis
        if timeline > 0:
            if timeline > 24:
                interpretation_parts.append("Long timeline ({:.0f} months) suggests complex implementation".format(timeline))
            elif timeline > 6:
                interpretation_parts.append("Moderate timeline ({:.0f} months)".format(timeline))
            else:
                interpretation_parts.append("Short timeline ({:.0f} months) indicates quick execution".format(timeline))
        
        # Project type detection
        text_lower = text.lower()
        if any(word in text_lower for word in ['bridge', 'road', 'highway']):
            interpretation_parts.append("Infrastructure project detected")
        elif any(word in text_lower for word in ['hospital', 'health', 'medical']):
            interpretation_parts.append("Healthcare project detected")
        elif any(word in text_lower for word in ['school', 'college', 'education']):
            interpretation_parts.append("Educational project detected")
        
        # Risk factors
        risk_indicators = []
        if 'flood' in text_lower:
            risk_indicators.append("flood-prone area")
        if 'forest' in text_lower:
            risk_indicators.append("forest clearance needed")
        if any(word in text_lower for word in ['hill', 'mountain', 'terrain']):
            risk_indicators.append("challenging terrain")
        
        if risk_indicators:
            interpretation_parts.append("Risk factors: " + ", ".join(risk_indicators))
        
        # Final assessment
        if prediction_label.lower() == 'feasible':
            interpretation_parts.append("✅ Project appears feasible based on available information")
        else:
            interpretation_parts.append("⚠️  Project shows risk indicators requiring attention")
        
        return ". ".join(interpretation_parts) + "."
    
    def _translate_text(self, text, from_lang, to_lang):
        """
        Simple translation wrapper (can be enhanced with actual translation service)
        For now, returns original text as translation services need API keys
        """
        # Placeholder for translation functionality
        # In a real implementation, you would use services like:
        # - Google Translate API
        # - Microsoft Translator
        # - Local translation models
        
        # For demo purposes, we'll just return the original text
        return text
    
    def batch_predict(self, texts, include_explanations=True):
        """Predict multiple DPRs at once"""
        results = []
        for i, text in enumerate(texts):
            try:
                result = self.predict_with_explanation(text)
                result['id'] = i
                results.append(result)
            except Exception as e:
                results.append({
                    'id': i,
                    'error': str(e),
                    'prediction': 'error',
                    'confidence': 0.0
                })
        return results

# Factory function for easy import
def create_predictor(model_path="models/dpr_model.pkl"):
    """Create and return a DPR predictor instance"""
    return DPRPredictor(model_path)

# Example usage and testing
if __name__ == "__main__":
    # Test the enhanced predictor
    import os
    model_path = os.path.join("..", "models", "dpr_model.pkl")
    if not os.path.exists(model_path):
        print(f"❌ Model not found at: {model_path}")
        print("Please train the model first using: python train.py")
        exit(1)
        
    predictor = DPRPredictor(model_path)
    
    # Test case 1: Feasible project
    test_text_1 = "Construction of primary health center in rural area. Budget ₹5 crores. Timeline 18 months. Government approved project with all clearances."
    
    # Test case 2: Risky project  
    test_text_2 = "Bridge construction over flood-prone river in hilly terrain. Budget ₹50 crores. Timeline 6 months. Environmental clearance pending."
    
    print("=== DPR Feasibility Prediction Test ===\n")
    
    print("Test 1 - Expected: Feasible")
    result_1 = predictor.predict_with_explanation(test_text_1)
    print(f"Prediction: {result_1['prediction']}")
    print(f"Confidence: {result_1['confidence']}")
    print(f"Interpretation: {result_1['explanation']['interpretation']}\n")
    
    print("Test 2 - Expected: Risky")
    result_2 = predictor.predict_with_explanation(test_text_2)
    print(f"Prediction: {result_2['prediction']}")
    print(f"Confidence: {result_2['confidence']}")
    print(f"Interpretation: {result_2['explanation']['interpretation']}")
    
    print("\n=== Top Features ===")
    for feature in result_2['explanation']['top_features']:
        print(f"- {feature['feature']}: {feature['value']} (importance: {feature['importance']})")