from pydantic import (
    BaseModel,
)


def model_dump_no_secrets(model: BaseModel, mode="python", reveal_secrets: set = set()) -> dict:
    schema = model.model_dump(mode=mode, exclude=reveal_secrets)
    for key in reveal_secrets:
        schema[key] = getattr(model, key).get_secret_value()
    return schema
