#import library pandas, numpy, beautifulsoup, regex re
import pandas as pd
import numpy as np
import requests
from requests import get
from bs4 import BeautifulSoup
import re

#defining genres list for which movies will be captured
genres = [
    
    "Action",
    "Adventure",
    "Animation",
    "Biography",
    "Comedy",
    "Crime",
    "Drama",
    "Family",
    "Fantasy",
    "Film-Noir",
    "History",
    "Horror",
    "Music",
    "Musical",
    "Mystery",
    "Romance",
    "Sci-Fi",
    "Sport",
    "Thriller",
    "War",
    "Western"
]

#creating genre-url dictionary for accessing each web page
url_dict = {}

for genre in genres:
    url = "https://www.imdb.com/search/title/?genres={}&sort=user_rating,desc&title_type=feature&num_votes=25000,&pf_rd_m=A2FGELUUNOQJNL&pf_rd_p=5aab685f-35eb-40f3-95f7-c53f09d542c3&pf_rd_r=N97GEQS6R7J9EV7V770D&pf_rd_s=right-6&pf_rd_t=15506&pf_rd_i=top&ref_=chttp_gnr_16"
    formated_url = url.format(genre)
    url_dict[genre] = formated_url
    


#creating web scarpper fuction which will route to url and save data for each genre in corresponding file

def scrapper_(url, file_name):    
    
    #step 1 : assign url
    imdb_url=url

    # Step 2: Set headers.
    headers = {"Accept-Language": "en-US, en;q=0.5"}

    # Step 3: Save all values to the results objects coming back from the .get on url
    results = requests.get(imdb_url, headers=headers)

    # Step 4: Parse the results object to movie_soup using the html parser
    movie_soup = BeautifulSoup(results.text, "html.parser")

    # Step 5: extract these attributes (to a list) from the movie_soup, creating empty list for each
    movie_name = []
    movie_years = []
    movie_runtime = []
    imdb_ratings = []
    number_votes = []
    us_gross = []
    description = []
    cast = []
    director = []


    # Step 6: Create a movie_div object to find all div objects in movie_soup
    movie_div = movie_soup.find_all('div', class_='lister-item mode-advanced')

    # Step 7: loop through each object in the movie_div
    for container in movie_div:

        try:
            # Step 8: Add each result from each attribute to list
        
            # name
            name = container.h3.a.text
            movie_name.append(name)

            # year
            year = container.h3.find('span', class_='lister-item-year').text
            movie_years.append(year)

            # runtime
            runtime = container.p.find('span', class_='runtime').text if container.p.find('span', class_='runtime').text else '-'
            movie_runtime.append(runtime)

            # IMDB rating
            imdb = float(container.strong.text)
            imdb_ratings.append(imdb)

            # There are two NV containers, grab both of them as they hold both the votes and the grosses
            nv = container.find_all('span', attrs={'name': 'nv'})

            # movie votes
            vote = nv[0].text
            number_votes.append(vote)

            # filter nv for gross
            grosses = nv[1].text if len(nv) > 1 else '-'
            us_gross.append(grosses)

            #movie description
            desc = container.find_all("p", class_="text-muted")[-1].text.lstrip()
            description.append(desc)

            #movie director/actors
            movieCast = container.find("p", class_="")

            try:
                casts = movieCast.text.replace("\n","").split('|')
                casts = [x.strip() for x in casts]
                casts = [casts[i].replace(j, "") for i,j in enumerate(["Director:", "Stars:"])]
                movieDirector = ', '.join([x.strip() for x in casts[0].replace("Directors:","").split(",")])
                movieStars = ', '.join([x.strip() for x in casts[1].split(",")])
            except:
              casts = movieCast.text.replace("\n","").strip()
              movieDirector = np.nan
              movieStars = ', '.join([x.strip() for x in casts.split(",")])

            cast.append(movieStars)
            director.append(movieDirector)
        
        except IndexError:
            continue


    # Step 9: creating pandas movie dataframe       
    movies = pd.DataFrame({
    'movie_name': movie_name,
    'movie_year': movie_years,
    'movie_runtime': movie_runtime,
    'imdb_ratings': imdb_ratings,
    'number_votes': number_votes,
    'us_gross_millions': us_gross,
    'directors': director,
    'cast':cast,
    'movie_description': description                                             
    })

    # Step 10: Use Pandas str.extract to remove all String characters, and save the value as type int for cleaning up the data with Pandas.
    movies['movie_year'] = movies['movie_year'].astype(str).str.extract('(\d+)').astype(int)
    movies['movie_runtime'] = movies['movie_runtime'].astype(str).str.extract('(\d+)').astype(int)
    movies['number_votes'] = movies['number_votes'].astype(str).str.replace(',', '').astype(int)
    movies['us_gross_millions'] = movies['us_gross_millions'].map(lambda x: x.lstrip('$').rstrip('M'))
    movies['us_gross_millions'] = pd.to_numeric(movies['us_gross_millions'], errors='coerce')
    
    movies=movies.replace(np.nan, '')

    #adding details for html formatting
    movies['movie_name'] =  ['Title : '+x for x in movies['movie_name']]
    movies['movie_year'] = ['Year : '+str(x) for x in movies['movie_year']]
    movies['movie_runtime']= ['Run time : '+str(x) for x in movies['movie_runtime']]
    movies['imdb_ratings'] = ['IMDB rating : '+str(x) for x in movies['imdb_ratings']]
    movies['number_votes'] = ['Votes : '+str(x) for x in movies['number_votes']]
    movies['us_gross_millions'] = ['Revenue USD : '+str(x) for x in movies['us_gross_millions']]
    movies['directors'] = ['Director : '+x for x in movies['directors']]
    movies['cast'] = ['Cast : '+x for x in movies['cast']]
    movies['movie_description'] = ['Summary : '+x for x in movies['movie_description']]

    # Step 11: Export our movie results to corresponding file
    #data files
    movies.to_csv('/content/sample_data/data_files/'+file_name)
    html=movies.to_html(header=False,index=False,justify='left')
    #html files
    html_file = open('/content/sample_data/html_files/'+genre+'.html', "w") 
    html_file.write(html) 
    html_file.close() 

    #creating individual template for each genre page
    #reading generic template
    file_temp = open('/template.html', "r") 
    soup_temp = BeautifulSoup(file_temp, 'html.parser')
    
    #reading genre specific html file
    file_genre = open('/content/sample_data/html_files/'+genre+'.html', "r") 
    soup_genre = BeautifulSoup(file_genre, 'html.parser')
    # all rows
    rows=soup_genre.findChildren(['tr'])
    # append to template object for each row in genre
    for i in rows:
      soup_temp.tbody.append(i) 
    
    #creating final html files for landing pages
    savechanges = soup_temp.prettify("utf-8") 
    html_file = open('/content/sample_data/final_files/'+genre+'.html', "wb") 
    html_file.write(savechanges) 
    html_file.close() 


# for each genre calling the function to scrap data
for genre, url in url_dict.items():
  print(genre)
  scrapper_(url, genre+'.csv')
