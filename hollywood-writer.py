import os
import time
from PIL import Image
import copy

import requests
import streamlit as st
# from dotenv import load_dotenv

# load_dotenv()
API_KEY = os.getenv('API_KEY')

st.title('🍌 Script Monkey 🐒')
st.markdown("Made With ❤️ By [jaredthecoder](https://www.youtube.com/@jaredthecoder)")

body_message = st.empty()

body_message.markdown("""
    ### This is Script Monkey: Your Personal Hollywood Screenwriter
    First create your characters / genre / setting and at a click of a button generate your story.
    """)
body_actions = st.container()
body_container = st.empty()

st.session_state.screenplay = None
# with open('test_outline.txt', "r+") as f:
#     text = f.read()
#     print(text)
st.session_state.character_loading = False
st.session_state.current_character_art = False
st.session_state.current_character_name = None
st.session_state.current_character_bio = None
st.session_state.current_character_art = None

st.session_state.title = None
st.session_state.genre = None
st.session_state.setting = None

def request_screenplay_page(screenplay_body_container, screenplay_body_message):
    print("Next page")
    url = f"https://api.runpod.ai/v2/llama2-7b-chat/runsync"

    headers = {
      "Authorization": API_KEY,
      "Content-Type": "application/json"
    }

    last_page = None
    if 'screenplay' in st.session_state and st.session_state.screenplay and len(st.session_state.screenplay) > 0:
        last_page = st.session_state.screenplay.split(" ")[-500:]
        last_page = " ".join(last_page)

    prev_page_addition = f"""
        Here is the last written page of this screenplay, your job is to write the next page of the screenplay

        Last page of the screen play
        ...{last_page}...

        Remember if the last page ends in the middle of a sentence, start your response finishing that sentence.

        Now using the given story outline and the previous written page, write the next page for this screenplay and use the story outline to first see where you are in the overall story. Analyze the story outline before generating the next page. See where which part of the hero's journey you're currently in before responding.

        If you cover an entire story point in the outline, simply go to the next one. If you have reached the COMPLETE end of the story outline then finish with the tag "SCRIPT STORY END". If the story outline isn't completely finalized in your story, simply stop at the end of the current scene with the tag "SCRIPT MONKEY CONTINUE".

        Only respond with the screenplay do not respond with any explanation or affirmative just the continuing screenplay
    """.strip()

    initial_page_addition = """
        Now using this story outline write the first page for a screenplay for this story outline. If you cover an entire story point in the outline, simply go to the next one.
    """.strip()
    prompt = f"""
        Write me a well structured screenplay (use two or three new line characters in between dialogue exchanges and at the end of a scene) with scene descriptions and character dialogue for the following story outline. The story outline is broken down in Joseph Campbell's Hero's Journey story structure.

        Here is the story outline:
        {st.session_state['story_outline']}

        {prev_page_addition if last_page else initial_page_addition}
    """.strip()

    payload = {
      "input": {
        "prompt": prompt,
        "sampling_params": {
          "max_tokens": 2000,
          "n": 1,
          "frequency_penalty": 0.1,
          "temperature": 0.75,
        }
      }
    }

    start_time = time.time()
    response = requests.post(url, headers=headers, json=payload)
    print(response.text)



    if 'screenplay' in st.session_state and st.session_state.screenplay and len(st.session_state.screenplay) > 0:
        output = st.session_state.screenplay
    else:
        output = ""

    response_json = response.json()
    if response_json["status"] == "COMPLETED":
        output += "".join(response_json["output"]["text"])
        screenplay_body_container.text("\n".join(output.split("\n")))
        return output

    status_url = f"https://api.runpod.ai/v2/llama2-7b-chat/stream/{response_json['id']}"

    while True:
        time.sleep(.5)
        try:
            get_status = requests.get(status_url, headers=headers)
            get_status_json = get_status.json()
            if "stream" in get_status_json:
                for stream in get_status_json["stream"]:
                    next_tokens = "".join(stream["output"]["text"])
                    output += next_tokens
                    screenplay_body_container.text("\n".join(output.split("\n")))
                    print(next_tokens)
            
            if get_status_json["status"] == "IN_PROGRESS":
                continue
            else:
                end_time = time.time()
                print("Text generation time:", (end_time - start_time)/60)
                screenplay_body_message.markdown("## Screenplay is generating...")
                return output

        except Exception as e:
            print(str(e))
            return ""


