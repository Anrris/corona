import pandas as pd
from news import *

news = dict()

news[pd.Timestamp(2020, 1, 23)] = dict(body="""
Title: Hubei lockdown<br>
source: https://en.wikipedia.org/wiki/2020_Hubei_lockdowns <br>
""")


news[pd.Timestamp(2020, 2, 21)] = dict(body="""
Italy sees confirmed virus cases more than quadruple<br>
 due to an emerging cluster in the country's north.<br>
""")

news[pd.Timestamp(2020, 2, 27)] = dict(body="""
President Trump declares that a widespread U.S. outbreak of<br>
 the virus is not inevitable, even as top health authorities<br>
  at his side warn Americans that more infections are coming.<br>
source: https://www.nytimes.com/aponline/2020/03/27/us/ap-us-virus-outbreak-chronology.html
""")

news[pd.Timestamp(2020, 3, 4)] = dict(body="""
The Italian government orders all sporting events to<br>
take place without fans until April 3 due to the outbreak.<br>
source: https://www.nytimes.com/aponline/2020/03/27/us/ap-us-virus-outbreak-chronology.html
""")

news[pd.Timestamp(2020, 3, 5)] = dict(body="""
The Senate passes an $8.3 billion measure to provide federal<br>
public health agencies money for vaccines, tests and potential treatments.<br>
source: https://www.nytimes.com/aponline/2020/03/27/us/ap-us-virus-outbreak-chronology.html
""")

news[pd.Timestamp(2020, 3, 8)] = dict(body="""
Italy's prime minister announces a sweeping coronavirus quarantine,<br>
restricting the movements of about a quarter of the country's population<br>
in a bid to limit contagions at the epicenter of Europe's outbreak.<br>
source: https://www.nytimes.com/aponline/2020/03/27/us/ap-us-virus-outbreak-chronology.html
""")

news[pd.Timestamp(2020, 3, 11)] = dict(body="""
The province at the center of China’s virus outbreak begins allowing factories<br>
and some other businesses to reopen in a show of confidence that Beijing is gaining<br>
control over the disease that devastated its economy.<br>
source: https://www.nytimes.com/aponline/2020/03/27/us/ap-us-virus-outbreak-chronology.html
""")

news[pd.Timestamp(2020, 3, 12)] = dict(body="""
The NBA becomes the first major American sports league to suspend play because of the pandemic.<br>
source: https://www.nytimes.com/aponline/2020/03/27/us/ap-us-virus-outbreak-chronology.html
""")


news[pd.Timestamp(2020, 3, 14)] = dict(body="""
Spain locks down its 46 million citizens, and <br>
France orders the closing of just about everything <br>
source: https://www.nytimes.com/aponline/2020/03/27/us/ap-us-virus-outbreak-chronology.html
""")

news[pd.Timestamp(2020, 3, 20)] = dict(body="""
Stocks close out their worst week since 2008 as economic woes<br>
from coronavirus seem sure to deepen; Dow sinks 900 points.<br>
source: https://www.nytimes.com/aponline/2020/03/27/us/ap-us-virus-outbreak-chronology.html
""")

news[pd.Timestamp(2020, 3, 23)] = dict(body="""
British Prime Minster Boris Johnson orders closure of most stores,<br>
bans gatherings for three weeks to stop coronavirus.<br>
source: https://www.nytimes.com/aponline/2020/03/27/us/ap-us-virus-outbreak-chronology.html
""")

news[pd.Timestamp(2020, 3, 24)] = dict(body="""
The International Olympic Committee postpones this summer's Tokyo Games for a year.<br>
source: https://www.nytimes.com/aponline/2020/03/27/us/ap-us-virus-outbreak-chronology.html
""")

news[pd.Timestamp(2020, 3, 27)] = dict(body="""
Trump signs an unprecedented $2.2 trillion economic rescue package<br>
into law after swift and near-unanimous action by Congress to support<br>
businesses, rush resources to overburdened health care providers and help<br>
struggling families during the deepening epidemic.<br>
source: https://www.nytimes.com/aponline/2020/03/27/us/ap-us-virus-outbreak-chronology.html
""")

news[pd.Timestamp(2020, 3, 28)] = dict(body="""
Title: China’s Wuhan — where coronavirus emerged — begins easing lockdown <br>
source: https://nypost.com/2020/03/28/chinas-wuhan-where-coronavirus-emerged-begins-easing-lockdown/ <br>
""")

        

