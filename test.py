import json
import logging
import openai
import requests
import streamlit as st
import os
<<<<<<< HEAD
from newsapi import NewsApiClient


def recursive_dict_eval(myDict):
    for key,value in myDict.items():
        try:
            if(isinstance(value, dict)):
                recursive_dict_eval(value)
            evaled_value=ast.literal_eval(value)
            assert isinstance(evaled_value,dict)
            myDict[key]=recursive_dict_eval(evaled_value)

        except (SyntaxError, ValueError, AssertionError):
            #SyntaxError, ValueError are for the literal_eval exceptions
            pass
    return myDict

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

def is_valid_news_api_key(api_key):
    news_api_key = api_key

    try:
        # # Send a test request to the OpenAI API
        # response = openai.Completion.create(model="text-davinci-003",                     
        #             prompt="Hello world")['choices'][0]['text']
        return True
    except Exception:
        pass

    return False

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
        st.write("*News API key active - ready to respond!*")
    else:
        st.warning("News API key not found as an environmental variable.")
        news_api_key = st.text_input("Enter your News API key:", key = news_api_key)

        if st.button("Save", key = news_api_key):
            if is_valid_news_api_key(news_api_key):
                os.environ["NEWS_API_KEY"] = news_api_key
                st.success("News API key saved as an environmental variable!")
                return news_api_key
            else:
                st.error("Invalid API key. Please enter a valid API key.")

class AI:
    def __init__(self) -> None:
        self.functions = [
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
<<<<<<< HEAD
                    "name": "get_headlines",
                    "description": "Looks for subject based news stories and returns the result as a JSON string.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "The news term query to execute. Must be a SINGLE LINE STRING!"}                            
                        },
                        "required": ["query"]
                    }
                }
                
=======
                    "name": "scrape_webpage",
                    "description": "Scrapes a webpage and returns the result as a JSON string.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "url": {"type": "string", "description": "The URL of the webpage to scrape."},
                        },
                        "required": ["url"],
                    },
                },
