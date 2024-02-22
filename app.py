
# A Flask app that returns a list of words that may be difficult for a learner of a given age and native language.

from flask import Flask, render_template, request

from wordfreq import top_n_list, word_frequency

import string

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/highlight', methods=['POST'])
def highlight():
    # Request form contents
    text = request.form['text']
    lang = request.form['lang']
    age = request.form['age']
    native = request.form.get('native_speaker')
    if native == 'on':
        native = True
    else:
        native = False
    ger_level = request.form['ger_levels']
    # Generate page output
    highlighted_text = generate_word_list(text, lang, age, native, ger_level)
    return render_template('highlight.html', highlighted_text=highlighted_text)

def remove_punctuation(text):
    # Remove punctuation from the text
    translator = str.maketrans('', '', string.punctuation)
    text_no_punctuation = text.translate(translator)
    return text_no_punctuation

def threshold_calculator(lang, age, native, ger_level):
    # Calculate the frequency threshold and if necessary generate an error.
    threshold_number = 0
    error = None
    #GER thresholds from Kusseling 2012.
    if native == False:
        threshold_number = int(ger_level)
    else:
        #English language thresholds from Anglin at al 1993. One SD below the mean for the age given.
        if lang == 'en':
            if (int(age)>4 and int(age)<18):
                threshold_number = 2975*int(age)-15954
            else:
                error = "Results will only be plausible for school age learners. The results are linearly extraoplated from ages 6-11, so take them with a pinch of salt outside that range."
        #German language thresholds from Segbers and Schroeder 2017. One SD below the mean for the age given.
        else:
            if (int(age)>6 and int(age)<25):
                threshold_number = (-54.59*int(age)*int(age)+6033*int(age)-33938)-(-35.8*int(age)*int(age)+1994*int(age)-9059)
            else:
                error = "Die Ergebnisse sind nur für Lernende im Alter von 6-24 Jahren plausibel. Die Ergebnisse werden nach einem Modell von Segbers und Schroeder im Alter von 6,8-22,4 Jahren quadratisch extrapoliert."
        
    return threshold_number, error

def generate_word_list(text, lang, age, native, ger_level):
    # Generate a list of words rarer than the expected vocabulary threshold for a native-speaker learners' 1 SD below the mean at a given age for a given text, language. Else if the speaker is non-native returns a list of possibly unknown words from their GER level.
    # Remove punctuation
    text_no_punctuation = remove_punctuation(text)

    # Split the text into words
    words = text_no_punctuation.split()

    # Make the word list case insensitive
    words_lower = [word.lower() for word in words]

    # Generate a set to get unique words (case insensitive)
    word_set = set(words_lower)

    # Generate list of most common words up to threshold
    if threshold_calculator(lang, age, native, ger_level)[1] != None:
        word_set = threshold_calculator(lang, age, native, ger_level)[1]
    else:
        list_by_rank = top_n_list(lang, threshold_calculator(lang, age, native, ger_level)[0], wordlist='best')
        min_freq = word_frequency(list_by_rank[-1], lang)
        word_set = [word for word in word_set if word_frequency(word, lang)<=min_freq]
        word_set = ', '.join(word_set)
    return word_set

if __name__ == '__main__':
    app.run(debug=True)