# Making import
import dash

# Creating app
app = dash.Dash(
    __name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}]
)

# Associating server
server = app.server
app.title = 'COVID - Analyse France'
app.config.suppress_callback_exceptions = True