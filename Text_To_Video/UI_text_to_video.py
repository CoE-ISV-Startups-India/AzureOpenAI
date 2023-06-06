import os
import openai
import requests
import matplotlib.pyplot as plt
from PIL import Image
from io import BytesIO
import itertools
import os
import cv2
import numpy as np
import glob
import streamlit as st
from PIL import Image
from numpy import asarray
from io import StringIO
import av
import io
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
from helper_tv import *

st.title(""" # TEXT to VIDEO""") 
st.write('This demo uses Azure TTS, Bing Search and Azure OpenAI for creating short video from text provided as a text file')
tab1,tab2=st.tabs(["Credentials","Demo"])
with tab1:
    openai.api_type = st.text_input("openai.api_type: ","azure")
    openai.api_base = st.text_input("openai.api_base: ","https://{}.openai.azure.com/")
    openai.api_version = st.text_input("openai.api_version: ","2023-05-15")
    openai.api_key = st.text_input("openai.api_key: "," ")

    folder_name=st.text_input("path to Folder name: "," ")
    #text_filepath=st.text_input("#### Text file path: ","C:\\Users\\jyravi\\python Codes\\openai-cookbook\\examples\\Covid_precautions.txt")
#speech_key, service_region = "0374199cd3584fb38f2f2252a55ef07a", "eastus"
    speech_key =st.text_input("Azure Speech key: "," ")
    service_region=st.text_input("Azure Speech region: ", " ")
## Bing search credentials ##
    subscription_key = st.text_input("Bing search key: "," ")
    search_url = st.text_input("Bing search url: ","https://api.bing.microsoft.com/v7.0/images/search")

    dep_id=st.text_input("DeploymentId (only if Custom Neural Voice): "," ")
    voice_name=st.text_input("neural voice name: "," ")

    audio_file_name=st.text_input("Audio Filename: "," .mp3")
    #frameSize=st.text_input("Frame size: ","(1280,720)")
    frameSize=(1280,720)
    output_video_name=st.text_input("Output video name: "," .mp4")
#output_video_name="output.mp4"
    final_video_name=st.text_input("Final video name: "," .mp4")
#final_video_name="final.mp4"
#folder_name="C:\\Users\\jyravi\\python Codes\\openai-cookbook\\examples\\covid_precautions3"
#text_filepath="C:\\Users\\jyravi\\python Codes\\openai-cookbook\\examples\\Covid_precautions.txt"

with tab2:
    uploaded_file = st.file_uploader("Choose a file")
    if uploaded_file is not None:
        # To convert to a string based IO:
        stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
        st.write('Uploaded Content is:', stringio)
    # To read file as string:
        string_data = stringio.read()
        if string_data is not None:
            st.write("File uploaded successfully")
        text_to_speech(string_data, speech_key, service_region,folder_name,audio_file_name,voice_name,dep_id)
        st.write("Audio File created")
        search_terms=searchgpt4(string_data)
        search_terms_list=remove(search_terms)
        st.write("Search terms identified")
        num_images, video_duration= n_images(audio_file_name, len(search_terms_list))
        content_urls=bing_search(subscription_key,search_url, search_terms_list,num_images=num_images)
        download_images(folder_name,content_urls)
        create_video(folder_name,frameSize,output_video_name, video_duration)
        audio_video_superimpose(output_video_name, audio_file_name, final_video_name)
        video_file = open(final_video_name, 'rb')
        video_bytes = video_file.read()
        st.video(video_bytes)   

    
