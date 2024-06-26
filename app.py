import streamlit as st
import os
import openai
from stable import stableai
from newsapi import NewsApiClient
from datetime import date, timedelta
from streamlit_extras.buy_me_a_coffee import button
from fakeyou import FakeYou
import tempfile
from streamlit_extras.streaming_write import write

st.set_page_config(page_icon="📰", page_title="TruthJournal")
fakeyou = FakeYou()
fakeyou.login(os.getenv("FY_USER"), os.getenv("FY_PASS"))

st.markdown(
    """
    <style>
.css-1jc7ptx, .e1ewe7hr3, .viewerBadge_container__1QSob, .styles_viewerBadge__1yB5_, .viewerBadge_link__1S137, .viewerBadge_text__1JaDK{ display: none; } #MainMenu{ visibility: hidden; } footer { visibility: hidden; } 
    </style>
    """,
    unsafe_allow_html=True
)
# Init
newsapi = NewsApiClient(api_key=os.getenv("NEWS_API_KEY"))

all_articles = newsapi.get_everything(q='Trump',
                                      language='en',
                                      from_param= date.today()-timedelta(days = 30),
                                      sources='cnn',
                                      sort_by='publishedAt',
                                      page = 1
                                      )
headlines = {}
radiohead = []

if len(all_articles['articles']) <= 8:
    for i in all_articles['articles']:
        headlines[i['title']] = i['title'] + '. ' + i['description']
        radiohead.append(i['title'])
else:
    for x in all_articles['articles']:
        if ("trump" in x['title'] or "Trump" in x['title'] or "trump" in x['description'] or "Trump" in x['description']) and len(radiohead) < 8:
            headlines[x['title']] = x['title'] + '. ' + x['description']
            radiohead.append(x['title'])

with st.sidebar:
    st.subheader("Top Stories")
    if len(radiohead) > 8:
        choice = st.radio("Dispel the myths:", radiohead[0:7])
    else:
        choice = st.radio("Dispel the myths:", radiohead)
st.title("TruthJournal ✔️")

openai.api_key = os.getenv("OPENAI_API_KEY")
model_id = 'gpt-3.5-turbo'

@st.cache_data
def ChatGPT_conversation(conversation):
    response = openai.chat.completions.create(
        model=model_id,
        messages=conversation
    )
    # api_usage = response['usage']
    # print('Total token consumed: {0}'.format(api_usage['total_tokens']))
    # stop means complete
    # print(response['choices'][0].finish_reason)
    # print(response['choices'][0].index)
    conversation.append({'role': response.choices[0].message.role, 'content': response.choices[0].message.content})
    return conversation
    
"""
Get your un-biased first hand news from TruthJournal! 📰️ 100% fact checked by yours truly, Donald. ✅️
"""

@st.cache_data
def text_to_speech(text):
    tts_result = fakeyou.say(text, "TM:03690khwpsbz")
    return tts_result

def wwts(conversation):
    st.header(choice)
    st.image('https://news.wttw.com/sites/default/files/styles/full/public/article/image-non-gallery/AP19221537019210.jpg')
    prompt = headlines[choice]
    conversation.append({'role': 'user', 'content': prompt})
    st.write('\n')  # add spacing
    if True:
        conversation = ChatGPT_conversation(conversation)
        with st.expander("The Truth", expanded=True):
            output = conversation[-1]['content'].strip()
            tts_holder = st.empty()
            write(output.replace("$", ""))  #output the results
            tts = text_to_speech(output[0:200])
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as fp:
                tts.save(fp.name)
                tts_holder.audio(fp.name, format="audio/wav")
            
if __name__ == '__main__':
    # call main function
    conversation = []
    conversation.append({'role': 'system', 'content': 'I will give you a news article and you will rewrite it in the tone of Donald Trump.'})
    wwts(conversation)
    button(username="digitalmagic", floating=False, width=221)
