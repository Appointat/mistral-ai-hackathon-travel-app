# mistral-ai-hackathon-travel-app

## Installation
### Local Hosting
1. Clone the repository, and then navigate to the project directory:
    ```shell
    git clone https://github.com/Appointat/mistral-ai-hackathon-travel-app.git
    cd mistral-ai-hackathon-travel-app/
    ```
2. Create and activate a virtual environment (optional but recommended):
    ```shell
    python -m venv myenvname
    ./myenvname/Scripts/activate # Windows
    source myenvname/bin/activate # MacOS
    ```
3. Install the dependencies: 
    ```shell
    python -m pip install --upgrade pip
    pip uninstall camel-ai  # Make sure you will get the latest version of Camel
    pip install streamlit
    pip install -r requirements.txt
    ```
4. update camel-ai 
    ```shell
    python update-camel-ai.py
    ```
5. Set up the streamlit app:
    ```shell
    streamlit run streamlit_app.py
    ```

6. run learning_by_QA
    ```bash 
    python app.py | tee -a output-20240408-01.log
    ```