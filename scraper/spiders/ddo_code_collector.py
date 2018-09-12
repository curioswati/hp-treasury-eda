import csv
import os
from urllib.parse import parse_qs, urlencode

import scrapy

from scraper.settings import PROJECT_PATH


class DDOCodeCollector(scrapy.Spider):
    '''
    Collect DDO Codes for treasuries.
    '''
    name = 'ddo_collector'
    start_urls = ['https://himkosh.nic.in/eHPOLTIS/PublicReports/wfrmDDOAllocationExpenditure.aspx']

    def parse(self, response):
        # create form request that will automatically collect form data from the page response.
        fr = scrapy.FormRequest.from_response(response, callback=self.collect_ddo_code)

        # convert the form body to dictionary
        formdata = parse_qs(fr.body)

        # remove the param that will collect datasets.
        # we are only interested in ddo codes which will get from ajax response.
        formdata.pop(b'ctl00$MainContent$btnGetReport')

        # values collected in the form dictionary are in list form,
        # make them strings.
        formdata = {key: value[0] for key, value in formdata.items()}

        # set the financial year
        formdata.update({b'ctl00$MainContent$ddlFinYr': '2018'})

        # we need ddo codes for all treasuries, so collect treasury codes from dropdown.
        treasuries = response.css('select#ddlTreaCode option')
        for treasury in treasuries[1:]:
            treasury_code = treasury.css('::attr(value)').extract_first()

            # now for every treasury code make the ajax request that'll fetch the ddos.
            formdata[b'ctl00$MainContent$ddlTreaCode'] = treasury_code
            yield fr.replace(body=urlencode(formdata),
                             meta={'treasury': treasury_code})

    def collect_ddo_code(self, response):
        '''
        create a CSV file with DDO names and DDO Codes.
        '''
        ddo_selector = response.css('select#ddlDDOCode option')

        datasets_path = os.path.normpath(os.path.join(PROJECT_PATH, '../datasets'))
        treasury_code = response.meta.get('treasury')
        filepath = os.path.join(datasets_path, '{}_ddo_codes.csv'.format(treasury_code))

        with open(filepath, 'w') as output_file:
            writer = csv.writer(output_file, delimiter=',')
            writer.writerow(['DDO Code', 'DDO Name'])

            for row in ddo_selector[1:]:
                code = row.css('::attr(value)').extract_first()
                name = row.css('::text').extract_first()
                writer.writerow([code, name])
