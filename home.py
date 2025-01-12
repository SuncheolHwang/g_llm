import streamlit as st
import streamlit_authenticator as stauth

# import yaml
# from yaml.loader import SafeLoader

st.set_page_config(
    page_title="LLM Collection for Office",
    page_icon="💀",
)

# with open("./config.yaml") as file:
#     config = yaml.load(file, Loader=SafeLoader)

credentials = {
    "credentials": {
        "usernames": {
            "suncheol322": {
                "email": st.secrets["credentials"]["usernames"]["suncheol322"]["email"],
                "name": st.secrets["credentials"]["usernames"]["suncheol322"]["name"],
                "password": st.secrets["credentials"]["usernames"]["suncheol322"][
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
    st.title("LLM Test")
    st.markdown(
        """
# My LLM Collection
    """
    )
elif st.session_state["authentication_status"] is False:
    st.error("Username/password is incorrect")
elif st.session_state["authentication_status"] is None:
    st.warning("Please enter your username and password")
