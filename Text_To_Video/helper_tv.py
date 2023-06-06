import os
import openai
import requests
import matplotlib.pyplot as plt
from PIL import Image
from io import BytesIO
import itertools
import cv2
import numpy as np
import glob
import os
import azure.cognitiveservices.speech as speechsdk
import pydub
from moviepy.editor import *
from natsort import natsorted
from moviepy.video.fx.resize import resize
import shutil
from pydub import AudioSegment
import re


def load_content(filename):
    with open(filename) as f:
        contents = f.readlines()
    contentstring=' '.join(contents)
    print("content string loaded")
    return contentstring

def text_to_speech(content, SPEECH_KEY, SPEECH_REGION, folder_name,audio_file_name,voice_name,depl_id=""):
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    os.chdir(folder_name)
# This example requires environment variables named "SPEECH_KEY" and "SPEECH_REGION"
    speech_config = speechsdk.SpeechConfig(subscription=SPEECH_KEY, region=SPEECH_REGION)
    audio_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)

    # The language of the voice that speaks.
    #speech_config.speech_synthesis_voice_name='en-US-testcustomnueral'
    if depl_id !="":
        speech_config.endpoint_id = depl_id
    
    speech_config.speech_synthesis_voice_name = voice_name
    speech_config.set_speech_synthesis_output_format(speechsdk.SpeechSynthesisOutputFormat.Audio24Khz160KBitRateMonoMp3)
    audio_config = speechsdk.audio.AudioOutputConfig(filename=audio_file_name)
    speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)

    # Get text from the console and synthesize to the default speaker.
    #print("Enter some text that you want to speak >")
    text = content

    speech_synthesis_result = speech_synthesizer.speak_text_async(text).get()

    if speech_synthesis_result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        print("Speech synthesized for text [{}]".format(text))
    elif speech_synthesis_result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = speech_synthesis_result.cancellation_details
        print("Speech synthesis canceled: {}".format(cancellation_details.reason))
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            if cancellation_details.error_details:
                print("Error details: {}".format(cancellation_details.error_details))
                print("Did you set the speech resource key and region values?")

#loading audio file form our system
def audio_duration(audio_file_name):
    sound = AudioSegment.from_file(audio_file_name, format="mp3")
#duration calculation function
    sound.duration_seconds == (len(sound)/ 1000.0)
    #aud_dur=round((sound.duration_seconds% 60),3)
    print("audio duration calculated")
    return (sound.duration_seconds)

def searchgpt4(contentstring, model="gpt-4"):
    response = openai.ChatCompletion.create(
    engine=model,
    messages = [{"role":"system","content":f"List down top keyphrases which describes the \"Content\" below for doing image search using MS Bing search.\nContent:{contentstring} \n"}],
    temperature=0.34,
    max_tokens=100,
    top_p=0.95,
    frequency_penalty=0,
    presence_penalty=0,
    stop=None)
    searchlist=response.choices[0].message['content'].split('\n')
    print("search list created")
    return searchlist
 
def remove(list):
    pattern = '[0-10]'
    ol = re.compile('[\d][.]')
    #list = [re.sub(pattern, '', i) for i in list]
    list=[ol.sub('', i) for i in list]
    #list= [re.sub('.', '', i) for i in list]
    return list
def bing_search(subscription_key,search_url, search_terms_list,num_images=5):
    contenturls=[]
    headers = {"Ocp-Apim-Subscription-Key" : subscription_key}
    if len(search_terms_list)==0:
        print("No search entities found in the content")
    elif len(search_terms_list)==1:
        try:
            params  = {"q": search_terms_list[0], "license": "public", "imageType": "Photo","safeSearch": "Strict","freshness": "Day"}
            resp = requests.get(search_url, headers=headers, params=params)
            resp.raise_for_status()
            search_results = resp.json()
            c_urls = [img["thumbnailUrl"] for img in search_results["value"][:num_images]]
            contenturls.append(c_urls)
            content_urls=list(itertools.chain(*contenturls))
        except:
            print("Error in Bing search")
    else:
        for ii in search_terms_list:
            try:
                if ii !='':            
                    params  = {"q": ii, "license": "public", "imageType": "Photo","safeSearch": "Strict"}
                    resp = requests.get(search_url, headers=headers, params=params)
                    resp.raise_for_status()
                    search_results = resp.json()
                    c_urls = [img["thumbnailUrl"] for img in search_results["value"][:num_images]]
                        #thumbnail_urls = [img["thumbnailUrl"] for img in search_results["value"][:16]]
                    contenturls.append(c_urls)
            
            except:
                pass  
            content_urls=list(itertools.chain(*contenturls)) 
        print("Bing search completed")          

    return content_urls
def download_images(folder_name,content_urls):   
    
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    for i in range(len(content_urls)):
        try:
            image_data = requests.get(content_urls[i]) 
            image_data.raise_for_status()
            image = Image.open(BytesIO(image_data.content)) 
            image.save(folder_name+"\\"+str(i)+".jpg")
            print(folder_name+"\\"+str(i)+".jpg")            
        except:
            pass
    print("Image saved to folder")

def create_video(folder_name,frameSize,output_video_name, video_duration):
    os.chdir(folder_name)
    gif_name = 'pic'
    fps = 24
    clips=[]
    w=int(frameSize[0])
    h=int(frameSize[1])
    file_list = glob.glob('*.jpg')  # Get all the pngs in the current directory
    #print(len(file_list))
    file_list_sorted = natsorted(file_list,reverse=False)  # Sort the images
    for m in file_list_sorted:
        clips.append(resize(ImageClip(m).set_duration(video_duration),width=w, height=h))
        #resize((1280,720)))
    #clips = [ImageClip(m).set_duration(2)
            #for m in file_list_sorted]

    concat_clip = concatenate_videoclips(clips, method="compose")
    concat_clip.write_videofile(output_video_name, fps=fps)
    print
def audio_video_superimpose(output_video_name, audio_file_name, final_video_name):
    videoclip = VideoFileClip(output_video_name)
    audioclip = AudioFileClip(audio_file_name)#.set_start(0.5).set_end(videoclip.duration)

    new_audioclip = CompositeAudioClip([audioclip.set_start(1)])
    videoclip.audio = new_audioclip
    videoclip.write_videofile(final_video_name)
    print("audio superimposed")
def n_images(audio_file_name, num_search_terms):
    a_dur=audio_duration(audio_file_name)
    #num_search_terms=len(search_terms)
    images=a_dur/2
    num_images=int(round(images/num_search_terms))
    video_duration=a_dur/(num_search_terms*num_images)
    return num_images, video_duration

#contentstring=load_content(text_filepath)
#text_to_speech(contentstring, speech_key, service_region,folder_name,audio_file_name,voice_name,dep_id)
#search_terms=searchgpt4(contentstring)
#search_terms_list=remove(search_terms)
#a_dur=audio_duration(audio_file_name)
#num_search_terms=len(search_terms)
#duration=2
#print(num_search_terms)
#images=a_dur/2
#num_images=round(images/num_search_terms)
#num_images, video_duration= n_images(audio_file_name, len(search_terms_list))
#content_urls=bing_search(subscription_key,search_url, search_terms_list,num_images=num_images)
#download_images(folder_name,content_urls)
#create_video(folder_name,frameSize,output_video_name, video_duration)
#audio_video_superimpose(output_video_name, audio_file_name, final_video_name)
