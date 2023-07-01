import openai
import streamlit as st
from streamlit_chat import message
import os
from dotenv import dotenv_values, load_dotenv
from random import randint
from PIL import Image
from bs4 import BeautifulSoup
from functions import function_params, wikidata_sparql_query, scrape_webpage, write_file, knowledgebase_create_entry, knowledgebase_list_entries, knowledgebase_read_entry, python_repl, read_csv_columns, image_to_text, read_file, edit_file, list_history_entries, write_history_entry, read_history_entry, query_wolframalpha
# from functions import function_params, wikidata_sparql_query
import json

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

system_message = """
PersonalAssistant:
===CONSTRAINTS===
You are genius level intelligent and knowledgable in every domain and field.
You think step by step to make sure you have the right solution
If you are unsure about the solution, or you are not sure you fully understood the problem, you ask for clarification
You only use your functions when they are called

===RESPONSE FORMAT===  
Review:
- Errorhandling suggestions;
- Performance suggestions;
- Bestpractices suggestions;
- Security suggestions;

Ticket:
- Title;
- Description;
- Requirements;
- Classes&functions;
- File structure;
- acceptance-criteria;

Brainstorm:
- Problem;
- Approach;
- Technology;
- Pros&Cons;

===COMMANDS===
/python [idea] - Calls the python_repl function.
/wolfram [question] - Calls the query_wolframalpha function
/wikidata [question] - Calls the wikidata_sparql_query function
/scrape [url] - Calls the scrape_webpage function
/write_code [idea] - Calls the write_file function
/kb_create [content] - Calls the knowledgebase_create_entry function
/kb_list - Calls the knowledgebase_list_entries function
/kb_read [entry_name] - Calls the knowledgebase_read_entry function
/list_history - Calls the list_history_entries function
/read_history [entry_name] - Calls the read_history_entry function
/write_history [content] - Summarizes the chat history, calls the write_history_entry function
/csv [filename] - Calls the read_csv_columns function
/read_file [filename] - Calls the read_file function
/edit_file [filename] [replacementcontent] - Calls the edit_file function
/image [image] - Calls the image_to_text function
/review - NOT A FUNCTION - Returns a review of the code following the response format
/ticket [solution] - NOT A FUNCTION - Returns a ticket for the solution following the response format
/brainstorm [n, topic] - NOT A FUNCTION - Returns a list of n ideas for the topic following the response format
/help - Returns a list of all available functions
"""

system_message2 = """
PersonalAssistant:
===CONSTRAINTS===
You recive the responses from the functions PersonalAssistant has called

===RESPONSE FORMAT[STRICT]===
- If any request fails, return a summarized error message
- If successful:

* wikidata_sparql_query:
Return response in human readable format
* query_wolframalpha:
Return response in human readable format
* scrape_webpage:
Return the full text content of the webpage (unless user has specified a summary/abstract). 
ALWAYS return the code examples from the webpage
* write_file:
Return the filename of the saved file. 
Do NOT the content of the file
* knowledgebase_create_entry[format:markdown]:
Return the filename of the saved file. 
Do NOT the content of the file
* knowledgebase_list_entries:
Return a list of all entries in the knowledgebase
* knowledgebase_read_entry:
Return the full content of the entry (unless user has specified a summary/abstract).
ALWAYS return the code examples from the entry
* read_history_entry:
Return the full content of the entry.
ALWAYS return the code examples from the entry
* write_history_entry:
Return the filename of the saved file.
Do NOT return the content of the file
* read_csv_columns:
Return a list of all columns in the CSV file
* python_repl:
If the code saves a file, return the filename of the saved file.
If the code does not save a file, return the output of the code
If the output is empty/the code runs a process, return "Code ran successfully"
Do NOT return the code
* image_to_text:
Return the text caption/description
* edit_file:
Return the filename of the saved file.
Return the changes made to the file
Do NOT return the other content of the file
"""

st.set_page_config(page_title='Chat with Functions', layout = 'centered', page_icon = ':heart_hands:', initial_sidebar_state = 'auto')
load_dotenv()

if 'last_response' not in st.session_state:
     st.session_state.last_response = ''
     
def check_openai_api_key():
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
                return api_key
            else:
                st.error("Invalid API key. Please enter a valid API key.")
                
def check_news_api_key():
    news_api_key = os.environ.get("NEWS_API_KEY")
    if news_api_key:
        st.write("*News API key active - ready to check the news!*")
    else:
        st.warning("NewsAPI key not found as an environmental variable.")
        news_api_key = st.text_input("Enter your NewsAPI key:")
        if st.button("Save"):
            # if is_valid_api_key(news_api_key):
            #     os.environ["NEWS_API_KEY"] = news_api_key
            os.environ["NEWS_API_KEY"] = news_api_key
            st.success("News API key saved as an environmental variable!")
            # else:
            #     st.error("Invalid API key. Please enter a valid API key.")
            return news_api_key

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

