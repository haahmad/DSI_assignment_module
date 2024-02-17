from typing import Any, Optional
import matplotlib.pyplot as plt
import yaml
import requests
import pandas as pd
from io import StringIO


class Analysis():

    def __init__(self, analysis_config: str) -> None:
        CONFIG_PATHS = ['configs/system_config.yml', 'configs/user_config.yml']

        # add the analysis config to the list of paths to load
        paths = CONFIG_PATHS + [analysis_config]

        # initialize empty dictionary to hold the configuration
        config = {}

        # load each config file and update the config dictionary
        for path in paths:
            with open(path, 'r') as f:
                this_config = yaml.safe_load(f)
            config.update(this_config)

        self.config = config

    def load_data(self) -> None:
        requestUrl = f'{self.config["api_base_path"]}/{self.config["endpoint"]}/{self.config["owner"]}/{self.config["resource"]}'
        data = requests.get(url=requestUrl).text
        dataframe = pd.read_json(StringIO(data))
        self.dataset = dataframe

    def compute_analysis(self) -> Any:
        return self.dataset[["forks_count", "open_issues_count", "watchers_count"]].mean()

    def plot_data(self, save_path: Optional[str] = None) -> plt.Figure:
        pass

    def notify_done(self, message: str) -> None:
        pass


x = Analysis('configs/job_file.yml')
print(x.config)
x.load_data()
print(x.dataset.shape)
print(x.dataset.columns)
print(x.dataset["forks_count"])
print(x.dataset["open_issues_count"])
print(x.dataset["watchers_count"])
print(x.compute_analysis())

