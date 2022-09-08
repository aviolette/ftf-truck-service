from src.locations import AWSLocationService
from src.models import Location


class MockLocationClient:
    def __init__(self, response):
        self.response = response

    def search_place_index_for_text(self, *args, **kwargs):
        return self.response


def test_aws_find_locations():
    client = MockLocationClient({'ResponseMetadata': {
        'RequestId': '3c1b7d9c-54e9-48c2-8789-12cdd2cabc0a', 'HTTPStatusCode': 200,
        'HTTPHeaders': {'date': 'Wed, 07 Sep 2022 00:35:56 GMT', 'content-type': 'application/json',
                        'content-length': '967', 'connection': 'keep-alive',
                        'x-amzn-requestid': '3c1b7d9c-54e9-48c2-8789-12cdd2cabc0a',
                        'access-control-allow-origin': '*', 'x-amz-apigw-id': 'YEEY_GY3oAMFULg=',
                        'access-control-expose-headers': 'x-amzn-errortype,x-amzn-requestid,x-amzn-errormessage,x-amzn-trace-id,x-amz-apigw-id,date',
                        'x-amzn-trace-id': 'Root=1-6317e76b-1dfa8bf806ed88d711dbf5f7'},
        'RetryAttempts': 0}, 'Results': [{'Distance': 559.3204248455561,
                                          'Place': {'AddressNumber': '5000', 'Country': 'USA',
                                                    'Geometry': {'Point': [-86.4321030110779,
                                                                           36.57200853223046]},
                                                    'Interpolated': True,
                                                    'Label': '5000 California Ave, Nashville, TN, 37209, USA',
                                                    'Municipality': 'Nashville',
                                                    'PostalCode': '37209 1414',
                                                    'Region': 'Tennessee',
                                                    'Street': 'California Ave',
                                                    'SubRegion': 'Davidson County'},
                                          'Relevance': 1}, {'Distance': 600.2345156676731,
                                                            'Place': {'AddressNumber': '5000',
                                                                      'Country': 'USA',
                                                                      'Geometry': {'Point': [
                                                                          -86.4321030110779,
                                                                          36.57200853223046]},
                                                                      'Interpolated': False,
                                                                      'Label': '5000 California Ave, Nashville, TN, 37209, USA',
                                                                      'Municipality': 'Nashville',
                                                                      'PostalCode': '37209 1414',
                                                                      'Region': 'Tennessee',
                                                                      'Street': 'California Ave',
                                                                      'SubRegion': 'Davidson County'},
                                                            'Relevance': 0.9919}],
        'Summary': {'BiasPosition': [-86.851584, 36.1674633],
                    'DataSource': 'Esri', 'MaxResults': 50,
                    'ResultBBox': [-86.85647102392115, 36.163788012305176,
                                   -86.8561030110779, 36.16400853223046],
                    'Text': '5607A California Avenue, Nashville, TN'}})
    service = AWSLocationService("foo", client)

    location = service.find_location("bazbar", Location(name="bar", latitude=3, longitude=4))

    assert location.is_valid()
    assert location.name == 'bazbar'
    assert location.latitude == 36.57200853223046
    assert location.longitude == -86.4321030110779
