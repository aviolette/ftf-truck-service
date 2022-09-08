from src.models import Location


class LocationService:
    def find_location(self, name: str, bias_location: Location) -> Location:
        pass


class AWSLocationService(LocationService):
    def __init__(self, index_name: str, client):
        self.index_name = index_name
        self.client = client

    def find_location(self, name: str, bias_location: Location) -> Location:
        results = self.client.search_place_index_for_text(
            BiasPosition=bias_location.lnglat(), IndexName=self.index_name, Text=name)
        if len(results['Results']):
            result = results['Results'][0]['Place']
            return Location(name=name, latitude=result['Geometry']['Point'][1],
                            longitude=result['Geometry']['Point'][0])
        return Location(name=name, valid=False)


class CacheAndForwardService(LocationService):
    def __init__(self, location_service: LocationService):
        self.location_service = location_service

    def find_location(self, name: str, bias_location: Location) -> Location:
        # TODO: Implement caching
        return self.location_service.find_location(name, bias_location)