class DailyData(object):
    baseurl = 'https://raw.githubusercontent.com/'\
                'CSSEGISandData/COVID-19/master/'\
                'csse_covid_19_data/csse_covid_19_daily_reports/'

    column_map = {
        'Province/State':'Province_State',
        'Country/Region':'Country_Region',
        'Last Update':'Last_Update'
    }

    date_dict = dict()

    @classmethod
    def get_date(cls, date: pd.Timestamp):
        if date in cls.date_dict:
            return cls.date_dict[date]
        date_csv = f'{date.month:02d}-{date.day:02d}-{date.year:02d}.csv'
        url = cls.baseurl+date_csv
        df = pd.read_csv(url)
        rename_dict = dict()
        for old_column in df.columns:
            if old_column in cls.column_map:
                new_column = cls.column_map[old_column]
                rename_dict[old_column] = new_column
        df = df.rename(columns = rename_dict)
        df.loc[df.Country_Region == "Mainland China", "Country_Region"] = "China"
        df.loc[df.Country_Region == "Korea, South", "Country_Region"] = "South Korea"
        df.loc[df.Country_Region == "Republic of Korea", "Country_Region"] = "South Korea"
        df.loc[df.Country_Region == "Iran (Islamic Republic of)", "Country_Region"] = "Iran"
        df.loc[df.Country_Region == "Taiwan*", "Country_Region"] = "Taiwan"
        cls.date_dict[date] = df
        return cls.date_dict[date]

    @classmethod
    def country(cls, date: pd.Timestamp, indicator: str):
        df = cls.get_date(date)
        countries = df.Country_Region.unique()
        df = pd.DataFrame(
            {
                "Country_Region" : df.Country_Region,
                indicator : df[indicator]
            }
        )
        counts = []
        _countries = []
        for country in countries:
            if pd.isna(country):
                continue
            _countries.append(country)
            count = sum(df[df.Country_Region==country][indicator])
            counts.append(count)

        date_str = f'{date.year}-{date.month:02d}-{date.day:02d}'

        return pd.DataFrame({'country':_countries, date_str:counts})

    @classmethod
    def ranged_country(cls, start: pd.Timestamp, end: pd.Timestamp, indicator):
        dfAll = None
        for date in pd.date_range(start, end):
            df = cls.country(date=date, indicator=indicator)
            if dfAll is None:
                dfAll = df
                continue

            dfAll = dfAll.merge(df, on='country', how='outer')
        dfAll = dfAll.fillna(0).set_index('country')
        dfAll.index.name = None
        dfAll = dfAll.T

        last_date_str = f'{end.year}-{end.month:02d}-{end.day:02d}'
        last = dfAll.loc[last_date_str]
        elements = []
        for col, count in zip(list(last.index), list(last)):
            elements.append((count, col))
        elements.sort(key = lambda x: x[0], reverse=True)

        return dfAll, elements

    @classmethod
    def region(cls, date: pd.Timestamp, country: str, indicator: str):
        df = cls.get_date(date)
        df = df[df.Country_Region == country]
        regions = df.Province_State.unique()
        df = pd.DataFrame(
            {
                "Province_State" : df.Province_State,
                indicator : df[indicator]
            }
        )
        counts = []
        _regions = []
        for reg in regions:
            if pd.isna(reg):
                continue
            _regions.append(reg)
            count = sum(df[df.Province_State==reg][indicator])
            counts.append(count)
        date_str = f'{date.year}-{date.month:02d}-{date.day:02d}'
        return pd.DataFrame({'region':_regions, date_str:counts})

    @classmethod
    def ranged_region(cls, start: pd.Timestamp, end: pd.Timestamp, country: str, indicator):
        dfAll = None
        for date in pd.date_range(start, end):
            df = cls.region(date=date, country=country, indicator=indicator)
            if dfAll is None:
                dfAll = df
                continue

            dfAll = dfAll.merge(df, on='region', how='right')
        dfAll = dfAll.fillna(0).set_index('region')
        dfAll.index.name = None
        dfAll = dfAll.T

        last_date_str = f'{end.year}-{end.month:02d}-{end.day:02d}'
        last = dfAll.loc[last_date_str]
        elements = []
        for col, count in zip(list(last.index), list(last)):
            elements.append((count, col))
        elements.sort(key = lambda x: x[0], reverse=True)

        return dfAll, elements

    @classmethod
    def news_dataframe(cls):


        date = []
        body = []
        for key, item in news.items():
            date.append(key)
            body.append(item['body'])

        df = pd.DataFrame(dict(
            date=date,
            body=body,
        ))
        return df





