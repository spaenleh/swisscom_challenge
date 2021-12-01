# Swisscom Assignment : Identifying similar geographical zones

## An exploratory data analysis

This repo proposes a solution to identifying similar zones using density data provided by the Swisscom Heatmaps API.

## Required libraries

`python-dotenv`: loading `.env` files for configuration or secrets  
`requests`: for simple get requests  
`oauthlib` and `requests-oauthlib`: for authenticated HTTP requests  
`matplotlib`: for visualization purposes  
`numpy`: for numerical computations and array manipulations  
`pandas`: for data manipulation  
`tslearn`: for TimeSeries manipulation and machine learning


## Structure of the analysis

The [Swisscom Assignment notebook](Swisscom_assignment.ipynb) presents the main data analysis steps :
- Data fetching using the API (tiles and scores)
- Data cleanup (minimal, only removing partial data or duplicates)
- Visualization (using [OpenStreetMap](https://www.openstreetmap.org/))
- Clustering using KMeans on TimeSeries
- Results analysis
