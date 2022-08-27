
# Book Recommendation system

[View the notebook in kaggle](https://www.kaggle.com/code/prathamsaraf1389/book-recommender-using-unsupervised-learning-eda)

This is a book recommender system which uses the unsupervised learning algorithm - Nearest Neighnours to predict next book to read

---

## Deploying it locally

Steps to run it locally

1. git clone the repository
```bash
https://github.com/pratham-saraf/book-recommender.git
```
2. Download the [Data Files](https://iiitbhopal1-my.sharepoint.com/:f:/g/personal/21u02027_iiitbhopal_ac_in/Eq7UQNo74d5EgyvFuMjnCM4B-OsCW_Fnh53wvcYxL6eBtQ?e=D2jDkQ) 
3. Move the downloaded Data files inside ```data``` folder which should be created inside ```model``` folder
4. Folder structure would look like 
```
.
├── app.py
├── model
│   ├── data
│   │   ├── book_id_map.csv
│   │   ├── recommedation_model.sav
│   │   ├── search_final.json
│   │   └── sparse_matrix.npz
│   ├── recommender.py
│   └── search.py
├── README.md
├── requirements.txt
├── run
├── static
│   ├── dashboard.js
│   ├── find.css
│   ├── find.js
│   ├── images
│   │   ├── dislike.svg
│   │   └── like.svg
│   ├── nav.css
│   ├── recommendation.js
│   ├── signin.css
│   └── starter-template.css
└── templates
    ├── dashboard.html
    ├── find.html
    ├── index.html
    ├── layout.html
    ├── login.html
    ├── recommend.html
    └── signup.html
```
5. Run the command to create the virtual env and source it
```bash
cd book-recommender
python3 -m venv env
source env/bin/activate
```


6. To install the python dependencies 
```bash
pip install -r requirements.txt
``` 
7. Create a .env file which contains
```
SECRET_KEY="A random password string for the flask"
MONGO_DB = "Mongo-DB-connection-URI"
```
8. The mongodb cluster should have two collections named
```
└── Cluster
    ├── user-book-data
    └── users

```
9. Give run permissions to the run file and execute it 
```bash
chmod +x run
./run
```
---
