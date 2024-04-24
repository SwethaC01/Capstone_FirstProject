# CAPSTONE_FIRST PROJECT

## Youtube Data Harvesting

Utilizing the YouTube API, the **'YouTube Data Harvesting'** project collects information from YouTube. This is achieved through Python scripting to interact with the YouTube API. The gathered data is then stored in a MySQL database, where tables are created to organize the information effectively. The tables are later joined as needed to generate SQL query outputs. Finally, this data is presented in a Streamlit application for intuitive viewing and analysis.

## **Technologies Used:**

  * Python
  * MySQL
  * Pandas
  * Streamlit

## 📦 Installation

With pip:

```bash
pip install pandas
pip install google-api-python-client
pip install mysql.connector
pip install streamlit
```

### 💻 Import Packages
```python
import streamlit as st
import time
import pandas as pd
from streamlit_option_menu import option_menu
from googleapiclient.discovery import build
import isodate
import mysql.connector
```
