import Analysis
import pandas
import matplotlib.pyplot as plt
import os
from pytest import raises

#assert that Analysis initializer correctly parses configs if config files are present
def testAnalysisInitializer():
    analysis = Analysis.Analysis('configs/job_file.yml')
    assert hasattr(analysis, 'config')


# test that analysis initialzier raises exceptions when initialized incorrectly
def testAnalysisInitializerRaises():
    with raises(Exception):
        analysis = Analysis.Analysis('')
    with raises(Exception):
        analysis = Analysis.Analysis('does-not-exists.yml')

#assert that Analysis load_data function can fetch and parse GitHub API data
def testAnalysisLoadData():
    analysis = Analysis.Analysis('configs/job_file.yml')
    analysis.load_data()
    assert hasattr(analysis, 'dataset')

#assert that Analysis load_data function can fetch and parse GitHub API data
def testAnalysisComputeAnalysis():
    analysis = Analysis.Analysis('configs/job_file.yml')
    analysis.load_data()
    analysisResults = analysis.compute_analysis()
    assert type(analysisResults) == pandas.Series
    assert analysisResults.size == 3

# assert that Analysis plot_data returns a figure and saves to default output path
def testAnalysisPlotData():
    analysis = Analysis.Analysis('configs/job_file.yml')
    analysis.load_data()
    figure = analysis.plot_data()
    assert type(figure) == plt.Figure
    assert os.path.isfile('output_figures/engagement_scatter_plots.png')