def request_story_outline(title, genre, setting, characters):
    url = f"https://api.runpod.ai/v2/llama2-7b-chat/runsync"

    headers = {
      "Authorization": API_KEY,
      "Content-Type": "application/json"
    }
    character_descriptions = ""

    for i, character in enumerate(characters):
        character_descriptions += f"""
            Character #{i+1} name: {character['name']}
            Character #{i+1} bio: {character['bio']}
            \n""".strip()

    prompt = f"""
        Write me an story outline with the following format/info from beginning to end
        
        Your story MUST include these characters described below
        {character_descriptions}
        \n
        Your story MUST be this genre: {genre}

        Your story MUST be in this setting: {setting}

        Your story MUST titled: "{title}"

        Your story outline must also be structured using Joseph Campbell's Hero's Journey outline to write the story. Write out the general plot first and then once you write the plot, write out each story point.

        Each story point should be no more than 3 sentences that describe what happens in general at this part of the story

        Here are the story points in order that you MUST format your story outline in
        1) The Call to Adventure
        2) Refusal of the Call
        3) Supernatural Aid
        4) The Crossing of the First Threshold
        5) Belly of the Whale
        6) The Road of Trials
        7) The Meeting with the Goddess
        8) Woman as the Temptress
        9) Atonement with the Father
        10) Apotheosis
        11) The Ultimate Boon
        12) Refusal of the Return
        13) The Magic Flight
        14) Rescue from Without
        15) The Crossing of the Return Threshold
        16) Master of the Two Worlds
        17) Freedom to Live

        Remember each of these story points are metaphorical in name, utilize the MEANING of the story point when writing out your story point.

        Finally, when you write this story outline make the story captivating and exciting.
    """.strip()

    payload = {
      "input": {
        "prompt": prompt,
        "sampling_params": {
          "max_tokens": 2000,
          "n": 1,
          "frequency_penalty": 0.1,
          "temperature": 0.75,
        }
      }
    }

    start_time = time.time()
    response = requests.post(url, headers=headers, json=payload)
    print(response.text)
    response_json = response.json()
    if response_json["status"] == "COMPLETED":
        body_message.markdown("## Here's Your Story Outline 🚀")
        body_container.write("".join(response_json["output"]["text"]))
        return "".join(response_json["output"]["text"])

    status_url = f"https://api.runpod.ai/v2/llama2-7b-chat/stream/{response_json['id']}"

    output = ""
    body_message.markdown("## Generating Your Story Outline...")

    while True:
        time.sleep(.5)
        try:
            get_status = requests.get(status_url, headers=headers)
            get_status_json = get_status.json()
            if "stream" in get_status_json:
                for stream in get_status_json["stream"]:
                    next_tokens = "".join(stream["output"]["text"])
                    output += next_tokens
                    body_container.write(output)
                    print(next_tokens)
            
            if get_status_json["status"] == "IN_PROGRESS":
                continue
            else:
                end_time = time.time()
                print("Text generation time:", (end_time - start_time)/60)
                body_message.markdown("## Here's Your Story Outline 🚀")
                return output

        except Exception as e:
            print(str(e))
            return output


def request_character_art(bio):
    url = "https://api.runpod.ai/v2/sd-anything-v3/runsync"

    payload = { 
        "input": {
            "prompt": f"Portrait, white background, the character description is {bio}",
            "height": 256,
            "width": 256,
            "num_outputs": 1,
            "num_inference_steps": 50,
            "guidance_scale": 10,
            "scheduler": "KLMS"
        } 

    }
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": API_KEY
    }

    response = requests.post(url, json=payload, headers=headers)
    print(response.text)
    
    art_image = response.json()["output"][0]["image"]
    
    return art_image


def generate_story_outline():
    st.session_state['story_outline'] = None

    output = request_story_outline(
        st.session_state.title, 
        st.session_state.genre, 
        st.session_state.setting, 
        st.session_state.characters
    )

    # with open("./test_outline.txt", "w+") as f:
    #     f.write(output)

    if output:
        st.session_state.story_outline = output
    else:
        st.session_state.story_outline = None


def goto_screenplay():
    st.session_state.screenplay_writing_mode = True


def write_screenplay(screenplay_body_container, screenplay_body_message, screenplay_actions):
    def page_writer():        
        output = request_screenplay_page(screenplay_body_container, screenplay_body_message)

        st.session_state.screenplay = output
        if 'SCRIPT MONKEY END' in output:
            output = "".join(output.split("SCRIPT MONKEY END"))
            screenplay_body_message.markdown("## 🍌 Screenplay Finished! 🍌")
            screenplay_actions.download_button(
                label="Download Screenplay (.md)",
                data=st.session_state.screenplay,
                file_name='screenplay.md',
                mime='text/markdown')
        else:
            output = "".join(output.split("SCRIPT MONKEY CONTINUE"))
            return page_writer()

    page_writer()

