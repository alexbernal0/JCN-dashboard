# JCN Dashboard - Development Guide

## Repository Information

- **Repository**: https://github.com/alexbernal0/JCN-dashboard
- **Local Path**: `/home/ubuntu/JCN-dashboard`
- **Main Branch**: master

## Working with Manus AI

This project is set up to be developed with Manus AI as your orchestrator. Here's how to work effectively:

### Making Changes

When you want to add features or make changes to your Streamlit app:

1. **Describe what you want**: Tell Manus what feature or change you need
2. **Manus will**:
   - Write or modify the necessary code
   - Test the changes if needed
   - Commit the changes to git
   - Push to GitHub automatically

### Example Requests

Here are some examples of what you can ask Manus to do:

- "Add a file upload feature to load CSV data"
- "Create a new page for user analytics"
- "Add a sidebar filter for date ranges"
- "Integrate with an API to fetch real-time data"
- "Add authentication to the dashboard"
- "Create interactive charts using Plotly"
- "Add data export functionality"

### Git Workflow

Manus will handle all git operations for you:
- Creating commits with descriptive messages
- Pushing changes to GitHub
- Managing branches if needed

### Testing Locally

To test your Streamlit app locally in the Manus environment:

```bash
cd /home/ubuntu/JCN-dashboard
streamlit run app.py
```

Manus can run this for you and expose the app for testing.

### Deploying to Streamlit Cloud

Once your code is pushed to GitHub, you can deploy to Streamlit Cloud:

1. Go to https://share.streamlit.io
2. Sign in with your GitHub account
3. Click "New app"
4. Select:
   - Repository: `alexbernal0/JCN-dashboard`
   - Branch: `master`
   - Main file path: `app.py`
5. Click "Deploy"

Your app will be live at a URL like: `https://your-app-name.streamlit.app`

## Project Structure

```
JCN-dashboard/
├── app.py                    # Main Streamlit application
├── requirements.txt          # Python dependencies
├── README.md                # Project overview
├── DEVELOPMENT_GUIDE.md     # This file
├── .gitignore               # Git ignore rules
└── data/                    # Data files (create as needed)
```

## Common Streamlit Patterns

### Adding New Pages

For multi-page apps, create a `pages/` directory:

```
JCN-dashboard/
├── app.py
└── pages/
    ├── 1_📊_Analytics.py
    ├── 2_📈_Reports.py
    └── 3_⚙️_Settings.py
```

### Using Session State

Store data across reruns:

```python
if 'counter' not in st.session_state:
    st.session_state.counter = 0

st.session_state.counter += 1
```

### Caching Data

Cache expensive computations:

```python
@st.cache_data
def load_data():
    return pd.read_csv('data.csv')
```

## Tips for Working with Manus

1. **Be specific**: The more details you provide, the better Manus can help
2. **Iterate**: Start with basic features and add complexity gradually
3. **Test frequently**: Ask Manus to run the app after significant changes
4. **Ask questions**: If you're unsure about something, just ask!

## Next Steps

Ready to build your dashboard? Tell Manus what features you want to add!

Some ideas to get started:
- Connect to your data source (CSV, database, API)
- Add specific visualizations for your use case
- Implement filters and controls
- Create multiple pages for different views
- Add export/download functionality
