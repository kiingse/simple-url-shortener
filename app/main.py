import logging.config

from fastapi import FastAPI

from app.common.config import Config
from app.common.fastapi_utils import RouterBuilder
from app.common.healthcheck import router as healthcheck_router
from app.url.routes import url_router

app_config = Config()

logging.config.fileConfig(app_config.LOGGING_CONF_FILE, disable_existing_loggers=False)

app = FastAPI(title=app_config.PROJECT_NAME)


app.include_router(
    RouterBuilder().with_router(healthcheck_router).with_router(url_router).build()
)
