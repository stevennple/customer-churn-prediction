import streamlit as st
import pandas as pd
import pickle
import numpy as np
import os
from openai import OpenAI
import plotly.graph_objects as go
import utils as ut


api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    st.error("API key for the external service is missing. Please check the environment configuration.")
else:
    client = OpenAI(
        base_url="https://api.groq.com/openai/v1",
        api_key=api_key
    )


def load_model(filename):
  try:
      with open(filename, "rb") as file:
          return pickle.load(file)
  except FileNotFoundError:
      st.write(f"Model file {filename} not found.")
      return None
  except Exception as e:
      st.write(f"Error loading model {filename}: {e}")
      return None
    

xgboost_model = load_model("xgb_model.pkl")
naive_bayes_model = load_model("nb_model.pkl")
random_forest_model = load_model("rf_model.pkl")
decision_tree_model = load_model("dt_model.pkl")
svm_model = load_model("svm_model.pkl")
knn_model = load_model("knn_model.pkl")
voting_classifier_model = load_model("voting_clf.pkl")
xgboost_SMOTE_model = load_model("xgboost-SMOTE.pkl")
xgboost_featureEngineered_model = load_model("xgboost-featureEngineered.pkl")

# Check if any of the critical models failed to load
if xgboost_model is None or random_forest_model is None or knn_model is None:
    st.write("Some models failed to load, please check the model files.")


def prepare_input(credit_score, location, gender, age, tenure, balance,
                   num_products, has_credit_card, is_active_member,
                   estimated_salary):

  input_dict = {
    "CreditScore": credit_score,
    "Age": age,
    "Tenure": tenure,
    "Balance": balance,
    "NumOfProducts": num_products,
    "HasCrCard": int(has_credit_card),
    "IsActiveMember": int(is_active_member),
    "EstimatedSalary": estimated_salary,
    "Geography_France": 1 if location == "France" else 0,
    "Geography_Germany": 1 if location == "Germany" else 0,
    "Geography_Spain": 1 if location == "Spain" else 0,
    "Gender_Male": 1 if gender == "Male" else 0,
    "Gender_Female": 1 if gender == "Female" else 0,
  }

  input_df = pd.DataFrame([input_dict])
  return input_df, input_dict

def make_predictions(input_df, input_dict):
  probabilities = {}
  try:
      probabilities["XGBoost"] = xgboost_model.predict_proba(input_df)[0][1]
  except Exception as e:
      st.write("Error in XGBoost model:", e)

  try:
      probabilities["Random Forest"] = random_forest_model.predict_proba(input_df)[0][1]
  except Exception as e:
      st.write("Error in Random Forest model:", e)

  try:
      probabilities["K-Nearest Neighbors"] = knn_model.predict_proba(input_df)[0][1]
  except Exception as e:
      st.write("Error in K-Nearest Neighbors model:", e)

  if probabilities:
      avg_probability = np.mean(list(probabilities.values()))
  else:
      avg_probability = 0
      st.write("No valid model predictions available.")

  col1, col2 = st.columns(2)

  with col1:
    fig = ut.create_gauge_chart(avg_probability)
    st.plotly_chart(fig, use_container_width=True)
    st.write(f"The customer has a {avg_probability:.2%} chance of churning.")

  with col2:
    fig_probs = ut.create_model_probability_chart(probabilities)
    st.plotly_chart(fig_probs, use_container_width=True)

  return avg_probability


def explain_prediction(probability, input_dict, surname, df):

  prompt = f"""You are an expert data scientist at a bank, where you specialize in interpreting and explaining predictions of machine learning models. 
  
  Your machine learning model has predicated that a customer named {surname} has a {round(probability * 100, 1)}% probability of churning, based on the information provided below. 

  Here is the customer's information:
  {input_dict}

  Here are the machine learning model's top 10 most important features for predicting churn:

                  Feature | Importance
    ------------------------------------------------
           NumOfProducts  |  0.323888
          IsActiveMember  |  0.164146
                     Age  |  0.109550
       Geography_Germany  |  0.091373
                 Balance  |  0.052786
        Geography_France  |  0.046463
           Gender_Female  |  0.045283
         Geography_Spain  |  0.036855
             CreditScore  |  0.035005
        Estimated Salary  |  0.032655
               HasCrCard  |  0.031940
                  Tenure  |  0.030054
              GenderMale  |  0.000000


  {pd.set_option("display.max_columns", None)}

  Here are summary statistics for churned customers:
  {df[df["Exited"] == 1].describe()}

  Here are summary statistics for non-churned customers:
  {df[df["Exited"] == 0].describe()}


  - If the customer has over a 40% risk of churning, generate a 3 sentence explanation of why they are at risk of churning.
  - If the customer has less than a 40% risk of churning, generate a 3 sentence explanation of why they might not be at risk of churning. 
  - Your explanation should be based on the customer's information, the summary statistics of churned and non-churned customers, and the feature importances provided. 

    Don't mention the probability of churning, or the machine learning model, or say anything like "Based on the machine learning model's prediction and top 10 most important features." Just explain the prediction neatly (NO FIRST PERSON). 
    
  """

  print("EXPLANATION PROMPT", prompt)

  raw_response = client.chat.completions.create(
    model="llama-3.2-3b-preview",
    messages=[{
      "role": "user",
      "content": prompt
    }],
  )
  return raw_response.choices[0].message.content


