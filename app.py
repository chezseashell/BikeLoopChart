import pandas as pd
import dash
from dash import dcc, html
import plotly.graph_objects as go
import gpx_utils
from dash.dependencies import Input, Output

# Initialize Dash app
app = dash.Dash(__name__)


# Load POI CSV file
poi_df = pd.read_csv("poi_only.csv") 
poi_df.head()


# Folder where images are stored
image_base_url = "https://raw.githubusercontent.com/chezseashell/BikeLoopChart/refs/heads/main/images/"

# Generate image paths dynamically
poi_df["image_url"] = poi_df["name"].apply(lambda x: f"{image_base_url}poi_{x.replace(' ', '_')}.jpg")

# Load restroom data
restroom_df = pd.read_csv("restrooms.csv")

# Load GPX file & extract track data
lats, lons, elevations, distances = gpx_utils.load_gpx("Manhattan_Loop.gpx")


# Build spatial index for fast searching
track_tree = gpx_utils.build_track_tree(lats, lons)

# Match POIs & restrooms to nearest track points
poi_distances = gpx_utils.match_to_nearest_point(poi_df, track_tree, distances)
restroom_distances = gpx_utils.match_to_nearest_point(restroom_df, track_tree, distances)
poi_names = poi_df["name"].tolist()
poi_images = poi_df["image_url"].tolist()


# Create figure
fig = go.Figure()

# POI Markers
fig.add_trace(go.Scatter(
    x=poi_distances,  
    y=[50] * len(poi_distances),  # Fixed height for POI markers
    mode='markers+text',
    marker=dict(color='#d8da33', size=10),
    text=poi_names,  
    textposition="top center",
    hoverinfo="text",  
    customdata=poi_images  # Store images as custom data
))

# Layout
fig.update_layout(
    title="Manhattan Loop With Elevation & POI", 
    xaxis_title="Distance (km)", 
    yaxis_title="Elevation (m)",
    yaxis=dict(range=[-15, 70]), 
    template="plotly_dark"
)

# Dash Layout
app.layout = html.Div([
    dcc.Graph(
        id="elevation-graph",
        figure=fig,
        style={"width": "80vw", "height": "70vh"}
    ),
    html.Div(
        id="image-display",
        style={"textAlign": "center", "marginTop": "20px"}
    )
])

# Callback to update image display on hover
@app.callback(
    Output("image-display", "children"),
    Input("elevation-graph", "hoverData")
)
def display_hover_image(hoverData):
    if hoverData and "customdata" in hoverData["points"][0]:
        img_url = hoverData["points"][0]["customdata"]
        return html.Img(src=img_url, style={"width": "200px", "borderRadius": "10px"})
    return ""

# Run app
if __name__ == "__main__":
    app.run_server(debug=True)
