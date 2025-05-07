import uvicorn

import app.settings as settings


if __name__ == "__main__":

    port = settings.LISTEN_PORT
    enable_reload = settings.ENVIRONMENT == "development"

    uvicorn.run("app.app:app", host="0.0.0.0", port=port, reload=enable_reload)
