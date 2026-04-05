import asyncio
from typing import List, Dict, Any, Callable

class Worker:
    def __init__(self, agent_id: str, prompt: str):
        self.agent_id = agent_id
        self.prompt = prompt
        self.status = "pending"
        self.result = None

    async def execute(self, model_callable: Callable):
        """Executes the worker's task asynchronously."""
        self.status = "running"
        try:
            # Simulate calling the model execution engine
            self.result = await model_callable(self.prompt)
            self.status = "completed"
        except Exception as e:
            self.result = str(e)
            self.status = "failed"
        return self.result

class TaskGraph:
    """
    Ported from Coordinator.ts.
    Manages parallel execution of independent workers using the TeammateTool pattern.
    """
    def __init__(self):
        self.workers: Dict[str, Worker] = {}

    def spawn_worker(self, agent_id: str, prompt: str) -> Worker:
        worker = Worker(agent_id, prompt)
        self.workers[agent_id] = worker
        return worker

    async def execute_parallel(self, worker_ids: List[str], model_callable: Callable) -> Dict[str, Any]:
        """
        Executes a set of workers in parallel.
        """
        tasks = []
        for wid in worker_ids:
            worker = self.workers.get(wid)
            if worker:
                tasks.append(worker.execute(model_callable))

        results = await asyncio.gather(*tasks, return_exceptions=True)
        return {wid: res for wid, res in zip(worker_ids, results)}

    def get_worker_status(self, agent_id: str) -> str:
        worker = self.workers.get(agent_id)
        if worker:
            return worker.status
        return "not_found"

    def stop_worker(self, agent_id: str):
        worker = self.workers.get(agent_id)
        if worker and worker.status == "running":
            worker.status = "stopped"
            # In a real async environment, we would cancel the task here.
