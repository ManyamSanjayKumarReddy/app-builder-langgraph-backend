from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import asyncio

from agent_v1.runtime.process_manager import process_manager

router = APIRouter(prefix="/projects", tags=["runtime-ws"])


@router.websocket("/{project_name}/runtime/ws/logs")
async def runtime_logs_ws(websocket: WebSocket, project_name: str):
    await websocket.accept()

    if not process_manager.has_process(project_name):
        await websocket.send_text("ERROR: No running process")
        await websocket.close()
        return

    process = process_manager.get_process(project_name)

    try:
        while True:
            sent = False

            try:
                line = process.stdout_queue.get_nowait()
                await websocket.send_text(line.rstrip())
                sent = True
            except Exception:
                pass

            try:
                line = process.stderr_queue.get_nowait()
                await websocket.send_text(f"[stderr] {line.rstrip()}")
                sent = True
            except Exception:
                pass

            if not sent:
                await asyncio.sleep(0.1)

            if not process.alive:
                await websocket.send_text("[process exited]")
                break

    except WebSocketDisconnect:
        pass

    finally:
        await websocket.close()
