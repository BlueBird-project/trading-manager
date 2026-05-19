from ke_client import ki_split_uri, SplitURIBase


@ki_split_uri(uri_template="https://ubflex.bluebird.eu/period_${minutes}")
class DurationURI(SplitURIBase):
    minutes: int
