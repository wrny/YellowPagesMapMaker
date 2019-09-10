# Yellow Pages Map Maker

A python script using Requests / BeautifulSoup to scrape data from yellowpages.com and ping the US Census Bureau API, and after that, use Pandas / Folium to make interactive HTML maps.

## Video

Video example can be viewed here:

[Google Drive](https://drive.google.com/file/d/10OfOoSVWukmcZoa9xfatCvmfME0YV6zh/view)

## About

Data is just a collection of numbers until you turn it into a story--and stories do better with maps. Map-based data visualization is one of the cooler things you can do with programming and with the Folium python module, maps are a snap! Naturally, you can put in any data (sales, prices, landmarks, etc.) you want, but I chose business data because it's really easy to gather.

Much of the code included in here is extracting addresses from yellowpages.com, and pinging the US Census Bureau's geocoding API, which is a decent (and free!) alternative to using paid services such as Google Maps.

Once the data is in a proper format, we iterate through all of the addresses and add points to a OpenStreetMaps map and display the data on an HTML page.

## What does this script do?

The script:

* Scrapes business address data from yellowpages.com using the Requests and BeautifulSoup modules with inputs from the command line (via the Argparse module).
* Writes it to a DataFrame, separating the street, city, state and zipcode into their own columns using Pandas.
* Uses the free US Census Bureau Data API to geocode the addresses (via Requests / Pandas)
* Drops incorrect / improperly formatted addresses and writes the properly formatted data to a csv file.
* Creates an HTML map using OpenStreetMaps and the Folium module

The program will accept arguments such as location, search term and number of pages you want to scrape. San Francisco, CA might have hundreds of veternarians, Topeka, HS has fewer. Selecting the number of pages you wish to scrape makes this easier to manage.

## Issues

If the addresses aren't properly formatted, then the Census Bureau API can't geocode them and so they're dropped from the map and the CSV file. Some of this is the fault of the person putting in the yellow pages ad, but regardless, the Goolge Maps API does a better job here. You get what you pay for!

At the time of this writing, yellowpages.com has no scraping protection whatsoever--they don't even require a proper user agent header to visit their stage. I included one anyway--but if they put in any additional protection, the scraping portion of the script likely won't work any longer. You'd have to use Selenium to visit the page, get the HTML to parse that HTML with BeautifulSoup.

## Usage

To use:

* Have a working Internet connection
* Download the files from this Git repository
* open up command line / go to the directory
* If it's your first time using the program, enter in:

```bash
pip install -r requirements.txt
```

then type:

```bash
python yellowpages_map.py
```

along with the (required!) arguements you want to search for and make a map for.

* -l / -location: physical location that you're searching for
* -s / -search_term: term you're searching for
* -p / -pages: The number of pages you want to scrape.

The below entry:

```bash
python yellowpages_map.py -l "San Francisco, CA" -s "Dog Walker" -p 5
```

Will scrape five pages (-p) of "Dog Walker" (-s) businesses in "San Francisco, CA" (-l).

The map is automatically generated after the scraping and titled "map.html" if there are business entries. The data scraped will have a CSV file name in the f"{search_terms}_{location}_addresses.csv" format. So the above argument will yield a csv file named "Dog Walker_San Francisco, CA_addresses.csv"

If there are no businesses listed for your search terms / location, then the program will throw an error and you'll see: "There were no results from your search. Ending program..."  

The program will also break if you add in any non-standard characters into your search such as:

```bash
python yellowpages_map.py -l "\Dallas\+Texas\\" -s "~B*B~Q~" -p 5
```

So don't do that.

Note that if your location or search terms have spaces, then you must enclose them in quotation marks in order for the program to work:

```bash
python yellowpages_map.py -l "New York, NY" -s "karate studio" -p 10
```
To be on the safe side, you might want to do that anyway.

Enjoy!

## License
[MIT](https://choosealicense.com/licenses/mit/)
