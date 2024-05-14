from flask import Flask , request ,jsonify
import asyncio
from collections import namedtuple
import requests
from bs4 import BeautifulSoup
import time
import spacy


app = Flask(__name__)

@app.route('/')
def index():
    return '<h1>Home Page</h1><form method="post"> <input type="text" name"input"><input type="submit"></form>'

# @app.route('/api', methods=['POST','GET'])
# def api():
#     user_input = request.args.get('input')
#     # input you will find in the end of url 
#     response = generate_response(user_input)

#     json = {
#         'input': user_input,
#         'response': response.response,
#         'accuracy': response.accuracy
#     }
#     return json

@app.route('/', methods=['POST','GET'])
def api():
    user_input = 'tv'
    print("sssssssssssssssss"+ user_input)
    # input you will find in the form data
    if(request.method == 'POST'):
    # Generate the response based on the user input
        response = generate_response(user_input)
    # Create a JSON object with the response data
        json_data = {
            'input': user_input,
            'response': response.response,
            'accuracy': response.accuracy
            }
        # Return the JSON response
        return jsonify(json_data)
    else:
        return jsonify("ahmeddddddd")
        

    



# Function to extract product names from user input
# Load spaCy's English model
nlp = spacy.load('en_core_web_sm')

# Function to extract product names from user input
def extract_product_name(text):
    doc = nlp(text)
    product_name = ""

    # Check for product nouns using POS tagging
    product_nouns = [token.text for token in doc if token.pos_ == "NOUN"]

    # Check for product entities using NER
    product_entities = [ent.text for ent in doc.ents if ent.label_ == "PRODUCT"]

    # Combine product nouns and entities
    potential_products = product_nouns + product_entities

    if potential_products:
        # Select the longest potential product as the final product name
        product_name = max(potential_products, key=len)

    return product_name




# function that take product name and search on amazon
def newsearch_amazon(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36'
        }

        # Send a GET request to the provided URL with headers
        response = requests.get(url, headers=headers)
        
        # Retry logic for 503 error
        max_retries = 150
        retries = 0
        while response.status_code == 503 and retries < max_retries:
            print('503 error - Retrying...')
            time.sleep(2)  # Wait for 2 seconds before retrying
            response = requests.get(url, headers=headers)
            retries += 1
        
        # If still getting 503 error after retries, return None
        if response.status_code == 503:
            print('503 error - Max retries reached. Service unavailable.')
            return None
        
        # Parse the HTML content of the page
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find all the product containers on the page
        product_containers = soup.find_all('div', {'data-component-type': 's-search-result'})
        
        # Initialize a list to store the results
        results = []
        
        # Iterate over each product container
        for container in product_containers:
            # Extract the product title
            title_element = container.find('h2')
            title = title_element.text.strip()
            
            # Extract the product price
            price_element = container.find('span', {'class': 'a-offscreen'})
            price = price_element.text.strip() if price_element else 'Not available'
            
            # Extract the product rating
            rating_element = container.find('span', {'class': 'a-icon-alt'})
            rating = rating_element.text.strip() if rating_element else 'Not rated'
            
            # Extract the product link
            link_element = container.find('a', {'class': 'a-link-normal'})
            link = 'https://www.amazon.com' + link_element['href'] if link_element else 'Link not available'
            
            # Create a dictionary of product details
            product = {
                'title': title,
                'price': price,
                'rating': rating,
                'link': link
            }
            
            # Add the product details to the results list
            results.append(product)
        
        # Return the results
        return results
    
    except requests.exceptions.RequestException as e:
        print('An error occurred:', e)
        return None



Response = namedtuple('Response','response accuracy')






# this part of bot server request and response
def generate_response(user_input: str) -> Response:
    # lc => lowercase
    lc_input = user_input.lower()
    product_name = extract_product_name(lc_input)

    if lc_input == "hello" or lc_input == "hi":
        return Response("Hey there, How i can help you !" , 1)
    elif lc_input == "goodbye" or lc_input == "bye":
        return Response("see you later!" , 1)
    else:
        print(lc_input)
        #first pass input to ntl functions
        # product = extract_product_name(lc_input)
        # print(product)
        result_products = newsearch_amazon('https://www.amazon.com/s?k='+product_name)
        print(result_products)
        return Response(result_products , 1)
        # return Response("Can't understand you.", 0)
    
def process_request():
    user_input = request.form['user_input']
    lc_input = user_input.lower()

    if lc_input == "hello" or lc_input == "hi":
        return jsonify(response="Hey there, How can I help you!")
    elif lc_input == "goodbye" or lc_input == "bye":
        return jsonify(response="See you later!")
    else:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(newsearch_amazon2('https://www.amazon.com/s?k=' + lc_input))
        return jsonify(response=result)

async def newsearch_amazon2(url):
    # Perform asynchronous operations here
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36'
    }
    # Send a GET request to the provided URL with headers
    response = requests.get(url, headers=headers)
    
    # Retry logic for 503 error
    max_retries = 150
    retries = 0
    while response.status_code == 503 and retries < max_retries:
        print('503 error - Retrying...')
        time.sleep(2)  # Wait for 2 seconds before retrying
        response = requests.get(url, headers=headers)
        retries += 1
    
    # If still getting 503 error after retries, return None
    if response.status_code == 503:
        print('503 error - Max retries reached. Service unavailable.')
        return None
    
    # Parse the HTML content of the page
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Find all the product containers on the page
    product_containers = soup.find_all('div', {'data-component-type': 's-search-result'})
    
    # Initialize a list to store the results
    results = []
    
    # Iterate over each product container
    for container in product_containers:
        # Extract the product title
        title_element = container.find('h2')
        title = title_element.text.strip()
        
        # Extract the product price
        price_element = container.find('span', {'class': 'a-offscreen'})
        price = price_element.text.strip() if price_element else 'Not available'
        
        # Extract the product rating
        rating_element = container.find('span', {'class': 'a-icon-alt'})
        rating = rating_element.text.strip() if rating_element else 'Not rated'
        
        # Extract the product link
        link_element = container.find('a', {'class': 'a-link-normal'})
        link = 'https://www.amazon.com' + link_element['href'] if link_element else 'Link not available'
        
        # Create a dictionary of product details
        product = {
            'title': title,
            'price': price,
            'rating': rating,
            'link': link
        }
        
        # Add the product details to the results list
        results.append(product)
    
    # Simulating a delay of 5 seconds
    await asyncio.sleep(5)
    
    # Return the results
    return results


if __name__ == '__main__':
    app.run()