def testbot(question):
    if "messages" not in st.session_state:
        st.session_state["messages"] = [
            # {"role": "system", "content": prefix_teacher},
            # {"role": "user", "content": "Who won the world series in 2020?"},
            # {"role": "assistant", "content": "I'm sorry, that is outside my expertise in data science and medicine."},
            {"role": "assistant", "content": "Hi! Ask me wikidata questions or python code to execute."}
            ]
    st.session_state.messages.append({"role": "user", "content": question})
    COMPLETION_MODEL = "gpt-3.5-turbo-0613"
    response = openai.ChatCompletion.create(
        model=COMPLETION_MODEL,
        messages=st.session_state.messages,
        functions=[
            {
            "name": "wikidata_sparql_query",
            "description": "Executes a SPARQL query on Wikidata and returns the result as a JSON string.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "The SPARQL query to execute. Must be a SINGLE LINE STRING!"},
                },
                "required": ["query"],
                },
            },
            {
            "name": "python_repl",
            "description": "Executes the provided Python code and returns the output.",
            "parameters": {
                "type": "object",
                "properties": {
                    "code": {"type": "string", "description": "The Python code to execute. Remember to print the output!"},
                },
                "required": ["code"],
                },
            },
        ],
        temperature=0,
    )
    if response.choices[0]["finish_reason"] == "stop":
        st.write(response.choices[0]["message"]["content"])
        # break

    elif response.choices[0]["finish_reason"] == "function_call":
        fn_name = response.choices[0].message["function_call"].name
        arguments = response.choices[0].message["function_call"].arguments
        step2(fn_name, arguments)

def step2(fn_name, arguments):
    
    function = locals()[fn_name]
    result = function(arguments)

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": None,
            "function_call": {
                "name": fn_name,
                "arguments": arguments,
            },
        }
    )

    st.session_state.messages.append(
        {
            "role": "function", 
            "name": fn_name, 
            "content": f'{{"result": {str(result)} }}'}
    )


    
                
