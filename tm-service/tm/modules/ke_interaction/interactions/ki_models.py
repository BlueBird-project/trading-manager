from ke_client import ki_split_uri, SplitURIBase
from rdflib import URIRef

# TODO: move to ke-client
UBFLEX_MARKET_BASE = "https://ubflex.bluebird.eu/market/"
SAREF4ENER_TIMESERIES = URIRef("TimeSeries", base="https://saref.etsi.org/saref4ener/")
UBMARKET_FORECAST = URIRef("Forecast", base=UBFLEX_MARKET_BASE)


@ki_split_uri(uri_template="https://ubflex.bluebird.eu/period_${minutes}")
class DurationURI(SplitURIBase):
    minutes: int
