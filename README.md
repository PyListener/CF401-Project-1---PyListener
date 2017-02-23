# PyListener

PyListener is an application written on the Python Pyramid framework, designed to assist people with apraxia communicate with loved-ones and caretakers using a series of pictograms translated to text and shareable via email or sms.

The purpose of this project was to create a visual communication tool in the form of a web-based app intended for use on mobile platforms to assist users with communication disabilities.
Instances include users with a communication disability such as Apraxia, a motor disorder in which the patient is unable to perform certain tasks or movements despite full understanding and willingness. In [Apraxia of speech](https://en.wikipedia.org/wiki/Apraxia_of_speech), patients have difficulty conveying ideas and thoughts from the brain to the spoken words. Apraxia of speech can manifest itself after incidents such as a stroke or trauma or be present in early infancy (Childhood Apraxia of Speech).


# How it works

A caregiver can register with a username, password, email, phone number and a profile picture. The caregiver is also prompted to enter the user's name.
Once registered, the caregiver becomes the primary contact for the user and a pictogram is created in the address book.

The account is immediately logged in and taken to the configuration page.
There, the caregiver can add or delete pictograms for contacts, categories and/or attributes. Fill the form with an image file, label, description (which will be used to build the sentence) and upload your customized pictogram.
Once done, simply click on the home button and you are ready to go!

The app comes with pre-loaded pictograms so any user can create an account and start building sentences right away.

The first screen for the user is the Address Book. There, the user can pick whom they wish to talk to. Once selected, it takes you to the second screen: Categories. There, the user can select the subject of the sentence. Which takes you to the third screen: Attributes. Attributes are always related to the category selected.

Once the sentence fully built, the user is taken to the fourth and final screen: Display.
The sentence will be, indeed, displayed and the user is offered three choices:
Send an SMS, send an Email or start over.

If the user picks SMS or Email, a message will immediately be sent to the contact selected at the begining of the sentence. If the user chooses to start over, they will be taken back to the first screen and can pick a new contact to talk to.

# How we built it

PyListener was created during our Code Fellows advanced python development midterm project by Ted Callahan, Maelle Vance and Rick Valenzuela. We had four days total to build the full application.

We chose the Pyramid framework for its robustness. We are currently looking to rebuild the application using Django as we have plan to expand.

We used Postgresql and sqlalchemy to build our database. The main challenge was to build all the relational databases as well as handling image uploads by users.

To send sms and emails, we used two external apis: [Twilio](https://github.com/twilio/twilio-python) and [Yagmail](https://github.com/kootenpv/yagmail). We are very thankful for their extensive documentation!

We deployed on Heroku: (http://pylistener.herokuapp.com/)

# How to run it yourself

Clone this repository into whatever directory you want to work from.

```bash
$ git clone https://github.com/PyListener/CF401-Project-1---PyListener.git
```

Assuming that you have access to Python 3 at the system level, start up a new virtual environment.

```bash
$ cd CF401-Project-1---PyListener
$ python3 -m venv venv
```

Open `venv/bin/activate` in your editor and pass your own environment variable as following :
- export DATABASE_URL= *your chosen database*
- export TEST_DB= *your test database*
- export EMAIL= *the gmail account you want to user to send emails from the app.*
- export PASSWORD= *your gmail password*
- export TWILIO_SID= *the twilio account sid you want to use to send emails from the app.*
- export TWILIO_TOKEN= *your twilio token*
- export TWILIO_NUMBER= *your twilio number in the following format: "+12345678910"*

Then activate your environment:

```bash
$ source venv/bin/activate
```

Once your environment has been activated, make sure to install the requirements:

```bash
(venv) $ pip install -e .
```

You are then ready to initialize your database and run the app!

```bash
$ initialize_db development.ini
$ pserve development.ini
```

# Special Thanks:

[Nicholas Hunt-Walker](https://github.com/nhuntwalker/)  
[Twilio](https://github.com/twilio/twilio-python)  
[Yagmail](https://github.com/kootenpv/yagmail)  
And Maelle's son Charlie who suffers from Apraxia
