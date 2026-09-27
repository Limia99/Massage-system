# train_model.py
import sys
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
from sklearn.metrics import classification_report, confusion_matrix
from imblearn.over_sampling import SMOTE
import joblib
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import GridSearchCV

# Set stdout to UTF-8
sys.stdout.reconfigure(encoding='utf-8')

# تحميل البيانات
df = pd.read_csv(r'emergency_message.csv', encoding='utf-8')

# إعداد البيانات
X = df['message']
y = df['category']
print(y.value_counts())
# تشفير التسميات
label_encoder = LabelEncoder()
y_encoded = label_encoder.fit_transform(y)

# تحويل النصوص إلى خصائص باستخدام TF-IDF
vectorizer = TfidfVectorizer(max_features=10000, stop_words=None)

# استخدام SMOTE لتوازن البيانات
smote = SMOTE(random_state=50)
X_tfidf = vectorizer.fit_transform(X)
X_smote, y_smote = smote.fit_resample(X_tfidf, y_encoded)

# تقسيم البيانات
X_train, X_test, y_train, y_test = train_test_split(X_smote, y_smote, test_size=0.25, random_state=50)

# إنشاء نموذج SVM مع تحسينات
param_grid = {
    'C': [0.1, 1.0, 10],
    'kernel': ['linear', 'rbf'],
    'gamma': ['scale', 'auto']
}
grid_search = GridSearchCV(SVC(), param_grid, scoring='f1_macro', cv=3, n_jobs=-1)
grid_search.fit(X_train, y_train)

# أفضل نموذج
best_model = grid_search.best_estimator_

# تقييم النموذج
y_pred = best_model.predict(X_test)
print(classification_report(y_test, y_pred))
print(confusion_matrix(y_test, y_pred))

# حفظ النموذج والمتجهات
joblib.dump(best_model, 'svm_model.pkl')
joblib.dump(vectorizer, 'tfidf_vectorizer.pkl')
joblib.dump(label_encoder, 'label_encoder.pkl')
