# -*- coding: utf-8 -*-
import csv
import os
import re
from datetime import datetime
from urllib.parse import urlencode

import pandas as pd
import scrapy
from scrapy.spidermiddlewares.httperror import HttpError
from scrapy.exceptions import CloseSpider

from scraper.settings import settings


def clean_text(text):
    return re.sub('\s{2,}', ' ', text).strip()


def make_file_name(attrs):
    filename = '{query}_{treasury}_{ddo}_{date}.csv'.format(**attrs)
    filename = re.sub(r',+', '', filename).replace(' ', '_').replace('/', '_')
    return filename


def get_datasets_path():
    dataset_relative_path = os.path.join(settings.PROJECT_PATH, '../datasets')
    dataset_path = os.path.normpath(dataset_relative_path)
    return dataset_path


def create_date_ranges(begin, stop):
    # create date ranges for 10 years from now.
    start_dates = pd.date_range(begin, stop, freq='MS').strftime('%Y%m%d')
    end_dates = pd.date_range(begin, stop, freq='M').strftime('%Y%m%d')

    if stop not in end_dates:
        end_dates = end_dates.append(pd.Index([stop]))

    return start_dates, end_dates


class DatasetCollector(scrapy.Spider):
    allowed_domains = ['himkosh.hp.nic.in']

    datasets_path = get_datasets_path()

    def parse(self, response):
        '''
        Collect queryable params and make dataset queries.
        '''

        if not hasattr(self, 'begin') and not hasattr(self, 'stop'):
            begin = '20080101'  # by default we collect for past 10 years from 2018.
            stop = datetime.today().strftime('%Y%m%d')
            start_dates, end_dates = create_date_ranges(begin, stop)

        else:
            start_dates, end_dates = create_date_ranges(self.begin, self.stop)

        # collect all treasury names from dropdown.
        treasuries = response.css('#cmbHOD option')

        # collect all query names from dropdown.
        queries = response.css('#ddlQuery option')

        # for each year for each query for each treasury, make requests for datasets.
        for treasury in treasuries[1:]:
            treasury_id = treasury.css('::attr(value)').extract_first()
            treasury_name = treasury.css('::text').extract_first()
            treasury_name = clean_text(treasury_name)

            ddo_file = open(
                os.path.join(self.datasets_path, '{}_ddo_codes.csv'.format(treasury_id))
            )
            ddo_code_reader = csv.reader(ddo_file)

            next(ddo_code_reader)
            for ddo in ddo_code_reader:
                ddo_code = ddo[0]

                for query in queries[1:]:
                    query_id = query.css('::attr(value)').extract_first()
                    query_name = query.css('::text').extract_first()
                    query_name = clean_text(query_name)

                    for start, end in zip(start_dates, end_dates):
                        query_params = {
                            'from_date': start,
                            'To_date': end,
                            'ddlquery': query_id,
                            'HODCode': '{}-{}'.format(treasury_id, ddo_code),
                            'Str': query_name
                        }

                        filename = make_file_name({'query': query_name,
                                                   'treasury': treasury_name,
                                                   'ddo': ddo_code,
                                                   'date': '{}-{}'.format(start, end)})
                        filepath = os.path.join(self.datasets_path, filename)

                        # don't request the same dataset again if it's already collected previously
                        if not os.path.exists(filepath):
                            yield scrapy.Request(
                                self.query_url.format(urlencode(query_params)), self.parse_dataset,
                                errback=self.handle_err, meta={'filepath': filepath}
                            )
            ddo_file.close()

    def handle_err(self, failure):
        if failure.check(HttpError):
            response = failure.value.response
            request = response.request
            self.logger.error('Request: {}'.format(request))
            self.logger.error('Request headers: {}'.format(request.headers))
            self.logger.error('Response headers: {}'.format(response.headers))

    def parse_dataset(self, response):
        '''
        Parse each dataset page to collect the data in a csv file.

        output: a csv file named with query_treasury_year(all lowercase) format.
        '''
        # header row for the file.
        heads = response.css('table tr.popupheadingeKosh td::text').extract()

        # all other rows
        data_rows = response.css('table tr[class*=pope]')

        if not data_rows:
            return

        # prepare file name and its path to write the file.
        filepath = response.meta.get('filepath')

        with open(filepath, 'w') as output_file:
            writer = csv.writer(output_file, delimiter=',')

            # write the header
            writer.writerow(heads)

            # write all other rows
            for row in data_rows:
                cols = row.css('td')
                observation = []
                for col in cols:
                    # since we need consistency in the row length,
                    # we need to extract each cell and set empty string when no data found.
                    # by default scrapy omits the cell if it's empty and it can cause inconsistent row lengths.  # noqa
                    observation.append(col.css('::text').extract_first(' '))
                writer.writerow(observation)


class DatasetCollector2(DatasetCollector):

    def parse(self, response):
        '''
        Collect queryable params and make dataset queries.
        '''

        if not hasattr(self, 'start') and not hasattr(self, 'end'):
            raise CloseSpider('No date range given!')

        # collect last query that gives consolidated data.
        query = response.css('#ddlQuery option')[10]

        query_id = query.css('::attr(value)').extract_first()
        query_name = query.css('::text').extract_first()
        query_name = clean_text(query_name)

        # collect all treasury names from dropdown.
        treasuries = response.css('#cmbHOD option')

        # for each treasury for each ddo, make requests for datasets for the given date range and query.  # noqa
        for treasury in treasuries[1:]:
            treasury_id = treasury.css('::attr(value)').extract_first()
            treasury_name = treasury.css('::text').extract_first()
            treasury_name = clean_text(treasury_name)

            ddo_file = open(
                os.path.join(self.datasets_path, '{}_ddo_codes.csv'.format(treasury_id))
            )
            ddo_code_reader = csv.reader(ddo_file)

            next(ddo_code_reader)
            for ddo in ddo_code_reader:
                ddo_code = ddo[0]

                query_params = {
                    'from_date': self.start,
                    'To_date': self.end,
                    'ddlquery': query_id,
                    'HODCode': '{}-{}'.format(treasury_id, ddo_code),
                    'Str': query_name
                }
                filename = make_file_name({'query': query_name,
                                           'treasury': treasury_name,
                                           'ddo': ddo_code,
                                           'date': '{}-{}'.format(self.start, self.end)})
                filepath = os.path.join(self.datasets_path, filename)

                # don't request the same dataset again if it's already collected previously
                if not os.path.exists(filepath):
                    yield scrapy.Request(
                        self.query_url.format(urlencode(query_params)), self.parse_dataset,
                        errback=self.handle_err, meta={'filepath': filepath}
                    )
            ddo_file.close()


class ExpendituresSpider(DatasetCollector2):
    name = 'expenditures'

    # this page contains all the populating info.
    start_urls = ['https://himkosh.hp.nic.in/treasuryportal/eKosh/ekoshddoquery.asp']

    # dataset is collected from here.
    query_url = 'https://himkosh.hp.nic.in/treasuryportal/eKosh/eKoshDDOPopUp.asp?{}'


class ReceiptsSpider(DatasetCollector):
    name = 'receipts'

    # this page contains all the populating info.
    start_urls = ['https://himkosh.hp.nic.in/treasuryportal/eKosh/eKoshDDOReceiptQuery.asp']

    # dataset is collected from here.
    query_url = 'https://himkosh.hp.nic.in/treasuryportal/eKosh/eKoshDDOReceiptPopUp.asp?{}'
