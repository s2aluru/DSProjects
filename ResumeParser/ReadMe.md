Created a resume parser using Spacy NER, OCR in Visual Studio Code IDE. Developed multile Python modules to convert data into Spacy format, extract entities and train NER model, performed OCR on a resume PDF and predicted entities. Following is the purpose of each python file.

json_spacy.py - Converts resume data into Spacy required format
train_model.py - Build Spacy model to extract entities 
predict_model.py - Predict entities
text_extractor.py - Use TIKA OCR to extract text from PDF
utils.py - Common functions used in the project
engine.py - Calls all the individual modules for learning model and prediction.

