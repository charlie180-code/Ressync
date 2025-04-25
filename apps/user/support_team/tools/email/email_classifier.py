import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout

emails = [
    "Hello, this is a legitimate email.",
    "Get your free coupons now!",
    "Meeting scheduled for tomorrow.",
    "Limited time offer, buy now!",
    "Confirm your account details."
]

labels = [0, 1, 0, 1, 0]  

vectorizer = TfidfVectorizer(max_features=1000)
X = vectorizer.fit_transform(emails).toarray()
y = np.array(labels)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = Sequential([
    Dense(512, input_dim=X.shape[1], activation='relu'),
    Dropout(0.5),
    Dense(256, activation='relu'),
    Dropout(0.5),
    Dense(1, activation='sigmoid')
])

model.compile(
    optimizer='adam', 
    loss='binary_crossentropy', 
    metrics=['accuracy']
)

model.fit(X_train, y_train, epochs=10, batch_size=32, validation_data=(X_test, y_test))

loss, accuracy = model.evaluate(X_test, y_test)
print(f"Accuracy: {accuracy * 100:.2f}%")

new_emails = ["You won a prize!", "Please confirm your email address."]
X_new = vectorizer.transform(new_emails).toarray()
predictions = model.predict(X_new)
for i, email in enumerate(new_emails):
    label = "Spam" if predictions[i] > 0.5 else "Not Spam"
    print(f"Email: {email}\nPrediction: {label}\n")