def start_chatbot():

    # openai_api_key = st.text_input('OpenAI API Key',key='chatbot_api_key')
    prefix_teacher = """You politely decline to answer questions outside the domains of data science, statistics, and medicine. 
    If the question is appropriate, you teach for students at all levels. Your response appears next to a web  
    tool that can generate bar charts, violin charts, histograms, pie charts, scatterplots, and summary statistics for  sample datasets or a user supplied CSV file.         
    """
    # st.write("💬 Chatbot Teacher")
    
        # Check if the API key exists as an environmental variable
    # api_key = st.secrets["OPENAI_API_KEY"]
    
    # try:
    #     api_key = st.secrets["OPENAI_API_KEY"]
    #     # api_key = st.secrets["OPENAI_API_KEY"]
    #     # os.environ["OPENAI_API_KEY"] = api_key
    #     st.write("*API key active - ready to respond!*")
    # except:
    #     st.warning("OpenAPI key not found as an environmental variable.")
    #     api_key = st.text_input("Enter your OpenAI API key:")

    #     if st.button("Save"):
    #         if is_valid_api_key(api_key):
    #             os.environ["OPENAI_API_KEY"] = api_key
    #             st.success("API key saved as an environmental variable!")
    #             st.secrets["OPENAI_API_KEY"] = os.environ["OPENAI_API_KEY"]
    #         else:
    #             st.error("Invalid API key. Please enter a valid API key.")

    # try:
    #     news_api_key = st.secrets["NEWS_API_KEY"]
    #     st.write("*News API key active - ready to check the news!*")
    # except:
    #     st.warning("NewsAPI key not found as an environmental variable.")
    #     news_api_key = st.text_input("Enter your NewsAPI key:")

    #     if st.button("Save"):
    #         # if is_valid_api_key(news_api_key):
    #         #     os.environ["NEWS_API_KEY"] = news_api_key
    #         st.success("News API key saved as an environmental variable!")
    #         # else:
    #         #     st.error("Invalid API key. Please enter a valid API key.")
    
        
    if "messages" not in st.session_state:
        st.session_state["messages"] = [
            # {"role": "system", "content": prefix_teacher},
            # {"role": "user", "content": "Who won the world series in 2020?"},
            # {"role": "assistant", "content": "I'm sorry, that is outside my expertise in data science and medicine."},
            {"role": "assistant", "content": "Hi! Ask me anything about data science and I'll try to answer it."}
            ]

    with st.form("chat_input", clear_on_submit=True):
        a, b = st.columns([4, 1])
        prompt = a.text_input(
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
        
    if prompt:
        st.session_state.messages.append({"role": "system", "content": system_message})
        st.session_state.messages.append({"role": "user", "content": prompt})
        try:
            #Make your OpenAI API request here
            # response = openai.Completion.create(model="gpt-3.5-turbo",                     
            #             prompt="Hello world")['choices'][0]['text']
            # system_set = {"role": "system", "content": prefix_teacher}
            # prefixed_message = prefix_teacher + st.session_state.messages
            response = openai.ChatCompletion.create(model="gpt-3.5-turbo-0613", messages=st.session_state.messages, functions = function_params, function_call="auto")
            response_message = response["choices"][0]["message"]
            if response_message.get("function_call"):
                # Step 3: call the function
                # Note: the JSON response may not always be valid; be sure to handle errors
                available_functions = {
                    "wikidata_sparql_query": wikidata_sparql_query,
                }  # only one function in this example, but you can have multiple
                function_name = response_message["function_call"]["name"]
                function_args = response_message["function_call"]["arguments"]
                st.write(f"Function name: {function_name}")
                st.write(f"Function arguments: {function_args}")

                if function_name == "python_repl":
                    function_response = python_repl(function_args.get("code"))
                elif function_name == "query_wolframalpha":
                    function_response = query_wolframalpha(function_args.get("query"))
                elif function_name == "knowledgebase_read_entry":
                    function_response = knowledgebase_read_entry(*function_args.values())
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": function_response,  # directly add function response to the conversation
                    })
                    return function_response, st.session_state.messages  # directly return function response
                elif function_name == "read_history_entry":
                    function_response = read_history_entry(*function_args.values())
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": function_response,  # directly add function response to the conversation
                    })
                    return function_response, st.session_state.messages  # directly return function response
                elif function_name == "write_history_entry":
                    function_response = write_history_entry(*function_args.values())
                elif function_name == "list_history_entries":
                    function_response = list_history_entries(*function_args.values())
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": function_response,  # directly add function response to the conversation
                    })
                    return function_response, st.session_state.messages  # directly return function response
                elif function_name == "knowledgebase_list_entries":
                    function_response = knowledgebase_list_entries()
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": function_response,  # directly add function response to the conversation
                    })
                    return function_response, st.session_state.messages
                elif function_name in ["knowledgebase_create_entry","knowledgebase_update_entry", "read_csv_columns", "write_file"]:
                    function_response = globals()[function_name](*function_args.values())
                elif function_name == "wikidata_sparql_query":
                    function_response = wikidata_sparql_query(function_args.get("query"))
                elif function_name == "scrape_webpage":
                    function_response = scrape_webpage(function_args.get("url"))
                elif function_name == "image_to_text":
                    function_response = image_to_text(function_args.get("filename"))
                elif function_name == "read_file":
                    function_response = read_file(function_args.get("filename"))
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": function_response,  # directly add function response to the conversation
                    })
                    return function_response, st.session_state.messages  # directly return function response
                elif function_name == "edit_file":
                    filename = function_args.get("filepath")
                    changes = function_args.get("changes")
                    function_response = edit_file(filename, changes)

                # logging.info(f"Function response: {function_response}")
        
                second_response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo-16k-0613",
                    messages=[
                        {"role": "system", "content": system_message2},
                        {"role": "user", "content": prompt},
                        message,
                        {
                            "role": "function",
                            "name": function_name,
                            "content": function_response,
                        },
                    ],
                )
                st.session_state.messages.append(second_response["choices"][0]["message"]) 
                return second_response["choices"][0]["message"]["content"], conversation  # Return the conversation here
            else:
                st.session_state.messages.append(message)
                return message["content"], st.session_state.messages  # Return the message here
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
        message(prompt, is_user=True, key = "using message")
        message(msg.content, key = "last message")
                    


st.title("Chatbot with Functions")
with st.expander('About Chatbot'):
    st.write("Author: David Liebovitz, MD, Northwestern University")
    st.write("Last updated 6/20/23")
    st.write(os.getenv("password"))
 
activate_chatbot = st.checkbox("Activate Chatbot with Functions", key = "activate chatbot")   
if activate_chatbot:
    if check_password():
        api_key = check_openai_api_key()
        question = st.text_input("What would you like to ask the chatbot?", key = "user input")
        if st.button("Start Chatbot"):
            # response = testbot(question)

            # testbot(question)
            response = testbot(st.session_state.messages)
            st.write(response)
            st.write(response.choices[0]["message"]["content"])


        

        
    # st.sidebar.text_area("Teacher:", value=st.session_state.last_response, height=600, max_chars=None)
    
