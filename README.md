# playfast
+ Reference
  - https://fastapi.tiangolo.com/ko/ 
+ Environment
  - python 3.11.7 https://docs.python.org/3.11/
  - fastapi 0.108.0 https://pypi.org/project/fastapi/
  - uvicorn 0.25.0 https://pypi.org/project/uvicorn/
  - jinja2 3.1.2 https://pypi.org/project/Jinja2/
  - python-dotenv 1.0.0 https://pypi.org/project/python-dotenv/

## Install FastAPI
+ install packages
  ```
  conda install fastapi
  conda install uvicorn
  ```
+ add **main.py** 
  - https://fastapi.tiangolo.com/#create-it
+ run uvicorn server
  ```
  uvicorn main:app --reload
  ```

## Set Up Portone API
+ Sign up
  - https://admin.portone.io/
+ Add Test Integration 
  - https://admin.portone.io/integration
+ Get Merchant ID & API Keys  
  - https://admin.portone.io/merchant
+ Reference (KR)
  - Official Guide:  https://developers.portone.io/docs/ko/ready/readme?v=v1


## Install Additional packages
+ install additional packages
  ```
  conda install jinja2
  conda install python-dotenv
  conda install httpx
  ```
+ add templates (jinja2)
  - https://fastapi.tiangolo.com/advanced/templates/
+ add .env file to save API keys (dotenv)  
  - https://fastapi.tiangolo.com/advanced/settings/#reading-a-env-file
+ add async API calls (httpx)
  - https://www.python-httpx.org/advanced/ 
