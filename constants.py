from managedState.extensions import KeyQueryFactory


class Constants:
    PATH_DYNAMIC_KEY = KeyQueryFactory(lambda sub_state, key: key)

    # Misc
    COLOURS = {
        "black": "#000000",
        "white": "#FFFFFF"
    }
