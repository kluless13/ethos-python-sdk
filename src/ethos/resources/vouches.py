"""
Vouches resource for Ethos API.
"""

from __future__ import annotations

from collections.abc import AsyncIterator, Iterator
from typing import TYPE_CHECKING, Any

from ethos.resources.base import AsyncBaseResource, BaseResource
from ethos.types.vouch import Vouch

if TYPE_CHECKING:
    pass


class Vouches(BaseResource[Vouch]):
    """
    Vouches API resource.

    Access vouch relationships between profiles.
    """

    _path = "/vouches"
    _model = Vouch

    def get(self, vouch_id: int) -> Vouch:
        """
        Get a vouch by ID.

        Args:
            vouch_id: The vouch ID

        Returns:
            The vouch
        """
        response = self._http.get(f"{self._path}/{vouch_id}")
        return self._parse_item(response)

    def _paginate_post(
        self,
        path: str,
        body: dict[str, Any],
        limit: int = 100,
    ) -> Iterator[Vouch]:
        """
        Iterate through pages using POST with body params.

        The vouches API uses POST with body instead of GET with query params.
        """
        offset = 0

        while True:
            body["limit"] = limit
            body["offset"] = offset

            response = self._http.post(path, json=body)

            # Handle different response formats
            if isinstance(response, list):
                items = response
            elif "data" in response:
                items = response["data"]
            elif "values" in response:
                items = response["values"]
            else:
                items = response.get("results", [])

            if not items:
                break

            for item in items:
                yield self._parse_item(item)

            if len(items) < limit:
                break

            offset += limit

    def list(
        self,
        author_profile_id: int | None = None,
        target_profile_id: int | None = None,
        staked: bool | None = None,
        archived: bool | None = None,
        limit: int = 100,
    ) -> Iterator[Vouch]:
        """
        List vouches with optional filtering.

        Args:
            author_profile_id: Filter by voucher (who gave the vouch)
            target_profile_id: Filter by target (who received the vouch)
            staked: Filter by staked status
            archived: Filter by archived status
            limit: Page size

        Yields:
            Vouch objects
        """
        body: dict[str, Any] = {}

        # Build subject/author profile ID lists for POST body
        if target_profile_id is not None:
            body["subjectProfileIds"] = [target_profile_id]
        if author_profile_id is not None:
            body["authorProfileIds"] = [author_profile_id]
        if staked is not None:
            body["staked"] = staked
        if archived is not None:
            body["archived"] = archived

        yield from self._paginate_post(self._path, body=body, limit=limit)

    def for_profile(self, profile_id: int) -> list[Vouch]:
        """
        Get all vouches received by a profile.

        Args:
            profile_id: The profile ID

        Returns:
            List of vouches received
        """
        return list(self.list(target_profile_id=profile_id))

    def by_profile(self, profile_id: int) -> list[Vouch]:
        """
        Get all vouches given by a profile.

        Args:
            profile_id: The profile ID

        Returns:
            List of vouches given
        """
        return list(self.list(author_profile_id=profile_id))

    def between(self, voucher_id: int, target_id: int) -> Vouch | None:
        """
        Get the vouch between two profiles if it exists.

        Args:
            voucher_id: Profile who gave the vouch
            target_id: Profile who received the vouch

        Returns:
            The vouch if it exists, None otherwise
        """
        vouches = list(
            self.list(
                author_profile_id=voucher_id,
                target_profile_id=target_id,
                limit=1,
            )
        )
        return vouches[0] if vouches else None


class AsyncVouches(AsyncBaseResource[Vouch]):
    """Async Vouches API resource."""

    _path = "/vouches"
    _model = Vouch

    async def get(self, vouch_id: int) -> Vouch:
        """Get a vouch by ID."""
        response = await self._http.get(f"{self._path}/{vouch_id}")
        return self._parse_item(response)

    async def _paginate_post(
        self,
        path: str,
        body: dict[str, Any],
        limit: int = 100,
    ) -> AsyncIterator[Vouch]:
        """
        Async iterate through pages using POST with body params.

        The vouches API uses POST with body instead of GET with query params.
        """
        offset = 0

        while True:
            body["limit"] = limit
            body["offset"] = offset

            response = await self._http.post(path, json=body)

            # Handle different response formats
            if isinstance(response, list):
                items = response
            elif "data" in response:
                items = response["data"]
            elif "values" in response:
                items = response["values"]
            else:
                items = response.get("results", [])

            if not items:
                break

            for item in items:
                yield self._parse_item(item)

            if len(items) < limit:
                break

            offset += limit

    async def list(
        self,
        author_profile_id: int | None = None,
        target_profile_id: int | None = None,
        staked: bool | None = None,
        archived: bool | None = None,
        limit: int = 100,
    ) -> AsyncIterator[Vouch]:
        """List vouches with optional filtering."""
        body: dict[str, Any] = {}

        # Build subject/author profile ID lists for POST body
        if target_profile_id is not None:
            body["subjectProfileIds"] = [target_profile_id]
        if author_profile_id is not None:
            body["authorProfileIds"] = [author_profile_id]
        if staked is not None:
            body["staked"] = staked
        if archived is not None:
            body["archived"] = archived

        async for vouch in self._paginate_post(self._path, body=body, limit=limit):
            yield vouch

    async def for_profile(self, profile_id: int) -> list[Vouch]:
        """Get all vouches received by a profile."""
        vouches = []
        async for vouch in self.list(target_profile_id=profile_id):
            vouches.append(vouch)
        return vouches

    async def by_profile(self, profile_id: int) -> list[Vouch]:
        """Get all vouches given by a profile."""
        vouches = []
        async for vouch in self.list(author_profile_id=profile_id):
            vouches.append(vouch)
        return vouches

    async def between(self, voucher_id: int, target_id: int) -> Vouch | None:
        """Get the vouch between two profiles if it exists."""
        async for vouch in self.list(
            author_profile_id=voucher_id,
            target_profile_id=target_id,
            limit=1,
        ):
            return vouch
        return None
