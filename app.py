from flask import Flask, render_template, request, jsonify
from flask_cors import CORS, cross_origin
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq   # (kept but no longer used)

app = Flask(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.google.com"
}

@app.route('/', methods=['GET'])
@cross_origin()
def homePage():
    return render_template("index.html")

@app.route('/review', methods=['POST','GET'])
@cross_origin()
def index():
    if request.method=='POST':
        try:
            searchString = request.form['content'].replace(" ","")
            flipkart_url = "https://www.flipkart.com/search?q=" + searchString

            # ✅ ✅ CHANGED: SAFE REQUEST WITH HEADERS (replaces uReq)
            flipkart_page = requests.get(flipkart_url, headers=HEADERS, timeout=45).text
            flipkart_html = bs(flipkart_page, "html.parser")

            bigboxes = flipkart_html.findAll("div", {"class": "cPHDOP col-12-12"})
            del bigboxes[0:3]
            box = bigboxes[0]

            product_link = "https://www.flipkart.com" + box.div.div.div.a['href']

            # ✅ ✅ CHANGED: SAFE PRODUCT REQUEST WITH HEADERS
            prodRes = requests.get(product_link, headers=HEADERS, timeout=15)
            prod_html = bs(prodRes.text, "html.parser")

            commentboxes = prod_html.find_all('div', {'class': "col EPCmJX"})

            filename = searchString + ".csv"
            fw = open(filename, "w", encoding="utf-8")
            headers = "Product, Customer Name, Rating, Heading, Comment \n"
            fw.write(headers)

            reviews = []
            for commentbox in commentboxes:
                try:
                    name = commentbox.find_all('p', {'class': '_2NsDsF AwS1CA'})[0].text
                except:
                    name = 'No name'

                try:
                    rating = commentbox.div.div.text
                except:
                    rating = 'No rating'

                try:
                    commenthead = commentbox.div.p.text
                except:
                    commenthead = 'No comment heading'

                try:
                    comtag = commentbox.find_all('div', {'class': ''})
                    cus_comment = comtag[0].div.text
                except Exception as e:
                    cus_comment = "No comment"

                mydict = {
                    "Product": searchString,
                    "Name": name,
                    "Rating": rating,
                    "CommentHead": commenthead,
                    "Comment": cus_comment
                }
                reviews.append(mydict)

            return render_template('results.html', reviews=reviews[0:len(reviews)-1])

        except Exception as e:
            print("The exception message is", e)
            return 'something went wrong'

    else:
        return render_template('index.html')


if __name__ == "__main__":
    app.run(debug=True)
