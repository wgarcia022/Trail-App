from openai import OpenAI
import streamlit as st
import pandas as pd

# Initialize OpenAI client
api_key = st.secrets["openai_api_key"]
client = OpenAI(api_key=api_key)


# Set page config
st.set_page_config(page_title="Eco Actions Tracker", page_icon="🌿", layout="centered")

# Initialize session state
if 'eco_points' not in st.session_state:
    st.session_state.eco_points = 0
if 'badges' not in st.session_state:
    st.session_state.badges = []

# Eco actions with points
eco_actions = {
    "🗑️ Picked up trash": {
        "points": 10,
        "description": "Helped keep the trail clean by collecting and properly disposing of litter."
    },
    "🥾 Stayed on trail": {
        "points": 5,
        "description": "Protected the environment by sticking to the marked trails and avoiding damage to surrounding vegetation."
    },
    "🌱 Educated someone about eco-friendly hiking": {
        "points": 15,
        "description": "Spread awareness about sustainable hiking practices to help others protect nature."
    },
    "🚯 Carried reusable water bottle": {
        "points": 5,
        "description": "Reduced waste by using a reusable water bottle instead of single-use plastic bottles."
    },
    "📷 Reported trail issue": {
        "points": 10,
        "description": "Contributed to trail maintenance by reporting hazards or issues to the authorities."
    }
}


# Badge thresholds
badge_levels = {
    "Eco Starter 🌱": 20,
    "Trail Hero 🦸‍♂️": 50,
    "Green Guardian 🌳🌟": 100
}

# Title
st.title("🌍 Log Your Eco-Friendly Actions")
st.markdown("Track your efforts and earn **EcoPoints** + badges as you help protect our trails!")

# Action selection
st.subheader("✅ Select the actions you completed today:")
selected_actions = []
for action in eco_actions:
    if st.checkbox(action):
        selected_actions.append(action)

# Submit button
if st.button("Submit Actions"):
    points_earned = sum(eco_actions[action]["points"] for action in selected_actions)
    st.session_state.eco_points += points_earned
    st.success(f"You earned {points_earned} EcoPoints! 🌟")
    
    # Show what user selected with descriptions
    if selected_actions:
        st.markdown("### 📝 Actions You Logged:")
        for action in selected_actions:
            st.markdown(f"**{action}** – {eco_actions[action]['description']}")

    # Badge check
    for badge, threshold in badge_levels.items():
        if st.session_state.eco_points >= threshold and badge not in st.session_state.badges:
            st.session_state.badges.append(badge)
            st.balloons()
            st.toast(f"🎉 Congrats! You've earned the '{badge}' badge!")

             # Let user know how many points to next badge
    next_badge_points = None
    for badge, threshold in sorted(badge_levels.items(), key=lambda x: x[1]):
        if st.session_state.eco_points < threshold:
            next_badge_points = threshold - st.session_state.eco_points
            next_badge_name = badge
            break

    if next_badge_points is not None:
        st.info(f"✨ Only **{next_badge_points} EcoPoints** more to reach **'{next_badge_name}'** badge! Keep going!")
    else:
        st.info("🏆 You've earned all available badges! Amazing work!")


# Display current score and badges
st.markdown("---")
st.subheader("🎯 Your Progress:")
st.write(f"**Total EcoPoints:** {st.session_state.eco_points}")
st.progress(min(st.session_state.eco_points, 100))

if st.session_state.badges:
    st.write("**🏅 Badges Earned:**")
    for badge in st.session_state.badges:
        st.markdown(f"- {badge}")
else:
    st.write("No badges yet — keep logging actions!")

# ----------------------------------------------
# 🌱 Trail Stewardship Section: Why & How-to
# ----------------------------------------------
st.markdown("---")
st.markdown("## 🌱 Protect the Flow, Preserve the Trail")

st.write(
    """
    Creekside trails aren’t just scenic routes — they help keep our water clean and our ecosystems strong.
    Every step we take can either help preserve it or accidentally harm it.

    Now that you've logged your eco-friendly actions, here are some simple but powerful ways you can keep making a difference — even after today.
    """
)

# Trail tips and prompts
protection_tips = [
    {
        "title": "Pack it out for the Creek",
        "tip": "Trash left behind can wash into the creek — take yours and a little extra litter back with you to help keep the water clean.",
        "prompt": "a hiker picking up trash with a reusable bag on a clean creekside forest trail"
    },
    {
        "title": "Snap Smart",
        "tip": "Snapping the perfect photo? Just zoom in from the trail — no need to wander off-path. Nature looks best when we leave it just as we found it.",
        "prompt": "a hiker taking a photo of a wildflower while standing on a marked forest trail, respecting nature and staying off sensitive vegetation"
    },
    {
        "title": "Bring a Reusable Bottle",
        "tip": "A refillable bottle keeps you going — and keeps plastic out of the trail.",
        "prompt": "a reusable water bottle placed on a rock beside a creek in a natural park"
    },
    {
        "title": "Report Trail Damage",
        "tip": "If you see flooding, erosion, or fallen trees, take a photo and share it with Santa Clara Valley Water District.",
        "prompt": "a person taking a photo of a damaged trail next to a creek for reporting"
    }
]

for i, tip in enumerate(protection_tips):
    with st.expander(f"📌 {tip['title']}"):
        st.write(tip["tip"])
        if st.button(f"Show example image for: {tip['title']}", key=f"img_{i}"):
            with st.spinner("Generating example image..."):
                try:
                    response = client.images.generate(
                        model="dall-e-3",  
                        prompt=tip["prompt"],
                        size="1024x1024",  
                        quality="standard",
                        n=1
                    )
                    image_url = response.data[0].url
                    st.image(image_url, caption=tip["title"], use_container_width=True)
                except Exception as e:
                    st.error(f"Couldn't generate image: {str(e)}")