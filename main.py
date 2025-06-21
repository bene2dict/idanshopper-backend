
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import requests
from bs4 import BeautifulSoup

app = FastAPI()

# Allow frontend (localhost for development)
app.add_middleware(
    CORSMiddleware,
    allow_origins= "http://localhost:3000",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/scrape")
async def scrape(request: Request):
    data = await request.json()
    url = data.get("url")


    if not url:
        return {"error": "No URL provided"}

    try:
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    except Exception as e:
        return {"error": f"Request failed: {str(e)}"}

    if response.status_code != 200:
        return {"error": "Failed to fetch page", data: response}

    soup = BeautifulSoup(response.text, "html.parser")

    # Title
    title_tag = soup.find("h1", {"class": "-fs20 -pts -pbxs"})
    title = title_tag.text.strip() if title_tag else "No title found"

    # Brand
    brand_tag = soup.find("a", string="Sony")
    brand = brand_tag.text.strip() if brand_tag else "No brand found"

    # Seller
    seller_tag = soup.find("a", {"class": "link -bl"})
    sellerName = seller_tag.text.strip() if seller_tag else "No seller found"

    # Current Price
    price_tag = soup.find("span", {"class": "-b -ubpt -tal -fs24 -prxs"})
    currentPrice = price_tag.text.strip() if price_tag else "No current price"

    # Old Price
    old_price_tag = soup.find("span", class_="-tal -gy5 -lthr -fs16 -pvxs -ubpt")
    oldPrice = old_price_tag.text.strip() if old_price_tag else "No old price"


    # Price Change Percent
    discount_tag = soup.find("span", class_="bdg _dsct _dyn -mls")
    priceChangePercent = discount_tag.text.strip() if discount_tag else "No discount info"

    # Image
    image_tag = soup.find("img", {"class": "-fw -fh"})
    image_url = (
        image_tag["data-src"] if image_tag and image_tag.has_attr("data-src")
        else image_tag["src"] if image_tag and image_tag.has_attr("src")
        else "No image found"
    )

    return {
        "title": title,
        "brand": brand,
        "sellerName": sellerName,
        "currentPrice": currentPrice,
        "oldPrice": oldPrice,
        "priceChangePercent": priceChangePercent,
        "image": image_url,
        "url": url,
    }