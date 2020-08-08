import Sold_Scraper as ss 
from pandas import read_sql 



cn = ss.cnn(ss.cfg.Azure_DB_CNString)
suburb_detail = read_sql('''select * 
                            from dbo.suburb 
                            where postcode >= '2070' and  postcode <= '2080'
                              ''',cn)

print(suburb_detail)


sd_list = suburb_detail.values.tolist()


for sub in sd_list:
    Postcode = sub[0]
    Suburb = sub[1].replace(' ','-')
    State = sub[2]
    ss.scraper(Suburb,State,Postcode)