def generate_email(probability, input_dict, explanation, surname):
  prompt = f"""You are a manager at SL Bank. You are responsible for ensuring that customers stay with the bank and are incentivized with various offers. 

  You noticed a customer named {surname} who has a {round(probability * 100, 1)}% probability of churning. 

  Here is the customer's information:
    {input_dict}

  Here is some explanation as to why the customer might be at risk of churning:
    {explanation}

  Generate an email to the customer based on their information, asking them to stay if they are at risk of churning, or offer them incentives so that they stay with the bank.

  Make sure to list out a set of incentives tailored to the customer's situation in a neat bullet point list format Don't ever mention the probability of churning, or the machine learning model to the customer.
  """

  raw_response = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=[{
      "role": "user",
      "content": prompt
    }],
  )

  print("\n\nEMAIL PROMPT", prompt)

  return raw_response.choices[0].message.content




st.title("Customer Churn Prediction")

df = pd.read_csv("churn.csv")

customers = [f"{row['CustomerId']} - {row['Surname']}" for _, row in df.iterrows()]

selected_customer_option = st.selectbox("Select a customer", customers)

if selected_customer_option:
  
  selected_customer_id = int(selected_customer_option.split(" - ")[0])

  print("Selected Customer ID", selected_customer_id)

  selected_surname = selected_customer_option.split(" - ")[1]

  print("Surname", selected_surname)

  selected_customer = df.loc[df["CustomerId"] == selected_customer_id].iloc[0]

  print("Selected Customer", selected_customer)


  col1, col2 = st.columns(2)

  with col1:
    
    credit_score = st.number_input(
      "Credit Score",
      min_value=300,
      max_value=850,
      value=int(selected_customer["CreditScore"]))

    location = st.selectbox(
      "Location", ["Spain", "France", "Germany"],
      index=["Spain", "France", "Germany"].index(
        selected_customer["Geography"]))

    gender = st.radio("Gender", ["Male", "Female"], 
                      index=0 if selected_customer["Gender"] == "Male" else 
                      1)

    age = st.number_input(
      "Age",
      min_value=18,
      max_value=100,
      value=int(selected_customer["Age"]))
    
    tenure = st.number_input(
      "Tenure (years)",
      min_value=0,
      max_value=50,
      value=int(selected_customer["Tenure"]))


  with col2:

    balance = st.number_input(
      "Balance",
      min_value=0.0,
      value=float(selected_customer["Balance"]))

    num_products = st.number_input(
      "Number of Products",
      min_value=1,
      max_value=10,
      value=int(selected_customer["NumOfProducts"]))

    has_credit_card = st.checkbox(
      "Has Credit Card",
      value=bool(selected_customer["HasCrCard"]))

    is_active_member = st.checkbox(
      "Is Active Member",
      value=bool(selected_customer["IsActiveMember"]))

    estimated_salary = st.number_input(
      "Estimated Salary",
      min_value=0.0,
      value=float(selected_customer["EstimatedSalary"]))



  input_df, input_dict = prepare_input(credit_score, location, gender, age, tenure, balance,
                                      num_products, has_credit_card, is_active_member,
                                      estimated_salary)

  avg_probability = make_predictions(input_df, input_dict)

  explanation = explain_prediction(avg_probability, input_dict, selected_customer["Surname"], df)

  st.markdown("---")

  st.subheader("Explanation of Prediction")

  st.markdown(explanation)

  email = generate_email(avg_probability, input_dict, explanation, selected_customer["Surname"])

  st.markdown("---")

  st.subheader("Personalized Email to Customer")

  st.markdown(email)