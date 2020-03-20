from typing import Any

from junction.confluence.api import _ApiClient
from junction.confluence.models import (
    Content,
    ContentArray,
    UpdateContent,
    CreateContent,
)


BASE_PATH = "content"


class ContentApi(object):
    """The Confluence Content API is used for managing all forms of contents including pages,
    blog posts, comments, attachments, and more.  Pages are well supported; the other types have not been
    touched or tested.  Only the needed methods are implemented; this is not a general purpose Confluence API
    wrapper.

    Reference https://developer.atlassian.com/cloud/confluence/rest/ for API semantics.
    """

    def __init__(self, api_client: _ApiClient, space_key: str) -> None:
        self.__api_client = api_client
        self.__space_key = space_key

    def create_content(self, content: CreateContent, **kwargs: Any) -> Content:
        """https://developer.atlassian.com/cloud/confluence/rest/#api-api-content-post"""
        response = self.__api_client.post(BASE_PATH, body=content, **kwargs)
        return self.__api_client.decode(response.text, Content)

    def update_content(
        self, content_id: str, content: UpdateContent, **kwargs: Any
    ) -> Content:
        """https://developer.atlassian.com/cloud/confluence/rest/#api-api-content-id-put"""
        response = self.__api_client.put(
            f"{BASE_PATH}/{content_id}", body=content, **kwargs
        )
        return self.__api_client.decode(response.text, Content)

    def delete_content(self, content_id: str, **kwargs: Any) -> None:
        """https://developer.atlassian.com/cloud/confluence/rest/#api-api-content-id-delete"""
        self.__api_client.delete(f"{BASE_PATH}/{content_id}", **kwargs)

    def get_content(
        self,
        type: str = None,
        title: str = None,
        status: str = None,
        posting_day: str = None,
        expand: str = None,
        trigger: str = None,
        start: int = 0,
        limit: int = 25,
        **kwargs: Any,
    ) -> ContentArray:
        """https://developer.atlassian.com/cloud/confluence/rest/#api-api-content-get"""
        query_params = {
            "type": type,
            "spaceKey": self.__space_key,
            "title": title,
            "status": status,
            "postingDay": posting_day,
            "expand": expand,
            "trigger": trigger,
            "start": start,
            "limit": limit,
        }

        if "query_params" in kwargs:
            query_params.update(kwargs["query_params"])
            del kwargs["query_params"]

        response = self.__api_client.get(
            BASE_PATH,
            query_params={k: v for k, v in query_params.items() if v is not None},
            **kwargs,
        )
        return self.__api_client.decode(response.text, ContentArray)

    def get_content_by_id(self, content_id: str, **kwargs: Any) -> Content:
        """https://developer.atlassian.com/cloud/confluence/rest/#api-api-content-id-get"""
        response = self.__api_client.get(f"{BASE_PATH}/{content_id}", **kwargs)
        return self.__api_client.decode(response.text, Content)
