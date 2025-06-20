import pandas as pd
import re
import nltk
import matplotlib.pyplot as plt
import seaborn as sns

from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.utils import resample

nltk.download('stopwords')

df = pd.read_csv("amazon_reviews.csv")
df = df[['reviewText', 'overall']].dropna()

def convertRating(score):
    if score <= 2:
        return "Negative"
    elif score in [3, 4]:
        return "Neutral"
    else:
        return "Positive"

df["sentiment"] = df["overall"].apply(convertRating)

customStopwords={"product","amazon","charger","device","adapter","ssd","transferring","tablet","months","message","format"}
stopwords = set(stopwords.words("english")) - {"not", "no", "nor", "don", "didn", "wasn", "isn", "aren"}
stopwords.update(customStopwords)
stemmer=PorterStemmer()
def cleanText(text):
    text = str(text).lower()
    text = re.sub(r"[^a-z\s]", "", text)
    words = text.split()
    stemmed_words = [stemmer.stem(word) for word in words if word not in stopwords]
    return " ".join(stemmed_words)

df["cleaned"] = df["reviewText"].apply(cleanText)

XtrainRaw, XtestRaw, ytrain, ytest = train_test_split(
    df["cleaned"], df["sentiment"], test_size=0.2, stratify=df["sentiment"], random_state=42
)

traindf = pd.DataFrame({"text": XtrainRaw, "label": ytrain})
maxCount = traindf["label"].value_counts().max()

balanceddf = pd.concat([
    resample(traindf[traindf.label == "Positive"], replace=True, n_samples=maxCount, random_state=42),
    resample(traindf[traindf.label == "Neutral"], replace=True, n_samples=maxCount, random_state=42),
    resample(traindf[traindf.label == "Negative"], replace=True, n_samples=maxCount, random_state=42)
]).sample(frac=1, random_state=42)

vectorizer = TfidfVectorizer(ngram_range=(1, 3), max_features=15000)
Xtrain = vectorizer.fit_transform(balanceddf["text"])
Xtest = vectorizer.transform(XtestRaw)

model = LogisticRegression(C=5, class_weight='balanced', solver='liblinear', max_iter=1000)
model.fit(Xtrain, balanceddf["label"])

ypred = model.predict(Xtest)

print("Classification Report:\n")
print(classification_report(ytest, ypred))

plt.figure(figsize=(6, 4))
sns.heatmap(confusion_matrix(ytest, ypred), annot=True, fmt='d',
            cmap='Blues', xticklabels=model.classes_, yticklabels=model.classes_)
plt.xlabel("Predicted")
plt.ylabel("Actual")
plt.title("Confusion Matrix")
plt.tight_layout()
plt.show()

def predictSentiment(text):
    cleaned = cleanText(text)
    vector = vectorizer.transform([cleaned])
    return model.predict(vector)[0]

print("\nSample Predictions:")
samples = [
    "Absolutely loved it!",
    "Terrible experience, not worth it.",
    "Not good at all. I hated it.",
    "Didn't meet expectations.",
    "Very satisfying and exceeded expectations!",
    "good performance, very impressive.",
    "Not worth the money, I'm very disappointed.",
    "Fantastic product and amazing service.",
]

for s in samples:
    print(f"Review: '{s}' → {predictSentiment(s)}")
