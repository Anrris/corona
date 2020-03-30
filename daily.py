import pandas as pd

class DailyData(object):
    baseurl = 'https://raw.githubusercontent.com/'\
                'CSSEGISandData/COVID-19/master/'\
                'csse_covid_19_data/csse_covid_19_daily_reports/'

    dates_csv = [
        '01-22-2020.csv',
        '01-23-2020.csv',
    ]

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
        cls.date_dict[date] = df
        return cls.date_dict[date]

    @classmethod
    def country(cls, date: pd.Timestamp, country: str):
        df = cls.get_date(date)
        return df[df.Country_Region == country]

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





