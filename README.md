# Expense Tracker

A beginner-friendly Python web app built with Streamlit. Add expenses, view the total, compare spending by category, and download the current list as a CSV file.

## Run it on your computer

1. Install Python from [python.org](https://www.python.org/downloads/) if it is not already installed.
2. Open a terminal in this project folder.
3. Install the required packages:

   ```bash
   pip install -r requirements.txt
   ```

4. Start the app:

   ```bash
   streamlit run app.py
   ```

The app should open in your browser. If it does not, open the local URL shown in the terminal.

## Publish it so people can use it

1. Sign in to GitHub and create a **public** repository, for example `expense-tracker`.
2. Upload `app.py` and `requirements.txt` from this folder to the repository's top level. You can also upload this README.
3. Open [share.streamlit.io](https://share.streamlit.io/) and sign in with GitHub.
4. Choose **Create app**, select your repository and branch, and set the main file path to `app.py`.
5. Deploy the app. When deployment finishes, open the Streamlit app URL to confirm it works, then share that URL on LinkedIn.

## Data and privacy

This demo keeps expenses in the active browser session. They are not permanently saved, and they may disappear when the session ends or the app restarts. Do not enter sensitive financial information. Add a database if you later want persistent storage.
