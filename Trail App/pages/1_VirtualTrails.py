import streamlit as st
from openai import OpenAI
from PIL import Image
import ast
import re


# --- Setup ---
api_key = st.secrets["openai_api_key"]
client = OpenAI(api_key=api_key)



# Trail options
trails = [
    {"trail_name": "Coyote Creek Trail", "location": "San Jose, CA"},
    {"trail_name": "Los Gatos Creek Trail", "location": "San Jose, CA"},
    {"trail_name": "Penitencia Creek Trail", "location": "San Jose, CA"},
]

# --- Title ---
st.title("🚶‍♂️ San Jose Virtual Trails (AI-Powered)")

# --- Trail selection ---
trail_names = [t["trail_name"] for t in trails]
selected_trail_idx = st.selectbox("Select a trail in San Jose:", range(len(trail_names)), format_func=lambda i: trail_names[i])

selected_trail = trails[selected_trail_idx]
trail_name = selected_trail["trail_name"]
location = selected_trail["location"]

st.markdown(f"You selected: **{trail_name}** — {location}")

if st.button("Generate Trail Overview"):
    # --- Display official trail image ---
    if trail_name == "Coyote Creek Trail":
        image = Image.open("Trail App/assets/Coyote Creek.jpeg")  # Point to assets folder
        st.image(image, caption="Coyote Creek Trail", use_container_width=True)

    elif trail_name == "Los Gatos Creek Trail":
        image = Image.open("Trail App/assets/Los Gatos Creek.jpg")  # Point to assets folder
        st.image(image, caption="Los Gatos Creek Trail", use_container_width=True)

    elif trail_name == "Penitencia Creek Trail":
        image = Image.open("Trail App/assets/Penitencia Creek.webp")  # Point to assets folder
        st.image(image, caption="Penitencia Creek Trail", use_container_width=True)

    # --- Generate AI trail info ---
    prompt_general = f"""
You are an expert naturalist and urban trail guide.

Generate the following information (4-6 sentences each) for the {trail_name} located in {location}:
1. Total length in miles and kilometers. Give a reasonable estimate for a trail of this name in San Jose.
2. Approximate times to complete the whole trail (one-way), from start to midpoint, and out-and-back (round trip), assuming moderate-walking pace.
3. Overall difficulty (Easy/Moderate/Hard) with a brief reason.
4. 2 interesting facts about the trail or area.
5. 2-3 safety cautions or environmental hazards to watch for.
6. List 4–6 plausible stop names along the trail (short descriptions).
7. A 1-2 sentence general description of the virtual route. Add a link to [San Jose Trail Maps](https://www.sanjoseca.gov/your-government/departments-offices/parks-recreation-neighborhood-services/planning-development/trail-network/trail-maps).

Format with Markdown, using clear bullet points or bold section titles.
"""
    with st.spinner("Generating trail overview with AI..."):
        general_info = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt_general}],
            temperature=0.7,
            max_tokens=900
        ).choices[0].message.content

    # Save into session
    st.session_state["trail_info"] = general_info
    st.session_state["active_trail_name"] = trail_name
    st.session_state["trail_stops"] = []
    st.session_state["stop_descriptions"] = []
    st.session_state["virtual_route_desc"] = ""
    st.session_state["current_stop"] = 0

# --- Display Trail Overview ---
general_info = st.session_state.get("trail_info", "")
if general_info:
    st.markdown(general_info)
else:
    st.info("After selecting a trail, click 'Generate Trail Overview' to start.")

# --- Button to generate stops ---
if st.session_state.get("trail_info") and st.button("Generate & Begin Virtual Walk"):
    prompt_extract_stops = f"""
From this AI-generated trail info, extract a list of trail stop names and short descriptions for the "{trail_name}".
Format like a Python list: ["Stop Name: short description", ...]
TRAIL INFO:
{st.session_state['trail_info']}
"""
    extraction = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt_extract_stops}],
        temperature=0.3,
        max_tokens=250
    ).choices[0].message.content

    # Attempt to parse AI response
    stops = []
    try:
        stops = ast.literal_eval(re.search(r"\[.*\]", extraction, re.DOTALL).group(0))
    except:
        stops = [line.strip('",[] ') for line in extraction.split("\n") if ':' in line]

    st.session_state["trail_stops"] = stops
    st.session_state["current_stop"] = 0

# --- Display Stop Navigation ---
if st.session_state.get("trail_stops"):
    trail_stops = st.session_state["trail_stops"]
    num_stops = len(trail_stops)

    col1, col2, col3 = st.columns([1, 3, 1])
    with col1:
        if st.button("⏮ Previous Stop", key="prevstop") and st.session_state["current_stop"] > 0:
            st.session_state["current_stop"] -= 1
    with col3:
        if st.button("Next Stop ⏭", key="nextstop") and st.session_state["current_stop"] < num_stops - 1:
            st.session_state["current_stop"] += 1

    current_stop_idx = st.session_state["current_stop"]
    stop_name_desc = trail_stops[current_stop_idx]

    if ":" in stop_name_desc:
        stop_name, stop_short_desc = stop_name_desc.split(":", 1)
    else:
        stop_name, stop_short_desc = stop_name_desc, ""

    # --- Generate AI stop description ---
    prompt_stop = f"""
For the {trail_name} in {location}, generate a detailed description for the stop "{stop_name}" ({stop_short_desc.strip()}).

Include:
- How this stop/area supports clean water (ecosystem, habitat, management)
- At least one notable plant or animal present
- 1–2 responsible hiking or stewardship tips
- A trail safety caution if relevant
- A short fun 'Did you know?' fact
Write in a friendly, educational tone (100–150 words max).
"""
    with st.spinner(f"AI is describing {stop_name.strip()}..."):
        stop_detail = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt_stop}],
            temperature=0.7,
            max_tokens=300
        ).choices[0].message.content

    st.markdown(f"### 🚩 Stop {current_stop_idx + 1} of {num_stops}: {stop_name.strip()}")
    st.markdown(f"*{stop_short_desc.strip()}*")
    st.markdown(stop_detail)

    # Progress bar
    progress = int(((current_stop_idx + 1) / num_stops) * 100)
    st.progress(progress)
else:
    st.info("After the overview, click 'Generate & Begin Virtual Walk' to see AI-powered stops and navigation.")

