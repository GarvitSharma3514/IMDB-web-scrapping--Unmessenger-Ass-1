import scrapy
import re
import time
import random
import csv

class ImdbSpider(scrapy.Spider):
    name = 'imdb_spider'

    def save_as_csv(self, filename, data):
        """
        Save a list of dictionaries to a CSV file.
        
        :param filename: The name of the CSV file.
        :param data: A list of dictionaries containing the data to be written.
        """
        if not data:
            print("No data provided")
            return
        
        # Get the list of keys from the first dictionary as the header
        header = data[0].keys()
        
        # Write the data to the CSV file
        with open(filename, mode='w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=header)
            
            # Write the header
            writer.writeheader()
            
            # Write the rows
            for item in data:
                writer.writerow(item)
        
        print(f'Data has been written to {filename}')

    def start_requests(self):
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}
        yield scrapy.Request("https://www.imdb.com/chart/top/?pf_rd_m=A2FGELUUNOQJNL&pf_rd_p=470df400-70d9-4f35-bb05-8646a1195842&pf_rd_r=5V6VAGPEK222QB9E0SZ8&pf_rd_s=right-4&pf_rd_t=15506&pf_rd_i=toptv&ref_=chttvtp_ql_3", headers=headers, callback=self.parse)

    def parse(self, response):
        # iterate movie sections
        movie_data = []
        for movie in response.css(".cli-parent"):
            # movie name
            movie_name = movie.css('h3::text').get()
            # movie year
            movie_year = movie.css('.cli-title-metadata-item:first-child::text').get()
            # movie ratings
            movie_rating = movie.css('.ipc-rating-star--base::text').get()
            # user votings
            user_vote = movie.xpath('.//span[@class="ipc-rating-star--voteCount"]//text()').getall()
            user_vote = user_vote[1].strip('"()')
            self.log(f'Processing: {movie_name}, {movie_year}, {movie_rating}, {user_vote}')
            movie_dict = {
                'movie_name': self.extract_name(movie_name),
                'movie_year': movie_year.strip(),
                'movie_rating': movie_rating,
                'user_votes': user_vote
            }
            self.log(f'Relevant Elements: {movie_dict}')
            movie_data.append(movie_dict)
        print('==========================')
        print(movie_data)
        delay = random.uniform(2, 5)
        self.log(f'Delaying for {delay} seconds.')
        time.sleep(delay)
        self.save_as_csv('output.csv', movie_data)

    def extract_name(self, name):
        name = name.strip()
        name = re.sub(r'^\d+\.\s*', '', name)
        return name