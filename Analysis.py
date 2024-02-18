from typing import Any, Optional
import matplotlib.pyplot as plt
import yaml
import requests
import pandas as pd
from io import StringIO
import logging
import os


class Analysis():

    def __init__(self, analysis_config: str) -> None:
        """Initializer for Analysis

        Pass in configuration yml file with details for this specific analysis job. Exception will be raised if cannot find analysis_config file, or config/system_file.yml or config/user_config.yml

        Parameters
        ----------
        analysis_config: str
            Path to yml file containing config for this analysis job
        
        Returns
        -------
        self: Analysis
            Initialized Analysis object with system, user and job config ymls loaded
        
        Examples
        --------
        >>>> Analysis('configs/job_config.yml')
        
        """

        if os.path.isfile(analysis_config) == False:
            logging.error('unable to load analysis_config, cannot proceed with initialization')
            raise Exception('analysis_config file not found')
        elif os.path.isfile('configs/system_config.yml') == False:
            logging.error('unable to load system_config.yml, cannot proceed with initialization')
            raise Exception('configs/system_config.yml not found')
        elif os.path.isfile('configs/user_config.yml') == False:
            logging.error('unable to load user_config.yml, cannot proceed with initialization')
            raise Exception('configs/user_config.yml not found')


        CONFIG_PATHS = ['configs/system_config.yml', 'configs/user_config.yml']

        # add the analysis config to the list of paths to load
        paths = CONFIG_PATHS + [analysis_config]
        logging.debug(paths)

        # initialize empty dictionary to hold the configuration
        config = {}

        # load each config file and update the config dictionary
        for path in paths:
            with open(path, 'r') as f:
                try: 
                    this_config = yaml.safe_load(f)
                    config.update(this_config)
                except Exception as e:
                    logging.error('failed to parse config files, initialization failed')
                    print(e)

        self.config = config
        logging.debug(config)
        logging.info('configs were loaded')

    def load_data(self) -> None:
        """ Loads data specifid in job config into a dataframe

        Loads list of repositories for an org specified in the configuration yml that was passed into this instances initializer. Throws exception if config values missing. Throws exception if loading data fails

        Parameters
        ----------
        None
            
        Returns
        -------
        None
            
        Examples
        --------
        >>>>> Analysis('config.yml').load_data()

        """

        if (self.config["api_base_path"] == None or self.config["endpoint"] == None or self.config["owner"] == None or self.config["resource"] == None):
            logging.error('Missing required configuration values, unable to load data')
            raise Exception('Missing required job configurations, check job configurations')

        requestUrl = f'{self.config["api_base_path"]}/{self.config["endpoint"]}/{self.config["owner"]}/{self.config["resource"]}'
        logging.debug(requestUrl)
        try:
            data = requests.get(url=requestUrl).text
            dataframe = pd.read_json(StringIO(data))
            self.dataset = dataframe
        except Exception as e:
            logging.error('failed to fetch from GitHub API and parse into pandas dataframe')
            raise Exception('Failed to load dataset for analysis, check job config has correct values specified')

    def compute_analysis(self) -> Any:
        """Computes mean # of forks, open issues and watchers across all repos in this github org

        Computes mean number of forks, open issues, and waters for repos in this organization. Data must be loaded first. Throws exception if data hasn't been loaded yet.

        Parameters
        ----------
        None

        Returns
        -------
        analysis_table: DataFrame

        Examples
        --------
        >>>>> Analysis('config.yml').load_data().compute_analysis()
        """

        if hasattr(self, 'dataset') == False:
            logging.error('Unable to compute analysis if data hasn not been loaded yet')
            raise Exception('Data not loaded yet, analaysis cannot be done')
    
        assert hasattr(self, 'dataset')

        return self.dataset[["forks_count", "open_issues_count", "watchers_count"]].mean()

    def plot_data(self, save_path: Optional[str] = None) -> plt.Figure:
        """ Plots engagement metrics vs watcher count for repos in the configured org

        Plots figure and saves to specified save_path location or default save location as per system_config.yml. plot color, title, and x,y axis labels configurable in job config
        Throws exception if data not loaded first
        Throws exception if missing required configurations

        Parameters
        ----------
        save_path: str
            optional param to customize save location.

        Returns
        -------
        figure: plt.Figure
            Figure generated by matplotplib. Saved to either default save location or custom location as a file.
        
        Examples
        --------
        >>>>> Analysis('config.yml').load_data().plot_data()
        """

        if hasattr(self, 'dataset') == False:
            logging.error('Unable to compute analysis if data hasn not been loaded yet')
            raise Exception('Data not loaded yet, analaysis cannot be done')
            
        assert hasattr(self, 'dataset')

        if (self.config["figure_size_x"] == None or self.config["figure_size_y"] == None or self.config["plot_color"] == None or self.config["plot_title"] == None or self.config["plot_x_title"] == None or self.config["plot_y_title"] == None):
            logging.error('Missing required configurations')
            raise Exception('Missing required configurations, check all config files')


        fig, ax = plt.subplots(figsize=(self.config["figure_size_x"], self.config["figure_size_y"]))
        # fig, ax = plt.subplots()

        forks = ax.scatter(self.dataset['watchers_count'], self.dataset['forks_count'], color=self.config["plot_color"])
        issues = ax.scatter(self.dataset['watchers_count'], self.dataset['open_issues_count'])
        ax.set_title(self.config["plot_title"])
        ax.set_ylabel(self.config["plot_y_title"])
        ax.set_xlabel(self.config["plot_x_title"])
        ax.legend([forks, issues], ['Forks', 'Open Issues'])
        ax.grid(0.7)

        default_save_location = self.config["save_path"]


        try: 
            if (save_path == None):
                save_location = default_save_location
            else:
                save_location = save_path

            plt.savefig(save_location)
        except Exception as e:
            print(e)
            logging.error('unable to save scatter plots figure to specified location')
            

        return fig
        

    def notify_done(self, message: str) -> None:
        """ Publishes done message to ntfy.sh

        Publishes done message passed in with message parameter to ntfy.sh at the topic name configured within system_config.yml

        Parameters
        ----------
        message: str
            Message for done notifcation which will be published to ntfy.sh

        Returns
        -------
        None
        
        Examples
        --------
        >>>>> Analysis('config.yml').load_data().notify_done()
        """

        if (self.config["ntfy_topic"] == None):
            logging.error("Missing ntfy.sh topic, cannot publish message")
            raise Exception('Missing ntfy.sh topic, specify it in system_config.yml')

        topic = self.config["ntfy_topic"]
        # print(topic)
        title = 'Ahmad_Hasan_DSI_BRS_Assignment Ntfy'
        # send a message through ntfy.sh
        try: 
            response = requests.post('https://ntfy.sh/' + topic, data=message.encode('utf-8'), headers={'Title': title})
        except Exception as e:
            print(e)
            logging.error('Failed to publish done message to ntfy.sh')
        # print(response)


"""
x = Analysis('configs/job_file.yml')
print(x.config)
x.load_data()
print(x.dataset.shape)
print(x.dataset.columns)
y = x.compute_analysis()
print(type(y))
print(y.size)
print(y)
x.plot_data()
# x.plot_data(save_path="local_file.png")
x.notify_done(message='Hello ntfy')
"""