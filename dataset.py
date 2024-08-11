import pandas as pd
import numpy as np

num_samples = 500

np.random.seed(0)  
heart_rate = np.random.randint(60, 100, size=num_samples)  
temperature = np.random.uniform(36.0, 102.0, size=num_samples)  # Changed the upper limit to 102

data = {
    'Patient_ID': np.arange(1, num_samples + 1),
    'Heart_Rate': heart_rate,
    'Temperature': temperature
}

df = pd.DataFrame(data)

df.to_csv('patient_data.csv', index=False)

print("Dataset generated and saved to 'patient_data.csv'")
