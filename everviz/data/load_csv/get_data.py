import pandas as pd
from webviz_config.common_cache import CACHE
from webviz_config.webviz_store import webvizstore


@CACHE.memoize(timeout=CACHE.TIMEOUT)
@webvizstore
def get_data(data_path) -> pd.DataFrame:
    return pd.read_csv(data_path, sep=None, engine="python")