>>>>>>> 344b110 (test functional!)
            ]
        # self.api_key = st.secrets["OPENAI_API_KEY"]
        self.messages = [
            {"role": "user", "content": "You are a researcher's helper who, as needed, determines facts using Wikidata via the 'wikkidata_sparql-query' function."},
            {"role": "user", "content": "You are a researcher's helper who, as needed, opens a URL to scrape a webpage using 'scrape_webpage' function."},
            ]
    def get_headlines(self, query: str) -> str:
        news_api_key = os.environ["NEWS_API_KEY"]
        st.write(query)
        newsapi = NewsApiClient(api_key=news_api_key)
        # sources = newsapi.get_sources()
        # response = newsapi.get_top_headlines(q=query
                                                #   sources = 'bbc-news, the-verge',
                                                #   category='business',
                                                #   language='en',
                                                #   country='us'
                                                #   )
        try:
            response = newsapi.get_top_headlines(q=query)
            output = json.dumps(response, indent=4)
            return output
        except requests.HTTPError as e:
            return f"A HTTP error occurred: {str(e)}"
        except requests.RequestException as e:
            return f"A request exception occurred: {str(e)}"
        except Exception as e:
            return f"An error occurred: {e}"    
    def wikidata_sparql_query(self, query: str) -> str:
        url = "https://query.wikidata.org/sparql"
        headers = {
            "Accept": "application/sparql-results+json",
            "User-Agent": "SPARQL Query GPT"
        }
        params = {"query": query, "format": "json"}

        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()  # Raises a HTTPError if the status is 4xx, 5xx

            json_response = response.json()

            head = json_response.get("head", {}).get("vars", [])
            results = json_response.get("results", {}).get("bindings", [])

            # Convert the 'head' and 'results' into strings and return them
            result_str = 'Variables: ' + ', '.join(head) + '\n'
            result_str += 'Results:\n'
            for result in results:
                for var in head:
                    result_str += f'{var}: {result.get(var, {}).get("value", "N/A")}\n'
                result_str += '\n'
            return result_str
        except requests.HTTPError as e:
            return f"A HTTP error occurred: {str(e)}"
        except requests.RequestException as e:
            return f"A request exception occurred: {str(e)}"
        except Exception as e:
            return f"An error occurred: {e}"
        
    def scrape_webpage(self, url: str) -> str:
        try:
            headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) ",
            "Referer": "https://www.google.com/",
            }
            headers2 = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7", 
    "Accept-Encoding": "gzip, deflate, br", 
    "Accept-Language": "en-US,en;q=0.9", 
    "Host": "httpbin.org", 
    "Referer": "https://www.scraperapi.com/", 
    "Sec-Ch-Ua": "\"Not.A/Brand\";v=\"8\", \"Chromium\";v=\"114\", \"Microsoft Edge\";v=\"114\"", 
    "Sec-Ch-Ua-Mobile": "?0", 
    "Sec-Ch-Ua-Platform": "\"macOS\"", 
    "Sec-Fetch-Dest": "document", 
    "Sec-Fetch-Mode": "navigate", 
    "Sec-Fetch-Site": "cross-site", 
    "Sec-Fetch-User": "?1", 
    "Upgrade-Insecure-Requests": "1", 
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.58", 
    "X-Amzn-Trace-Id": "Root=1-649f9199-75d5dd99543795db31a59e98"
  }
            st.write(f'Here is the function  captured URL: {url}')
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # Raises a HTTPError if the status is 4xx, 5xx

            # Parse the webpage with BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')

            # Remove any existing <a> tags (hyperlinks)
            for a in soup.find_all('a', href=True):
                a.decompose()

            # Remove any existing <img> tags (images)
            for img in soup.find_all('img', src=True):
                img.decompose()

            # Extract text from the parsed HTML
            text = soup.get_text()

            # Remove extra whitespace
            text = ' '.join(text.split())

            return text
        except requests.HTTPError as e:
            return f"A HTTP error occurred: {str(e)}"
        except requests.RequestException as e:
            return f"A request exception occurred: {str(e)}"
        except Exception as e:
            return f"An error occurred: {e}"
        
    def call_ai(self, new_message):
        if new_message:
            self.messages.append({"role": "user", "content": new_message})

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0613",
            messages=self.messages,
            functions=self.functions,
            function_call="auto",
            )
        msg = json.dumps(response['choices'][0]['message'])
        mid_process = json.loads(msg)
        arguments = json.loads(mid_process['function_call']['arguments'])
        query = arguments["query"]
        st.write(f'initial message: {msg}')
        # msg = response['choices'][0]['message'].to_dict()
        st.write(f'dict processed message: {query}')
        self.messages.append(msg)
        if mid_process['content']:
            logging.debug(mid_process['content'])
        if 'function_call' in mid_process:
            st.write(mid_process['function_call'])
            st.write(mid_process['function_call']['name'])
            st.write(mid_process['function_call']['arguments'])
            # dict_received = msg['function_call']['arguments']
            # dict_received = recursive_dict_eval(dict_received)
            # st.write(dict_received['query'])
            # ['function_call']['name'] tells us which function we should call
            if mid_process['function_call']['name'] == 'wikidata_sparql_query':
                # ['function_call']['arguments'] contains the arguments of the function
                logging.debug(mid_process['function_call']['arguments'])
                # Here, we call the requested function and get a response as a string
                function_response = self.wikidata_sparql_query(mid_process['function_call']['arguments'])
                logging.debug(function_response)
                # We add the response to messages
                self.messages.append({"role": "function", "name": mid_process["function_call"]["name"], "content": function_response})

                self.call_ai(new_message=None) # pass the function response back to AI
                
            if mid_process['function_call']['name'] == 'get_headlines':
                # ['function_call']['arguments'] contains the arguments of the function
                logging.debug(mid_process['function_call']['arguments'])
                # Here, we call the requested function and get a response as a string
                function_response = self.get_headlines(query)
                logging.debug(function_response)
                # We add the response to messages
                self.messages.append({"role": "function", "name": mid_process["function_call"]["name"], "content": function_response})

                self.call_ai(new_message=None) # pass the function response back to AI
                
            if msg['function_call']['name'] == 'scrape_webpage':
                # ['function_call']['arguments'] contains the arguments of the function
                logging.debug(msg['function_call']['arguments'])
                # Here, we call the requested function and get a response as a string
                st.write("sending message to scrape_webpage")
                # url = extract_url(msg['function_call']['arguments'])
                st.write(f' here is the full message: {msg}')
                st.write(f" here is the supposed url: {msg['function_call']['arguments']}")
                real_url = json.loads(msg['function_call']['arguments'])['url']
                st.write(f' here is the real url: {real_url}')
                function_response = self.scrape_webpage(real_url)
                # function_response = self.scrape_webpage(url)
                st.write("got response from scrape_webpage")
                st.write(function_response)
                logging.debug(function_response)
                # We add the response to messages
                self.messages.append({"role": "function", "name": msg["function_call"]["name"], "content": function_response})

                self.call_ai(new_message=None) # pass the function response back to AI

    def get_last_message(self):
        return self.messages[-1]['content']

st.title("Wikidata Researcher Helper")

check_openai_api_key()
check_news_api_key()
if os.environ.get("OPENAI_API_KEY"):
    ai = AI()
    input = st.text_input("Enter your message here:")
    if st.button("Send"):
        # answer_old = ai.get_last_message()
        # st.write(answer_old)
        ai.call_ai(input)
        answer = ai.get_last_message()
        st.write(answer)
