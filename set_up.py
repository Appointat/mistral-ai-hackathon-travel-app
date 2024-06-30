from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse

# from apps.streamlit_ui.multi_agents_async import async_main
from apps.streamlit_ui.role_playing_async import async_main

app = FastAPI()


async def process_request(content: str, user: dict):
    # task_prompt = content
    # context_text = content
    # num_roles = 4
    # num_subtasks = 3
    # search_enabled = False
    # response_language = "Chinese"
    # async for message in async_main(
    #     task_prompt=task_prompt,
    #     context_text=context_text,
    #     num_roles=num_roles,
    #     num_subtasks=num_subtasks,
    #     search_enabled=search_enabled,
    #     output_language=response_language,
    # ):
    #     yield message
    async for message in async_main(content):
        yield message
    yield "TASK_DONE"


@app.post("/process")
async def process(request: Request):
    data = await request.json()
    content = data["content"]
    user = data["user"]

    async def event_generator():
        async for message in process_request(content, user):
            yield f"{message}\n"

    return StreamingResponse(event_generator(), media_type="text/plain")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8101)
