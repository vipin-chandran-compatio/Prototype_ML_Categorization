import pandas as pd
import pickle
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction import text
import numpy as np
import configparser
import slack
from slack.errors import SlackApiError
import os.path
#from neomodel import db
import boto3
from py2neo import Graph, Node, Relationship
import settings
import cleanup

def send_message(token, channel, msg, attach_flag, opfile):
    try:
        client = slack.WebClient(token=token)
        client.chat_postMessage(channel=channel, text=msg)
        if attach_flag == "1":
            print("Sending file attachment!")
            with open(opfile, 'rb') as att:
                r = client.api_call("files.upload", files={
                        'file': att,
                    }, data={
                    'channels': channel,
                    'filename': opfile,
                    'title': 'Test Attachment to Slack',
                    'initial_comment': 'Test Attachment description',
                    })
                assert r.status_code == 200

    except SlackApiError as e:
        print(f"Slack integration error: {e.response['error']}")

def send_attach(token, channel, opfile):

    client = slack.WebClient(token=token)

    with open(opfile, 'rb') as att:
        r = client.api_call("files.upload", files={
            'file': att,
        }, data={
            'channels': channel,
            'filename': opfile,
            'title': 'Test Attachment to Slack',
            'initial_comment': 'Test Attachment description',
        })
        assert r.status_code == 200

def load_model(model_file, vector_file): #test

    # model variable refers to the global variable
    with open(model_file, 'rb') as f:
        model = pickle.load(f)
    with open(vector_file, 'rb') as f:
        vec = pickle.load(f)

    return model, vec

def prediction(df, model, vec):
    perf = []
    prob = []
    check = []
    info = []
    df = df.reset_index(drop=True)

    for idx, i in df['Description_Cleaned'].iteritems():
        # print(i)
        #####X6 = vectorizer.transform([i])
        #####y_pred2 = model.predict(X6.toarray())
        X6 = vec.transform([i])
        y_pred2 = model.predict(X6.toarray())
        perf.append(y_pred2[0])
        prob.append(format(np.amax(model.predict_proba(X6.toarray())), 'f'))
        # if y_pred2[0] == df['category'].iat[idx]:
        # check.append("MATCH")
        # else:
        # check.append("MIS-MATCH")

    df['predicted_category'] = perf
    df['probability'] = prob
    #####df['check'] = check

    return df

def ready_data(df):
    print("Readying data - Cleanup and Structuring")
    df['Description_Cleaned'] = cleanup.clean_text(df.Description)
    df = df[~df['Description_Cleaned'].isna()]
    return df

def main():

    #########################################
    try:
        config = configparser.ConfigParser()
        config.read('config.ini')
        output_folder = config['config']['output_folder']
        read_folder = config['config']['read_folder']
        inputfile = config['config']['inputfile']
        modelFolder = config['config']['modelFolder']
        model_pkl_name = config['config']['model_pkl_name']
        vec_pkl_name = config['config']['vec_pkl_name']
        attach_flag = config['config']['attach_flag']
        notify = config['config']['notify']
        slacktoken = settings.slacktoken
        slackchannel = settings.slackchannel

    except Exception as e:
        raise Exception(str(e))
    #########################################

    #vectorizer = CountVectorizer(analyzer='word', ngram_range=(
    #    1, 1), token_pattern=r'\b[a-zA-Z]{2,}\b')
    #input = folder + inputfile
    model_file = modelFolder + model_pkl_name
    vector_file = modelFolder + vec_pkl_name
    if os.path.exists(read_folder + inputfile):
       df_midday_raw = pd.read_csv(read_folder + inputfile)
    else:
        print("Input file does not exist. Exiting!")
        exit(1)

    if (len(df_midday_raw)):
        df_final = ready_data(df_midday_raw)
    else:
        err = "Empty Dataframe(s). Exiting!"
        print(err)
        if notify == "1": send_message(slacktoken, slackchannel, "Error from " + __file__ + "\n" + str(err),"0", output_folder)
        exit(1)

    model, vec = load_model(model_file, vector_file)
    df_res = prediction(df_final, model, vec)

    if len(df_res.index):
        output = output_folder + "\\categorized_" + inputfile
        df_res.to_csv(output, index=False)
        #if notify == "1": send_message(slacktoken, slackchannel, "From " + __file__ + "\n", attach_flag, output)
        print(df_res['predicted_category'])
        print("Done!")
        if notify == "1": send_message(slacktoken,slackchannel,"Test from script: Done!","0", output)
    else:
        err = "Model results are empty. Exiting!"
        print(err)
        if notify == "1": send_message(slacktoken, slackchannel, "Error from " + __file__ + "\n" + str(err),"0", output)
        exit(1)


if __name__ == '__main__':
    main()
