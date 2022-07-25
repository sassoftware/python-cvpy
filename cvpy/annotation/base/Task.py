class Task(object):

    def __init__(self, task_id: str, start_image_id: str, end_image_id: str) -> None:
        self._task_id = task_id
        self._start_image_id = start_image_id
        self._end_image_id = end_image_id

    @property
    def task_id(self) -> str:
        return self._task_id

    @task_id.setter
    def task_id(self, task_id: str) -> None:
        self._task_id = task_id

    @property
    def start_image_id(self) -> str:
        return self._start_image_id

    @start_image_id.setter
    def start_image_id(self, start_image_id: str) -> None:
        self._start_image_id = start_image_id

    @property
    def end_image_id(self) -> str:
        return self._end_image_id

    @end_image_id.setter
    def end_image_id(self, end_image_id: str) -> None:
        self._end_image_id = end_image_id
