import os
import sys

# Add the AI_Land_Registry subdirectory to Python's path
base_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(base_dir, 'AI_Land_Registry'))

from AI_Land_Registry.app import create_app

app = create_app()

if __name__ == '__main__':
    # Auto-initialize dataset & models if running app.py directly
    ds_path = app.config['DATASET_PATH']
    if not os.path.exists(ds_path):
        print("Generating synthetic dataset...")
        from AI_Land_Registry.dataset.generate_data import generate_synthetic_data
        generate_synthetic_data(ds_path, n_samples=1000)
        
    price_model_path = os.path.join(app.config['ML_MODEL_FOLDER'], 'price_model.pkl')
    fraud_model_path = os.path.join(app.config['ML_MODEL_FOLDER'], 'fraud_model.pkl')
    
    if not os.path.exists(price_model_path):
        print("Training land valuation prediction model...")
        from AI_Land_Registry.ml.land_price_prediction import train_model as train_price_model
        train_price_model(ds_path, price_model_path)
        
    if not os.path.exists(fraud_model_path):
        print("Training transaction fraud classification model...")
        from AI_Land_Registry.ml.fraud_detection import train_model as train_fraud_model
        train_fraud_model(ds_path, fraud_model_path)
        
    print("\n--- Starting Flask Development Server ---")
    app.run(debug=True, host='127.0.0.1', port=5000)
