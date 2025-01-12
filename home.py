import streamlit as st
import streamlit_authenticator as stauth

# import yaml
# from yaml.loader import SafeLoader

st.set_page_config(
    page_title="LLM Collection for Office",
    page_icon="💀",
)

username = list(st.secrets["credentials"]["usernames"].keys())[0]

credentials = {
    "credentials": {
        "usernames": {
            username: {
                "email": st.secrets["credentials"]["usernames"][username]["email"],
                "name": st.secrets["credentials"]["usernames"][username]["name"],
                "password": st.secrets["credentials"]["usernames"][username][
                    "password"
                ],
            }
        }
    },
    "cookie": {
        "expiry_days": st.secrets["cookie"]["expiry_days"],
        "key": st.secrets["cookie"]["key"],
        "name": st.secrets["cookie"]["name"],
    },
}

authenticator = stauth.Authenticate(
    # config["credentials"],
    # config["cookie"]["name"],
    # config["cookie"]["key"],
    # config["cookie"]["expiry_days"],
    credentials["credentials"],
    credentials["cookie"]["name"],
    credentials["cookie"]["key"],
    credentials["cookie"]["expiry_days"],
)


def login_callback(data):
    st.session_state["authentication_status"] = data["widget"]
    st.session_state["name"] = data["username"]


try:
    authenticator.login(callback=login_callback)
except Exception as e:
    st.error(e)

if st.session_state["authentication_status"]:
    authenticator.logout()
    st.write(f'Welcome *{st.session_state["name"]}*')
    st.title("LLM for Personal Use")
    st.markdown(
        """
# 1. Gemini Test
    """
    )
elif st.session_state["authentication_status"] is False:
    st.error("Username/password is incorrect")
elif st.session_state["authentication_status"] is None:
    st.warning("Please enter your username and password")
