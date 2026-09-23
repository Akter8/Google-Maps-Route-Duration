import pytest
from src.config import ConfigError, load_routes
def test_valid_routes(): assert load_routes('{"routes":[{"id":"R1","origin":"a","destination":"b"}]}')[0].id == "R1"
@pytest.mark.parametrize("raw", ['{}', '{"routes":[]}', '{"routes":[{"id":"X","origin":"a","destination":"b"}]}'])
def test_bad_routes(raw):
    with pytest.raises(ConfigError): load_routes(raw)
