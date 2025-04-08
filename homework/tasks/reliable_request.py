import abc

import httpx


class ResultsObserver(abc.ABC):
    @abc.abstractmethod
    def observe(self, data: bytes) -> None: ...


async def do_reliable_request(url: str, observer: ResultsObserver) -> None:
    """
    Одна из главных проблем распределённых систем - это ненадёжность связи.

    Ваша задача заключается в том, чтобы таким образом исправить этот код, чтобы он
    умел переживать возвраты ошибок и таймауты со стороны сервера, гарантируя
    успешный запрос (в реальной жизни такая гарантия невозможна, но мы чуть упростим себе задачу).

    Все успешно полученные результаты должны регистрироваться с помощью обсёрвера.
    """
    max_attempts = 10
    attempt = 0
    timeout = 10
    
    async with httpx.AsyncClient() as client:
        while attempt < max_attempts:
            try:
                response = await client.get(url, timeout=timeout)
                response.raise_for_status()
                data = response.read()

                observer.observe(data)
                return
            except httpx.HTTPError:
                attempt += 1
