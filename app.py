from flask import Flask, render_template, request, jsonify
from flask_cors import CORS, cross_origin
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq

app = Flask(__name__)

@app.route('/', methods=['GET'])
@cross_origin()
def homePage():
    return render_template("index.html")

@app.route('/review', methods=['POST','GET'])
@cross_origin()
def index():
    if request.method=='POST':
        try:
            searchString = request.form['content'].replace(" ","");
            flipkart_url = "https://www.flipkart.com/search?q=" + searchString
            uClient = uReq(flipkart_url)
            flipkart_page=uClient.read()
            uClient.close()
            flipkart_html = bs(flipkart_page, "html.parser")
            bigboxes=flipkart_html.findAll("div",{"class":"cPHDOP col-12-12"})
            del bigboxes[0:3]
            box=bigboxes[0]
            product_link = "https://www.flipkart.com" + box.div.div.div.a['href']
            prodRes = requests.get(product_link)
            prod_html = bs(prodRes.text, "html.parser")
            print(prod_html)
            commentboxes = prod_html.find_all('div', {'class': "col EPCmJX"})

            filename = searchString + ".csv"
            fw = open(filename, "w")
            headers = "Product, Customer Name, Rating, Heading, Comment \n"
            fw.write(headers)
            reviews = []
            for commentbox in commentboxes:
                try:
                    name=commentbox.find_all('p',{'class':'_2NsDsF AwS1CA'})[0].text

                except:
                    name='No name'

                try:
                    rating = commentbox.div.div.text


                except:
                    rating='No rating'

                try:
                    commenthead = commentbox.div.p.text
                except:
                    commenthead='No comment heading'

                try:
                    comtag = commentbox.find_all('div', {'class': ''})
                    cus_comment = comtag[0].div.text

                except Exception as e:
                    print("Exception will create in directory: ", e)
                    cus_comment = "No comment"


                mydict={"Product": searchString, "Name": name, "Rating":rating,"CommentHead":commenthead,"Comment": cus_comment}
                reviews.append(mydict)
            return render_template('results.html',reviews=reviews[0:len(reviews)-1])
        except Exception as e:
            print("The exception message is", e)
            return 'something went wrong'

    else:
        return render_template('index.html')



if __name__=="__main__":
    app.run(debug=True)


