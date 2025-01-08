import streamlit as st
from dotenv import load_dotenv
import os

db_url = st.secrets["database"]["DB_URL"]
db_name = st.secrets["database"]["DB_NAME"]
admin_collection = st.secrets["database"]["DB_ADMIN"]
user_collection = st.secrets["database"]["DB_USER"]

def main():
    
    st.write("# Welcome to NutriScanAI! 🙋‍♂️")
    st.markdown("""
NutriScanAI is your go-to platform for evaluating the ingredients in your daily packaged food items 🧃.
We aim to provide you with insights into the hazardous nature of the ingredients used, as well as the associated allergies, to keep you informed, safe, and healthy. 🍏
### How We Categorize Ingredients 🗒️:
Our AI model scans the ingredients list of your product and classifies them into **4 categories** (from Type 0 to Type 3), based on their impact on human health:
- **Type 0**: Fully safe to consume ✅
- **Type 1**: Minor or moderate health impact ⚠️
- **Type 2**: Contains ingredients that may be harmful or cause mild side effects ❌
- **Type 3**: Highly hazardous ingredients, should be avoided at all costs 🚨
In addition, our AI model also checks whether any of the ingredients may cause allergic reactions based on your personal preferences and medical history.
### How It Works 🤔:
Using NutriScanAI is simple and intuitive! Here's how you can get started:
1. **User Info**: Go to the *User Section* in the sidebar, then enter your name, gender, and state. 
2. **Allergy Information**: Next, let us know if you have any allergies so we can tailor the analysis.
3. **Scan the Ingredients**: You can either take a new photo or upload a picture of the ingredients list from your gallery. 📸
   - Ensure that the ingredients section is clear, well-lit, and in frame.
4. **Get Results**: In a few seconds, NutriScanAI will analyze the ingredients and categorize them according to their health impact. If any ingredient poses an allergy risk to you, we will display that information. ⚡
### What We Provide:
- Real-time analysis of food ingredients 🌱
- Risk classification for each ingredient based on health impact 🧠
- Allergy alerts tailored to your personal profile 🤧
With NutriScanAI, making healthier food choices has never been easier! 🌟
""")
    
if __name__ == "__main__":
    main()