if 'screenplay_writing_mode' in st.session_state:
    screenplay_writing_mode = copy.deepcopy(st.session_state.screenplay_writing_mode)
else:
    screenplay_writing_mode = None

if 'story_outline' in st.session_state:
    story_outline = copy.deepcopy(st.session_state.story_outline)
else:
    story_outline = None
    
if screenplay_writing_mode:
    tab1, tab2 = st.tabs(["Screenplay", "Story Outline"])

    with tab1:
        _write_screenplay = tab1.button("Generate New Screenplay", type="primary")
        
        screenplay_body_message = tab1.empty()
        screenplay_actions = tab1.container()
        screenplay_body_container = tab1.empty()

        if 'screenplay' in st.session_state and st.session_state.screenplay:
            screenplay_body_container.text(st.session_state['screenplay'])

        if _write_screenplay:
            write_screenplay(screenplay_body_container, screenplay_body_message, screenplay_actions)

    with tab2:
        tab2.button("Re-generate the story outline", type="secondary", on_click=generate_story_outline)
        tab2.write(st.session_state['story_outline'])
   
else:
    # story outline page (before screenplay writing)
    if story_outline:
        col1, col2 = st.columns([1,1])

        with col1:
            body_actions.button("Re-generate the story outline", type="secondary", on_click=generate_story_outline)
        
        with col2:
            _goto_screenplay = body_actions.button("Continue To Screenplay", type="primary")
            if _goto_screenplay:
                goto_screenplay()

        body_container.write(story_outline)

if 'characters' in st.session_state:
    characters = copy.deepcopy(st.session_state.characters)
else:
    characters = []




with st.sidebar:
    st.markdown("# New Screenplay Project")
    
    st.divider()

    # setting the default label to none to use a subheader instead
    st.markdown("## Your Movie Title")
    st.session_state.title = st.text_input(
        "Your Movie Title", 
        label_visibility="collapsed", 
        placeholder="(e.g. Script Monkey vs The World Part 3)")
    
    st.markdown("## Main Characters")

    # Load the character list view
    if 'characters' in st.session_state:
        for i, character in enumerate(st.session_state.characters):
            print("character", character)
            col1, col2, col3 = st.columns([1,3,1])
            with col1:
                art_image = character["art_image"]
                st.image(art_image)

            with col2:
                st.markdown(f"### {character['name']}")
                st.markdown(character["bio"])

            with col3:
                def delete_character():
                    del characters[i]
                    st.session_state.characters = characters

                st.button("X", on_click=delete_character, key=i)
    
    my_expander = st.expander(label='Add a Character', expanded=False)
    
    with my_expander:
        def character_art_toggle(x, y):
            print(x, y)
            st.session_state.current_character_art = val

        def submit_character():
            if st.session_state.character_loading:
                return;

            st.session_state.character_loading = True
            if st.session_state.current_character_art:
                # get art image from runpod stable diffusion
                try:

                    art_image = request_character_art(st.session_state.current_character_bio)
                except Exception as e:
                    print(str(e))
                    # message that if failed
                    art_image = Image.open('character.png')
            else:
                art_image = Image.open('character.png')

            character = {
                "name": st.session_state.current_character_name,
                "bio": st.session_state.current_character_bio,
                "art_image": art_image
            }
            
            characters.append(character)
            st.session_state.characters = characters
            st.session_state.character_loading = False
        # todo
        # st.button("Generate Random Character (experimental)")

        st.session_state.current_character_name = st.text_input("Character Name")
        st.session_state.current_character_bio = st.text_area("Short Character Bio", max_chars=150)
        st.session_state.current_character_art = st.toggle("Generate Character Art (experimental)")

        if st.session_state.character_loading:
            st.markdown("***Loading character....***")
        st.button("Add Character", on_click=submit_character)

    st.markdown("## Genre (optional)")
    st.session_state.genre = st.text_input(
        "Genre", 
        label_visibility="collapsed", 
        placeholder="(e.g. Romantic Comedy)")
  
    st.markdown("## Setting (optional)")
    st.session_state.setting = st.text_input(
        "Setting", 
        label_visibility="collapsed", 
        placeholder="(e.g. Cyberpunk dystopian world)")

    st.divider()

    st.markdown("*note: Story outline generation may take a minute or two*")
    st.button("Generate", type="primary", on_click=generate_story_outline)
