import importlib


def main():
    import ghia

    importlib.reload(ghia)  # force reload (config could change)
    if hasattr(ghia, 'app'):
        return ghia.app
    elif hasattr(ghia, 'create_app'):
        return ghia.create_app(None)
    else:
        raise RuntimeError(
            "Can't find a Flask app. "
            "Either instantiate `ghia.app` variable "
            "or implement `ghia.create_app(dummy)` function. "
            "See https://flask.palletsprojects.com/en/1.1.x/patterns"
            "/appfactories/"
            "for additional information."
            )

if __name__ == "__main__":
    main()