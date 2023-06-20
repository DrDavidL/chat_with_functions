import openai
import streamlit as st
from streamlit_chat import message
import os
from dotenv import dotenv_values, load_dotenv
from random import randint

# import numpy as np
# import pandas as pd
# from ydata_profiling import ProfileReport
# from streamlit_pandas_profiling import st_profile_report
# import streamlit.components.v1 as components
# import numpy as np
# import plotly.figure_factory as ff
# import matplotlib.pyplot as plt
# import seaborn as sns
# from statsmodels.imputation import mice
# from sklearn.model_selection import train_test_split
# from sklearn.preprocessing import LabelEncoder, StandardScaler
# from sklearn.decomposition import PCA
# from sklearn.metrics import accuracy_score, confusion_matrix, roc_curve, roc_auc_score, average_precision_score, precision_recall_curve, auc, f1_score
# from sklearn.linear_model import LogisticRegression
# from sklearn.tree import DecisionTreeClassifier
# from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
# from sklearn.impute import SimpleImputer
# from sklearn import svm
# # import asyncio
# # import bardapi
# # from bardapi import Bard
# from tableone import TableOne
# from scipy import stats

# import random
# from random import randint
# 



st.set_page_config(page_title='Chat with Functions', layout = 'centered', page_icon = ':heart_hands:', initial_sidebar_state = 'auto')
load_dotenv()

if 'last_response' not in st.session_state:
     st.session_state.last_response = ''

def is_valid_api_key(api_key):
    openai.api_key = api_key

    try:
        # Send a test request to the OpenAI API
        response = openai.Completion.create(model="text-davinci-003",                     
                    prompt="Hello world")['choices'][0]['text']
        return True
    except Exception:
        pass

    return False

def check_password():

    """Returns `True` if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["password"] == os.getenv("password"):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # don't store password
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show input for password.
        st.sidebar.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        st.sidebar.write("*Please contact David Liebovitz, MD if you need an updated password for access.*")
        return False
    elif not st.session_state["password_correct"]:
        # Password not correct, show input + error.
        st.sidebar.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        st.sidebar.error("😕 Password incorrect")
        return False
    else:
        # Password correct.
        return True

                
def start_chatbot():

    # openai_api_key = st.text_input('OpenAI API Key',key='chatbot_api_key')
    prefix_teacher = """You politely decline to answer questions outside the domains of data science, statistics, and medicine. 
    If the question is appropriate, you teach for students at all levels. Your response appears next to a web  
    tool that can generate bar charts, violin charts, histograms, pie charts, scatterplots, and summary statistics for  sample datasets or a user supplied CSV file.         
    """
    st.write("💬 Chatbot Teacher")
    
        # Check if the API key exists as an environmental variable
    api_key = os.environ.get("OPENAI_API_KEY")

    if api_key:
        st.write("*API key active - ready to respond!*")
    else:
        st.warning("API key not found as an environmental variable.")
        api_key = st.text_input("Enter your OpenAI API key:")

        if st.button("Save"):
            if is_valid_api_key(api_key):
                os.environ["OPENAI_API_KEY"] = api_key
                st.success("API key saved as an environmental variable!")
            else:
                st.error("Invalid API key. Please enter a valid API key.")

        
    if "messages" not in st.session_state:
        st.session_state["messages"] = [
            # {"role": "system", "content": prefix_teacher},
            # {"role": "user", "content": "Who won the world series in 2020?"},
            # {"role": "assistant", "content": "I'm sorry, that is outside my expertise in data science and medicine."},
            {"role": "assistant", "content": "Hi! Ask me anything about data science and I'll try to answer it."}
            ]

    with st.form("chat_input", clear_on_submit=True):
        a, b = st.columns([4, 1])
        user_input = a.text_input(
            label="Your question:",
            placeholder="e.g., teach me about violin plots",
            label_visibility="collapsed",
        )
        b.form_submit_button("Send", use_container_width=True)

    for msg in st.session_state.messages:
        a = randint(0, 10000000000)
        message(msg["content"], is_user=msg["role"] == "user", key = a)

    # if user_input and not openai_api_key:
    #     st.info("Please add your OpenAI API key to continue.")
        
    if user_input:
        st.session_state.messages.append({"role": "system", "content": prefix_teacher})
        st.session_state.messages.append({"role": "user", "content": user_input})
        try:
            #Make your OpenAI API request here
            # response = openai.Completion.create(model="gpt-3.5-turbo",                     
            #             prompt="Hello world")['choices'][0]['text']
            # system_set = {"role": "system", "content": prefix_teacher}
            # prefixed_message = prefix_teacher + st.session_state.messages
            response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=st.session_state.messages)
        except openai.error.Timeout as e:
            #Handle timeout error, e.g. retry or log
            print(f"I'm super busy! Please try again in a moment. Thanks! Here's the error detail: {e}")
            pass
        except openai.error.APIError as e:
            #Handle API error, e.g. retry or log
            print(f"OpenAI API returned an API Error: {e}")
            pass
        except openai.error.APIConnectionError as e:
            #Handle connection error, e.g. check network or log
            print(f"OpenAI API request failed to connect: {e}")
            pass
        except openai.error.InvalidRequestError as e:
            #Handle invalid request error, e.g. validate parameters or log
            print(f"OpenAI API request was invalid: {e}")
            pass
        except openai.error.AuthenticationError as e:
            #Handle authentication error, e.g. check credentials or log
            print(f"OpenAI API request was not authorized: {e}")
            pass
        except openai.error.PermissionError as e:
            #Handle permission error, e.g. check scope or log
            print(f"OpenAI API request was not permitted: {e}")
            pass
        except openai.error.RateLimitError as e:
            #Handle rate limit error, e.g. wait or log
            print(f"I'm so busy! Please try again in a moment. Thanks! Here's the error detail: {e}")
            pass

        # response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=st.session_state.messages)
        msg = response.choices[0].message
        st.session_state.messages.append(msg)      
        message(user_input, is_user=True, key = "using message")
        message(msg.content, key = "last message")
                    


st.title("Chatbot with Functions")
with st.expander('About Chatbot'):
    st.write("Author: David Liebovitz, MD, Northwestern University")
    st.write("Last updated 6/20/23")
    st.write(os.getenv("password"))
 
activate_chatbot = st.checkbox("Activate Chatbot with Functions", key = "activate chatbot")   
if activate_chatbot:
    if check_password():
        start_chatbot()
    # st.sidebar.text_area("Teacher:", value=st.session_state.last_response, height=600, max_chars=None)
    
