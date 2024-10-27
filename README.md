# Customer Churn Prediction Web App

This project is an end-to-end pipeline for predicting customer churn, designed to analyze customer data and predict churn probability using multiple machine learning models. It includes data preprocessing, model training, hyperparameter tuning, and an interactive web app for real-time prediction and analysis.

## Table of Contents
- [Features](#features)
- [Technologies Used](#technologies-used)
- [Installation](#installation)
- [Usage](#usage)
- [Model Explanation](#model-explanation)
- [License](#license)

---

## Features

- **Data Preprocessing**: Load and clean customer data to ensure high-quality input for models.
- **Multiple Machine Learning Models**: Trained using:
  - XGBoost
  - Random Forest
  - K-Nearest Neighbors
  - Decision Tree
  - SVM (Support Vector Machine)
- **Hyperparameter Tuning**: Tune models to improve performance and prediction accuracy.
- **Real-Time Inference**: Deploy models with a Streamlit web app to predict customer churn probabilities interactively.
- **Interactive Visualization**: Gauge and bar charts to display individual churn probabilities and model-specific performance.

## Technologies Used

- **Python**: Core programming language for data processing and model development.
- **Groq**: Integrates with OpenAI's API for predictive insights and explanations.
- **Machine Learning**: Utilizes scikit-learn and XGBoost for model training and evaluation.
- **Streamlit**: For deploying the web app and providing an interactive UI.
- **Plotly**: Data visualization for churn probability and model-specific output.
- **Data Science Topics**: 
  - Feature Engineering
  - Data Visualization
  - Model Inference

## Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/your-username/customer-churn-prediction.git
   cd customer-churn-prediction

2. **Set Up Dependencies:**

- Install the required packages listed in requirements.txt:
  ```bash
  pip install -r requirements.txt
  
3. **Set Up API Key (Optional):**
- If using the OpenAI API for predictive insights, ensure the API key is set up as an environment variable:
  ```bash
  export GROQ_API_KEY=your_api_key_here
4. **Run the Application:**
- Start the Streamlit app locally:
  ```bash
  streamlit run main.py
  
## Usage
1. Input Customer Details: Enter customer attributes such as credit score, age, tenure, balance, etc.
2. View Churn Prediction: The app will display a churn probability score and model-specific insights.
3. Generate Retention Email: Get a suggested email template for retaining high-risk customers.

## Model Explanation
This project uses multiple machine learning models to predict the probability of customer churn. Models include:

- XGBoost: Known for its accuracy and efficiency in handling structured data.
- Random Forest: A versatile model that leverages multiple decision trees for better generalization.
- K-Nearest Neighbors: A non-parametric model that predicts based on feature similarity.
- Decision Tree: Simple model that splits features based on entropy or Gini impurity.
- SVM (Support Vector Machine): Effective in high-dimensional spaces for classification tasks.
The final churn probability is computed as an average of the individual model predictions. Visualizations include a gauge chart for overall churn probability and a bar chart comparing the output of each model.

Replace `your-username` with your GitHub username, and if you want to use OpenAI, be sure to add the `GROQ_API_KEY` setup instructions in the **Set Up API Key** section.

Let me know if there's anything else, and good luck with your deployment!