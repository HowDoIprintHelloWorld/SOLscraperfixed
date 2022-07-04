# To anyone reading this who understands my code:
# 1) Please tell me how, I don't get it myself at this point
# 2) This script will only work well at the time of writing. 
#    For example, if more review pages are added, they won't 
#    be taken into consideration by my script.

# !!!!!
# CHANGE THIS ACCORDINGLY!!!
# !!!!!
VADERINSTALLED = False
# !!!!!
# !!!!!

import requests, nltk, time
from deep_translator import GoogleTranslator
from bs4 import BeautifulSoup as bs4
from nltk.sentiment import SentimentIntensityAnalyzer

from progress.bar import Bar
# URL strings because f-strings are annoying to use with this script
URLb = "https://www.trustpilot.com/review/"
URLe = ".ch?languages=al&page="


def scan(numofiters, company):
  ToBretL = []
  printmode = False

  print(f"Scanning {company} public reviews...")
  # The reviews have many pages, so I have to iterate through all of them
  for i in range(1, numofiters):
    # Gets the page content and puts into into the bs4 parser or something
    res = requests.get(URLb+company+URLe+str(i)).text
    soup = bs4(res, "html.parser")

    # Finds all reviews and appends them to a list (Also filters out most unneeded things)
    # Printmode is the filter that says when to append things and when not 
    for review in soup.find_all("p", class_="typography_typography__QgicV"):
      if "Claim your profile" in review.text:
        break
      if "62%" in review.text or "71%" in review.text:
        printmode = True
      if printmode == True and "%" not in review.text:
        ToBretL.append(review.text)
    printmode = True
  return ToBretL

# Uses black magic and a bit of math to figure out if input-text is positive or negative
# Also makes sure that floating point inaccuracy won't mess things up
def analyse(text2analyse, company, sia, score):
  cs = sia.polarity_scores(text2analyse)
  if cs["neg"] == 0 or cs["pos"] - cs["neg"] > 1:
    return abs(cs["compound"])
  else: 
    return -abs(cs["compound"])
  return (cs["compound"]*10000 + score*10000) / 10000

def workon(l, company):
  score = 0
  bar = Bar(f'Processing data for {company}', max=len(l))
  for i in range(len(l)):
    test = trs.translate(l[i])
    score = analyse(test, "coop", SentimentIntensityAnalyzer(), score)
    bar.next()
  bar.finish
  return score

# Checks who is the winner and how popular they are
def getwinner(ms, cs):
  print(f"The results are in! The winner is:")
  if ms > cs:
    print("Migros!")
  else:
    print("Coop!")


if __name__ == "__main__":
  # Installs wordlist 
  then = time.time()
  if not VADERINSTALLED:
    print("Installing Sentiment Analysis wordlist")
    nltk.download("vader_lexicon")

  # Fetches wordlists and prints their length
  coopl, migrosl = scan(8, "coop"), scan(12, "migros")
  print(f"Coop data amount: {len(coopl)}\nMigros data amount: {len(migrosl)}")

  # Makes a google translator object for us to easily use
  # Also prints what it's doing to make my script more complicated than it actually is (and for debugging ;) )
  print("Making translator object...")
  trs = GoogleTranslator(source='auto', target='en')

  print("\n>>>   Running Sentiment Analysis AI on coop...")
  coopscore = workon(coopl, "coop")
  print("\n\n>>>   Running Sentiment Analysis AI on migros...")
  migrosscore = workon(migrosl, "migros")

  # Calculate time taken
  print(f"\nMigros' score: {migrosscore}\nCoops' Score: {coopscore}")
  t = f"{(int(time.time() - then)//60)}:{round(time.time() - then - 60*((time.time() - then)//60), 2)}m"
  print(f"[i]   Finished in {t}")
  getwinner(migrosscore, coopscore)
