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
        fig, ax = plt.subplots(figsize=(self.config["figure_size_x"], self.config["figure_size_y"]))
        # fig, ax = plt.subplots()

        forks = ax.scatter(self.dataset['watchers_count'], self.dataset['forks_count'], color=self.config["plot_color"])
        issues = ax.scatter(self.dataset['watchers_count'], self.dataset['open_issues_count'])
        ax.set_title(self.config["plot_title"])
        ax.set_ylabel(self.config["plot_y_title"])
        ax.set_xlabel(self.config["plot_x_title"])
        ax.legend([forks, issues], ['Forks', 'Open Issues'])
        ax.grid(0.7)


        default_save_location = f'./{self.config["save_path"]}/engagement_scatter.png'
        #print(default_save_location)

        if (save_path == None):
            save_location = default_save_location
        else:
            save_location = save_path

        #print(save_location)

        plt.savefig(save_location)
        return fig
        

    def notify_done(self, message: str) -> None:
        topic = self.config["ntfy_topic"]
        # print(topic)
        title = 'Ahmad_Hasan_DSI_BRS_Assignment Ntfy'
        # send a message through ntfy.sh
        response = requests.post('https://ntfy.sh/' + topic, data=message.encode('utf-8'), headers={'Title': title})
        # print(response)



x = Analysis('configs/job_file.yml')
print(x.config)
x.load_data()
print(x.dataset.shape)
print(x.dataset.columns)
print(x.dataset["forks_count"])
print(x.dataset["open_issues_count"])
print(x.dataset["watchers_count"])
print(x.compute_analysis())
x.plot_data()
x.plot_data(save_path="local_file.png")
x.notify_done(message='Hello ntfy')

