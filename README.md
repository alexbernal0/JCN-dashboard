# JCN Dashboard

A Streamlit dashboard application for the JCN project.

## Overview

This repository contains the code for a Streamlit-based dashboard application. The app is orchestrated and developed using Manus AI.

## Setup

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Installation

1. Clone this repository:
```bash
git clone https://github.com/alexbernal0/JCN-dashboard.git
cd JCN-dashboard
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

### Running the App

To run the Streamlit app locally:

```bash
streamlit run app.py
```

The app will be available at `http://localhost:8501`

## Deployment

This app can be deployed to Streamlit Cloud:

1. Push your code to this GitHub repository
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub account
4. Select this repository and the main app file
5. Deploy!

## Project Structure

```
JCN-dashboard/
├── app.py              # Main Streamlit application
├── requirements.txt    # Python dependencies
├── README.md          # This file
└── data/              # Data files (if needed)
```

## Development

All code development and updates are orchestrated through Manus AI, which handles:
- Code generation and updates
- Git commits and pushes
- Dependency management
- Documentation updates

## License

MIT License
