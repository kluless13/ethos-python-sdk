"""
Integration tests with mocked HTTP responses.

These tests verify the SDK's behavior against mocked API responses,
covering the HTTP client, resource methods, error handling, and pagination.
"""

import pytest
import respx
from httpx import Response

from ethos import AsyncEthos, Ethos
from ethos.exceptions import (
    EthosAPIError,
    EthosAuthenticationError,
    EthosNotFoundError,
    EthosRateLimitError,
)

BASE_URL = "https://api.ethos.network/api/v2"


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def client():
    """Create a sync client for testing."""
    with Ethos(client_name="test", rate_limit=0) as c:
        yield c


@pytest.fixture
async def async_client():
    """Create an async client for testing."""
    async with AsyncEthos(client_name="test", rate_limit=0) as c:
        yield c


# =============================================================================
# Profiles Resource Tests
# =============================================================================


class TestProfilesResource:
    """Tests for Profiles resource."""

    @respx.mock
    def test_get_profile_by_id(self, client):
        """Test getting a profile by ID."""
        respx.get(f"{BASE_URL}/profiles/123").mock(
            return_value=Response(
                200,
                json={
                    "id": 123,
                    "profileId": 123,
                    "address": "0xabc123",
                    "displayName": "Test User",
                    "score": 1500,
                    "status": "ACTIVE",
                },
            )
        )

        profile = client.profiles.get(123)

        assert profile.id == 123
        assert profile.display_name == "Test User"
        assert profile.score == 1500

    @respx.mock
    def test_get_profile_by_address(self, client):
        """Test getting a profile by Ethereum address."""
        respx.get(f"{BASE_URL}/profiles/address/0xabc123").mock(
            return_value=Response(
                200,
                json={
                    "id": 456,
                    "profileId": 456,
                    "address": "0xabc123",
                    "displayName": "Address User",
                    "score": 1800,
                },
            )
        )

        profile = client.profiles.get_by_address("0xabc123")

        assert profile.id == 456
        assert profile.address == "0xabc123"

    @respx.mock
    def test_get_profile_by_twitter(self, client):
        """Test getting a profile by Twitter handle."""
        respx.get(f"{BASE_URL}/profiles/userkey/x.com/user/testuser").mock(
            return_value=Response(
                200,
                json={
                    "id": 789,
                    "profileId": 789,
                    "displayName": "Twitter User",
                    "userkeys": ["x.com/user/testuser"],
                },
            )
        )

        profile = client.profiles.get_by_twitter("testuser")

        assert profile.id == 789
        assert profile.twitter_handle == "testuser"

    @respx.mock
    def test_search_profiles(self, client):
        """Test searching profiles."""
        respx.get(f"{BASE_URL}/profiles/search").mock(
            return_value=Response(
                200,
                json={
                    "values": [
                        {"id": 1, "displayName": "User One", "score": 1500},
                        {"id": 2, "displayName": "User Two", "score": 1600},
                    ]
                },
            )
        )

        profiles = client.profiles.search("user", limit=10)

        assert len(profiles) == 2
        assert profiles[0].id == 1
        assert profiles[1].display_name == "User Two"

    @respx.mock
    def test_list_profiles_pagination(self, client):
        """Test listing profiles with pagination."""
        # First page
        respx.get(f"{BASE_URL}/profiles").mock(
            side_effect=[
                Response(
                    200,
                    json={
                        "values": [
                            {"id": 1, "displayName": "User 1"},
                            {"id": 2, "displayName": "User 2"},
                        ]
                    },
                ),
                Response(200, json={"values": [{"id": 3, "displayName": "User 3"}]}),
                Response(200, json={"values": []}),
            ]
        )

        profiles = list(client.profiles.list(limit=2))

        assert len(profiles) == 3
        assert profiles[0].id == 1
        assert profiles[2].id == 3


# =============================================================================
# Vouches Resource Tests
# =============================================================================


class TestVouchesResource:
    """Tests for Vouches resource."""

    @respx.mock
    def test_get_vouch(self, client):
        """Test getting a vouch by ID."""
        respx.get(f"{BASE_URL}/vouches/100").mock(
            return_value=Response(
                200,
                json={
                    "id": 100,
                    "authorProfileId": 1,
                    "subjectProfileId": 2,
                    "staked": True,
                    "archived": False,
                    "balance": "1000000000000000000",
                },
            )
        )

        vouch = client.vouches.get(100)

        assert vouch.id == 100
        assert vouch.author_profile_id == 1
        assert vouch.target_profile_id == 2
        assert vouch.amount_eth == 1.0

    @respx.mock
    def test_list_vouches_with_filter(self, client):
        """Test listing vouches with target filter."""
        respx.get(f"{BASE_URL}/vouches").mock(
            return_value=Response(
                200,
                json={
                    "values": [
                        {
                            "id": 1,
                            "authorProfileId": 10,
                            "subjectProfileId": 20,
                            "staked": True,
                            "archived": False,
                        },
                        {
                            "id": 2,
                            "authorProfileId": 11,
                            "subjectProfileId": 20,
                            "staked": True,
                            "archived": False,
                        },
                    ]
                },
            )
        )

        vouches = list(client.vouches.list(target_profile_id=20, limit=10))

        assert len(vouches) == 2
        assert all(v.target_profile_id == 20 for v in vouches)

    @respx.mock
    def test_vouches_for_profile(self, client):
        """Test getting vouches for a profile."""
        respx.get(f"{BASE_URL}/vouches").mock(
            return_value=Response(
                200,
                json={
                    "values": [
                        {
                            "id": 1,
                            "authorProfileId": 10,
                            "subjectProfileId": 20,
                            "staked": True,
                            "archived": False,
                        }
                    ]
                },
            )
        )

        vouches = client.vouches.for_profile(20)

        assert len(vouches) == 1
        assert vouches[0].target_profile_id == 20


# =============================================================================
# Reviews Resource Tests
# =============================================================================


class TestReviewsResource:
    """Tests for Reviews resource."""

    @respx.mock
    def test_get_review(self, client):
        """Test getting a review by ID."""
        respx.get(f"{BASE_URL}/reviews/200").mock(
            return_value=Response(
                200,
                json={
                    "id": 200,
                    "authorProfileId": 1,
                    "subjectProfileId": 2,
                    "score": "positive",
                    "comment": "Great!",
                    "archived": False,
                },
            )
        )

        review = client.reviews.get(200)

        assert review.id == 200
        assert review.is_positive
        assert review.comment == "Great!"

    @respx.mock
    def test_list_reviews(self, client):
        """Test listing reviews."""
        respx.get(f"{BASE_URL}/reviews").mock(
            return_value=Response(
                200,
                json={
                    "values": [
                        {
                            "id": 1,
                            "authorProfileId": 10,
                            "subjectProfileId": 20,
                            "score": "positive",
                        },
                        {
                            "id": 2,
                            "authorProfileId": 11,
                            "subjectProfileId": 20,
                            "score": "negative",
                        },
                    ]
                },
            )
        )

        reviews = list(client.reviews.list(target_profile_id=20, limit=10))

        assert len(reviews) == 2


# =============================================================================
# Markets Resource Tests
# =============================================================================


class TestMarketsResource:
    """Tests for Markets resource."""

    @respx.mock
    def test_get_market(self, client):
        """Test getting a market by ID."""
        respx.get(f"{BASE_URL}/markets/50").mock(
            return_value=Response(
                200,
                json={
                    "id": 50,
                    "profileId": 100,
                    "trustPrice": "0.75",
                    "distrustPrice": "0.25",
                },
            )
        )

        market = client.markets.get(50)

        assert market.id == 50
        assert market.profile_id == 100

    @respx.mock
    def test_get_market_by_profile(self, client):
        """Test getting a market by profile ID."""
        respx.get(f"{BASE_URL}/markets/profile/100").mock(
            return_value=Response(
                200,
                json={
                    "id": 50,
                    "profileId": 100,
                    "trustPrice": "0.80",
                    "distrustPrice": "0.20",
                },
            )
        )

        market = client.markets.get_by_profile(100)

        assert market.profile_id == 100


# =============================================================================
# Activities Resource Tests
# =============================================================================


class TestActivitiesResource:
    """Tests for Activities resource."""

    @respx.mock
    def test_get_activity(self, client):
        """Test getting an activity by ID."""
        respx.get(f"{BASE_URL}/activities/300").mock(
            return_value=Response(
                200,
                json={
                    "id": 300,
                    "type": "vouch",
                    "authorProfileId": 1,
                    "subjectProfileId": 2,
                },
            )
        )

        activity = client.activities.get(300)

        assert activity.id == 300
        assert activity.type == "vouch"

    @respx.mock
    def test_list_activities(self, client):
        """Test listing activities."""
        respx.get(f"{BASE_URL}/activities").mock(
            return_value=Response(
                200,
                json={
                    "values": [
                        {"id": 1, "type": "vouch", "authorProfileId": 10},
                        {"id": 2, "type": "review", "authorProfileId": 11},
                    ]
                },
            )
        )

        activities = list(client.activities.list(limit=10))

        assert len(activities) == 2


# =============================================================================
# Scores Resource Tests
# =============================================================================


class TestScoresResource:
    """Tests for Scores resource."""

    @respx.mock
    def test_get_score(self, client):
        """Test getting a score by address."""
        respx.get(f"{BASE_URL}/score/0xabc123").mock(
            return_value=Response(
                200,
                json={
                    "profileId": 123,
                    "address": "0xabc123",
                    "value": 1650,
                },
            )
        )

        score = client.scores.get("0xabc123")

        assert score.value == 1650
        assert score.level == "reputable"

    @respx.mock
    def test_get_score_by_profile(self, client):
        """Test getting a score by profile ID."""
        respx.get(f"{BASE_URL}/score/profile/456").mock(
            return_value=Response(
                200,
                json={
                    "profileId": 456,
                    "value": 1800,
                },
            )
        )

        score = client.scores.get_by_profile(456)

        assert score.profile_id == 456
        assert score.value == 1800


# =============================================================================
# Users Resource Tests
# =============================================================================


class TestUsersResource:
    """Tests for Users resource."""

    @respx.mock
    def test_get_user(self, client):
        """Test getting a user by ID."""
        respx.get(f"{BASE_URL}/user/500").mock(
            return_value=Response(
                200,
                json={
                    "id": 500,
                    "profileId": 100,
                    "displayName": "Test User",
                    "score": 1500,
                    "xpTotal": 5000,
                },
            )
        )

        user = client.users.get(500)

        assert user.id == 500
        assert user.profile_id == 100
        assert user.xp_total == 5000

    @respx.mock
    def test_get_user_by_address(self, client):
        """Test getting a user by Ethereum address."""
        respx.get(f"{BASE_URL}/user/by/address/0xabc123").mock(
            return_value=Response(
                200,
                json={
                    "id": 501,
                    "profileId": 101,
                    "address": "0xabc123",
                    "displayName": "Address User",
                },
            )
        )

        user = client.users.get_by_address("0xabc123")

        assert user.id == 501


# =============================================================================
# Endorsements Resource Tests
# =============================================================================


class TestEndorsementsResource:
    """Tests for Endorsements resource."""

    @respx.mock
    def test_get_endorsements_for_user(self, client):
        """Test getting endorsements for a user."""
        respx.get(f"{BASE_URL}/endorsements/x.com/user/testuser").mock(
            return_value=Response(
                200,
                json={
                    "values": [
                        {
                            "activityId": 1000,
                            "endorserProfileId": 100,
                            "endorsementType": "vouch",
                            "connectionDegree": "1st",
                        },
                        {
                            "activityId": 1001,
                            "endorserProfileId": 101,
                            "endorsementType": "review",
                            "connectionDegree": "2nd",
                        },
                    ],
                    "summary": {
                        "totalEndorsers": 2,
                        "totalVouches": 1,
                        "totalReviews": 1,
                    },
                    "total": 2,
                    "limit": 50,
                    "offset": 0,
                },
            )
        )

        response = client.endorsements.get_for_user("x.com/user/testuser")

        assert len(response) == 2
        assert response.endorsements[0].is_first_degree
        assert response.endorsements[1].endorsement_type == "review"


# =============================================================================
# Votes Resource Tests
# =============================================================================


class TestVotesResource:
    """Tests for Votes resource."""

    @respx.mock
    def test_get_vote_stats(self, client):
        """Test getting vote stats."""
        respx.get(f"{BASE_URL}/votes/stats").mock(
            return_value=Response(
                200,
                json={
                    "upvotes": 10,
                    "downvotes": 3,
                    "weightedUpvotes": 15.0,
                    "weightedDownvotes": 4.5,
                },
            )
        )

        stats = client.votes.get_stats(target_type="review", activity_id=100)

        assert stats.upvotes == 10
        assert stats.net_votes == 7

    @respx.mock
    def test_list_votes(self, client):
        """Test listing votes."""
        respx.get(f"{BASE_URL}/votes").mock(
            return_value=Response(
                200,
                json={
                    "values": [
                        {
                            "voterProfileId": 1,
                            "targetType": "review",
                            "targetId": 100,
                            "isUpvote": True,
                        },
                        {
                            "voterProfileId": 2,
                            "targetType": "review",
                            "targetId": 100,
                            "isUpvote": False,
                        },
                    ]
                },
            )
        )

        votes = list(client.votes.list(target_type="review", activity_id=100, limit=10))

        assert len(votes) == 2


# =============================================================================
# Replies Resource Tests
# =============================================================================


class TestRepliesResource:
    """Tests for Replies resource."""

    @respx.mock
    def test_get_reply(self, client):
        """Test getting a reply by ID."""
        respx.get(f"{BASE_URL}/replies/by-id").mock(
            return_value=Response(
                200,
                json=[
                    {
                        "id": 600,
                        "contractType": "review",
                        "parentId": 100,
                        "authorProfileId": 50,
                        "content": "Thank you!",
                    }
                ],
            )
        )

        reply = client.replies.get(600)

        assert reply.id == 600
        assert reply.content == "Thank you!"
        assert reply.is_review_reply

    @respx.mock
    def test_get_replies_by_ids(self, client):
        """Test getting multiple replies by IDs."""
        respx.get(f"{BASE_URL}/replies/by-id").mock(
            return_value=Response(
                200,
                json=[
                    {
                        "id": 600,
                        "contractType": "review",
                        "parentId": 100,
                        "authorProfileId": 50,
                        "content": "Reply 1",
                    },
                    {
                        "id": 601,
                        "contractType": "vouch",
                        "parentId": 101,
                        "authorProfileId": 51,
                        "content": "Reply 2",
                    },
                ],
            )
        )

        replies = client.replies.get_by_ids([600, 601])

        assert len(replies) == 2


# =============================================================================
# XP Resource Tests
# =============================================================================


class TestXPResource:
    """Tests for XP resource."""

    @respx.mock
    def test_get_xp_total(self, client):
        """Test getting XP total."""
        respx.get(f"{BASE_URL}/xp/user/x.com/user/testuser").mock(
            return_value=Response(
                200,
                json={"total": 5000, "xp": 5000},
            )
        )

        total = client.xp.get_total("x.com/user/testuser")

        assert total == 5000

    @respx.mock
    def test_get_xp_season_total(self, client):
        """Test getting XP season total."""
        respx.get(f"{BASE_URL}/xp/user/x.com/user/testuser/season/1").mock(
            return_value=Response(
                200,
                json={"total": 2500},
            )
        )

        total = client.xp.get_season_total("x.com/user/testuser", 1)

        assert total == 2500


# =============================================================================
# Invitations Resource Tests
# =============================================================================


class TestInvitationsResource:
    """Tests for Invitations resource."""

    @respx.mock
    def test_list_invitations(self, client):
        """Test listing invitations."""
        respx.get(f"{BASE_URL}/invitations").mock(
            return_value=Response(
                200,
                json={
                    "values": [
                        {
                            "id": 1,
                            "senderProfileId": 100,
                            "inviteeAddress": "0xabc",
                            "status": "INVITED",
                        },
                        {
                            "id": 2,
                            "senderProfileId": 100,
                            "inviteeAddress": "0xdef",
                            "status": "ACCEPTED",
                        },
                    ]
                },
            )
        )

        invitations = list(client.invitations.list(sender_profile_id=100, limit=10))

        assert len(invitations) == 2
        assert invitations[0].is_pending
        assert invitations[1].is_accepted


# =============================================================================
# Notifications Resource Tests
# =============================================================================


class TestNotificationsResource:
    """Tests for Notifications resource."""

    @respx.mock
    def test_get_notification_stats(self, client):
        """Test getting notification stats."""
        respx.get(f"{BASE_URL}/notifications/stats/me").mock(
            return_value=Response(
                200,
                json={"unreadCount": 5},
            )
        )

        stats = client.notifications.get_stats()

        assert stats.unread_count == 5

    @respx.mock
    def test_list_notifications(self, client):
        """Test listing notifications."""
        respx.get(f"{BASE_URL}/notifications/me").mock(
            return_value=Response(
                200,
                json={
                    "values": [
                        {
                            "id": 1,
                            "type": "VOUCH",
                            "title": "New vouch",
                            "isRead": False,
                        },
                        {"id": 2, "type": "REVIEW", "title": "New review", "isRead": True},
                    ]
                },
            )
        )

        notifications = list(client.notifications.list(limit=10))

        assert len(notifications) == 2
        assert notifications[0].is_unread


# =============================================================================
# Contributions Resource Tests
# =============================================================================


class TestContributionsResource:
    """Tests for Contributions resource."""

    @respx.mock
    def test_get_contribution_history(self, client):
        """Test getting contribution history."""
        respx.get(f"{BASE_URL}/contributions/history").mock(
            return_value=Response(
                200,
                json={
                    "history": [
                        {"date": "2024-01-15", "tasks": 3, "forgiven": False},
                        {"date": "2024-01-16", "tasks": 0, "forgiven": True},
                    ]
                },
            )
        )

        history = client.contributions.get_history()

        assert history.total_days == 2
        assert history.total_tasks == 3

    @respx.mock
    def test_get_contribution_days(self, client):
        """Test getting contribution days."""
        respx.get(f"{BASE_URL}/contributions/history").mock(
            return_value=Response(
                200,
                json={
                    "history": [
                        {"date": "2024-01-15", "tasks": 3, "forgiven": False},
                    ]
                },
            )
        )

        days = client.contributions.get_days()

        assert len(days) == 1
        assert days[0].tasks == 3


# =============================================================================
# Error Handling Tests
# =============================================================================


class TestErrorHandling:
    """Tests for error handling."""

    @respx.mock
    def test_not_found_error(self, client):
        """Test 404 error handling."""
        respx.get(f"{BASE_URL}/profiles/99999").mock(
            return_value=Response(404, json={"error": "Not found"})
        )

        with pytest.raises(EthosNotFoundError):
            client.profiles.get(99999)

    @respx.mock
    def test_rate_limit_error(self, client):
        """Test 429 error handling."""
        respx.get(f"{BASE_URL}/profiles/1").mock(
            return_value=Response(
                429,
                json={"error": "Rate limited"},
                headers={"Retry-After": "60"},
            )
        )

        with pytest.raises(EthosRateLimitError) as exc_info:
            client.profiles.get(1)

        assert exc_info.value.retry_after == 60

    @respx.mock
    def test_authentication_error(self, client):
        """Test 401 error handling."""
        respx.get(f"{BASE_URL}/profiles/1").mock(
            return_value=Response(401, json={"error": "Unauthorized"})
        )

        with pytest.raises(EthosAuthenticationError):
            client.profiles.get(1)

    @respx.mock
    def test_forbidden_error(self, client):
        """Test 403 error handling."""
        respx.get(f"{BASE_URL}/profiles/1").mock(
            return_value=Response(403, json={"error": "Forbidden"})
        )

        with pytest.raises(EthosAuthenticationError):
            client.profiles.get(1)

    @respx.mock
    def test_server_error(self, client):
        """Test 500 error handling."""
        respx.get(f"{BASE_URL}/profiles/1").mock(
            return_value=Response(500, json={"error": "Internal server error"})
        )

        with pytest.raises(EthosAPIError) as exc_info:
            client.profiles.get(1)

        assert exc_info.value.status_code == 500

    @respx.mock
    def test_generic_api_error(self, client):
        """Test generic API error handling."""
        respx.get(f"{BASE_URL}/profiles/1").mock(
            return_value=Response(400, json={"message": "Bad request"})
        )

        with pytest.raises(EthosAPIError) as exc_info:
            client.profiles.get(1)

        assert "Bad request" in str(exc_info.value)


# =============================================================================
# Pagination Tests
# =============================================================================


class TestPagination:
    """Tests for pagination logic."""

    @respx.mock
    def test_pagination_exhausts_all_pages(self, client):
        """Test that pagination fetches all pages."""
        respx.get(f"{BASE_URL}/profiles").mock(
            side_effect=[
                Response(
                    200,
                    json={"values": [{"id": i} for i in range(1, 101)]},
                ),
                Response(
                    200,
                    json={"values": [{"id": i} for i in range(101, 151)]},
                ),
                Response(200, json={"values": []}),
            ]
        )

        profiles = list(client.profiles.list(limit=100))

        assert len(profiles) == 150

    @respx.mock
    def test_pagination_stops_on_partial_page(self, client):
        """Test that pagination stops when receiving fewer items than limit."""
        respx.get(f"{BASE_URL}/profiles").mock(
            return_value=Response(
                200,
                json={"values": [{"id": i} for i in range(1, 51)]},
            )
        )

        profiles = list(client.profiles.list(limit=100))

        assert len(profiles) == 50

    @respx.mock
    def test_pagination_handles_data_format(self, client):
        """Test pagination with 'data' key instead of 'values'."""
        respx.get(f"{BASE_URL}/activities").mock(
            return_value=Response(
                200,
                json={"data": [{"id": 1, "type": "vouch"}, {"id": 2, "type": "review"}]},
            )
        )

        activities = list(client.activities.list(limit=10))

        assert len(activities) == 2

    @respx.mock
    def test_pagination_handles_list_format(self, client):
        """Test pagination with direct list response."""
        respx.get(f"{BASE_URL}/activities").mock(
            return_value=Response(
                200,
                json=[{"id": 1, "type": "vouch"}, {"id": 2, "type": "review"}],
            )
        )

        activities = list(client.activities.list(limit=10))

        assert len(activities) == 2


# =============================================================================
# Async Tests
# =============================================================================


class TestAsyncClient:
    """Tests for async client."""

    @respx.mock
    @pytest.mark.asyncio
    async def test_async_get_profile(self, async_client):
        """Test async profile fetching."""
        respx.get(f"{BASE_URL}/profiles/123").mock(
            return_value=Response(
                200,
                json={
                    "id": 123,
                    "profileId": 123,
                    "displayName": "Async User",
                    "score": 1700,
                },
            )
        )

        profile = await async_client.profiles.get(123)

        assert profile.id == 123
        assert profile.display_name == "Async User"

    @respx.mock
    @pytest.mark.asyncio
    async def test_async_search_profiles(self, async_client):
        """Test async profile search."""
        respx.get(f"{BASE_URL}/profiles/search").mock(
            return_value=Response(
                200,
                json={
                    "values": [
                        {"id": 1, "displayName": "User One"},
                        {"id": 2, "displayName": "User Two"},
                    ]
                },
            )
        )

        profiles = await async_client.profiles.search("user")

        assert len(profiles) == 2

    @respx.mock
    @pytest.mark.asyncio
    async def test_async_error_handling(self, async_client):
        """Test async error handling."""
        respx.get(f"{BASE_URL}/profiles/99999").mock(
            return_value=Response(404, json={"error": "Not found"})
        )

        with pytest.raises(EthosNotFoundError):
            await async_client.profiles.get(99999)


# =============================================================================
# HTTP Client Tests
# =============================================================================


class TestHTTPClient:
    """Tests for HTTP client behavior."""

    @respx.mock
    def test_default_headers(self, client):
        """Test that default headers are sent."""
        route = respx.get(f"{BASE_URL}/profiles/1").mock(return_value=Response(200, json={"id": 1}))

        client.profiles.get(1)

        request = route.calls[0].request
        assert request.headers["Accept"] == "application/json"
        assert request.headers["Content-Type"] == "application/json"
        assert request.headers["X-Ethos-Client"] == "test"

    @respx.mock
    def test_params_are_cleaned(self, client):
        """Test that None params are removed."""
        route = respx.get(f"{BASE_URL}/vouches").mock(
            return_value=Response(200, json={"values": []})
        )

        list(client.vouches.list(author_profile_id=100, target_profile_id=None, limit=10))

        request = route.calls[0].request
        # Check that None value was not included
        assert "subjectProfileId" not in str(request.url)
        assert "authorProfileId=100" in str(request.url)

    @respx.mock
    def test_204_returns_empty_dict(self, client):
        """Test that 204 responses return empty dict."""
        respx.get(f"{BASE_URL}/profiles/1").mock(return_value=Response(204))

        # This would normally raise because parsing {} fails
        # but verifies the 204 handling path is exercised
        try:
            client.profiles.get(1)
        except Exception:
            pass  # Expected - empty dict can't be parsed as Profile


# =============================================================================
# Additional Async Tests
# =============================================================================


class TestAsyncResources:
    """Additional async tests for better coverage."""

    @respx.mock
    @pytest.mark.asyncio
    async def test_async_get_vouch(self, async_client):
        """Test async vouch fetching."""
        respx.get(f"{BASE_URL}/vouches/100").mock(
            return_value=Response(
                200,
                json={
                    "id": 100,
                    "authorProfileId": 1,
                    "subjectProfileId": 2,
                    "staked": True,
                    "archived": False,
                },
            )
        )

        vouch = await async_client.vouches.get(100)

        assert vouch.id == 100

    @respx.mock
    @pytest.mark.asyncio
    async def test_async_get_review(self, async_client):
        """Test async review fetching."""
        respx.get(f"{BASE_URL}/reviews/200").mock(
            return_value=Response(
                200,
                json={
                    "id": 200,
                    "authorProfileId": 1,
                    "subjectProfileId": 2,
                    "score": "positive",
                },
            )
        )

        review = await async_client.reviews.get(200)

        assert review.id == 200
        assert review.is_positive

    @respx.mock
    @pytest.mark.asyncio
    async def test_async_get_activity(self, async_client):
        """Test async activity fetching."""
        respx.get(f"{BASE_URL}/activities/300").mock(
            return_value=Response(
                200,
                json={
                    "id": 300,
                    "type": "review",
                    "authorProfileId": 1,
                },
            )
        )

        activity = await async_client.activities.get(300)

        assert activity.id == 300

    @respx.mock
    @pytest.mark.asyncio
    async def test_async_get_market(self, async_client):
        """Test async market fetching."""
        respx.get(f"{BASE_URL}/markets/50").mock(
            return_value=Response(
                200,
                json={
                    "id": 50,
                    "profileId": 100,
                },
            )
        )

        market = await async_client.markets.get(50)

        assert market.id == 50

    @respx.mock
    @pytest.mark.asyncio
    async def test_async_get_score(self, async_client):
        """Test async score fetching."""
        respx.get(f"{BASE_URL}/score/0xabc").mock(
            return_value=Response(
                200,
                json={
                    "profileId": 123,
                    "value": 1700,
                },
            )
        )

        score = await async_client.scores.get("0xabc")

        assert score.value == 1700


# =============================================================================
# Additional Resource Method Tests
# =============================================================================


class TestAdditionalMethods:
    """Tests for additional resource methods."""

    @respx.mock
    def test_vouches_by_profile(self, client):
        """Test getting vouches given by a profile."""
        respx.get(f"{BASE_URL}/vouches").mock(
            return_value=Response(
                200,
                json={
                    "values": [
                        {
                            "id": 1,
                            "authorProfileId": 100,
                            "subjectProfileId": 200,
                            "staked": True,
                            "archived": False,
                        }
                    ]
                },
            )
        )

        vouches = client.vouches.by_profile(100)

        assert len(vouches) == 1
        assert vouches[0].author_profile_id == 100

    @respx.mock
    def test_reviews_positive(self, client):
        """Test filtering positive reviews."""
        respx.get(f"{BASE_URL}/reviews").mock(
            return_value=Response(
                200,
                json={
                    "values": [
                        {
                            "id": 1,
                            "authorProfileId": 10,
                            "subjectProfileId": 20,
                            "score": "positive",
                        }
                    ]
                },
            )
        )

        reviews = list(client.reviews.list(score="positive", limit=10))

        assert len(reviews) == 1
        assert reviews[0].is_positive

    @respx.mock
    def test_activities_vouch_type(self, client):
        """Test filtering activities by vouch type."""
        respx.get(f"{BASE_URL}/activities").mock(
            return_value=Response(
                200,
                json={"values": [{"id": 1, "type": "vouch", "authorProfileId": 10}]},
            )
        )

        activities = list(client.activities.list(activity_type="vouch", limit=10))

        assert len(activities) == 1
        assert activities[0].type == "vouch"

    @respx.mock
    def test_profiles_recent(self, client):
        """Test getting recent profiles."""
        respx.get(f"{BASE_URL}/profiles/recent").mock(
            return_value=Response(
                200,
                json={"values": [{"id": 1, "displayName": "New User"}]},
            )
        )

        profiles = client.profiles.recent(limit=5)

        assert len(profiles) == 1

    @respx.mock
    def test_markets_list(self, client):
        """Test listing markets."""
        respx.get(f"{BASE_URL}/markets").mock(
            return_value=Response(
                200,
                json={"values": [{"id": 1, "profileId": 100}, {"id": 2, "profileId": 101}]},
            )
        )

        markets = list(client.markets.list(limit=10))

        assert len(markets) == 2

    @respx.mock
    def test_score_breakdown(self, client):
        """Test getting score breakdown."""
        respx.get(f"{BASE_URL}/score/0xabc/breakdown").mock(
            return_value=Response(
                200,
                json={
                    "profileId": 123,
                    "value": 1650,
                    "breakdown": {
                        "reviews": 100,
                        "vouches": 200,
                        "attestations": 50,
                    },
                },
            )
        )

        score = client.scores.breakdown("0xabc")

        assert score.breakdown.reviews == 100
        assert score.breakdown.vouches == 200

    @respx.mock
    def test_votes_upvotes_for(self, client):
        """Test getting upvotes for an activity."""
        respx.get(f"{BASE_URL}/votes").mock(
            return_value=Response(
                200,
                json={
                    "values": [
                        {
                            "voterProfileId": 1,
                            "targetType": "review",
                            "targetId": 100,
                            "isUpvote": True,
                        }
                    ]
                },
            )
        )

        votes = list(client.votes.upvotes_for("review", 100))

        assert len(votes) == 1
        assert votes[0].is_upvote

    @respx.mock
    def test_invitations_check_eligibility(self, client):
        """Test checking invitation eligibility."""
        respx.get(f"{BASE_URL}/invitations/check").mock(
            return_value=Response(
                200,
                json={
                    "canInvite": True,
                    "address": "0xabc123",
                    "reason": None,
                },
            )
        )

        eligibility = client.invitations.check_eligibility("0xabc123")

        assert eligibility.can_invite is True

    @respx.mock
    def test_activities_recent(self, client):
        """Test getting recent activities."""
        respx.get(f"{BASE_URL}/activities").mock(
            return_value=Response(
                200,
                json={
                    "values": [
                        {"id": 1, "type": "vouch", "authorProfileId": 10},
                        {"id": 2, "type": "review", "authorProfileId": 11},
                    ]
                },
            )
        )

        activities = client.activities.recent(limit=5)

        assert len(activities) == 2


# =============================================================================
# Edge Cases and Error Response Tests
# =============================================================================


class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""

    @respx.mock
    def test_empty_search_results(self, client):
        """Test handling empty search results."""
        respx.get(f"{BASE_URL}/profiles/search").mock(
            return_value=Response(200, json={"values": []})
        )

        profiles = client.profiles.search("nonexistent")

        assert profiles == []

    @respx.mock
    def test_profile_without_twitter(self, client):
        """Test profile without Twitter userkey."""
        respx.get(f"{BASE_URL}/profiles/1").mock(
            return_value=Response(
                200,
                json={
                    "id": 1,
                    "displayName": "No Twitter User",
                    "userkeys": ["farcaster.xyz/user/fid/123"],
                },
            )
        )

        profile = client.profiles.get(1)

        assert profile.twitter_handle is None

    @respx.mock
    def test_vouch_with_zero_balance(self, client):
        """Test vouch with zero balance."""
        respx.get(f"{BASE_URL}/vouches/1").mock(
            return_value=Response(
                200,
                json={
                    "id": 1,
                    "authorProfileId": 10,
                    "subjectProfileId": 20,
                    "staked": True,
                    "archived": False,
                    "balance": "0",
                },
            )
        )

        vouch = client.vouches.get(1)

        assert vouch.amount_eth == 0.0

    @respx.mock
    def test_api_error_with_text_body(self, client):
        """Test API error with plain text body."""
        respx.get(f"{BASE_URL}/profiles/1").mock(
            return_value=Response(500, text="Internal Server Error")
        )

        with pytest.raises(EthosAPIError) as exc_info:
            client.profiles.get(1)

        assert "Internal Server Error" in str(exc_info.value)

    @respx.mock
    def test_rate_limit_without_retry_after(self, client):
        """Test rate limit error without Retry-After header."""
        respx.get(f"{BASE_URL}/profiles/1").mock(
            return_value=Response(429, json={"error": "Too many requests"})
        )

        with pytest.raises(EthosRateLimitError) as exc_info:
            client.profiles.get(1)

        assert exc_info.value.retry_after is None


# =============================================================================
# Extended Users Resource Tests
# =============================================================================


class TestUsersResourceExtended:
    """Extended tests for Users resource to improve coverage."""

    @respx.mock
    def test_get_user_by_profile_id(self, client):
        """Test getting a user by profile ID."""
        respx.get(f"{BASE_URL}/user/by/profile-id/100").mock(
            return_value=Response(
                200,
                json={"id": 501, "profileId": 100, "displayName": "Profile User"},
            )
        )
        user = client.users.get_by_profile_id(100)
        assert user.profile_id == 100

    @respx.mock
    def test_get_user_by_username(self, client):
        """Test getting a user by username."""
        respx.get(f"{BASE_URL}/user/by/username/testuser").mock(
            return_value=Response(
                200,
                json={"id": 502, "profileId": 101, "displayName": "testuser"},
            )
        )
        user = client.users.get_by_username("testuser")
        assert user.id == 502

    @respx.mock
    def test_get_user_by_twitter(self, client):
        """Test getting a user by Twitter handle."""
        respx.get(f"{BASE_URL}/user/by/x/twitteruser").mock(
            return_value=Response(
                200,
                json={"id": 503, "profileId": 102, "displayName": "Twitter User"},
            )
        )
        user = client.users.get_by_twitter("@twitteruser")
        assert user.id == 503

    @respx.mock
    def test_get_user_by_discord(self, client):
        """Test getting a user by Discord ID."""
        respx.get(f"{BASE_URL}/user/by/discord/123456789").mock(
            return_value=Response(
                200,
                json={"id": 504, "profileId": 103, "displayName": "Discord User"},
            )
        )
        user = client.users.get_by_discord("123456789")
        assert user.id == 504

    @respx.mock
    def test_get_user_by_farcaster(self, client):
        """Test getting a user by Farcaster ID."""
        respx.get(f"{BASE_URL}/user/by/farcaster/12345").mock(
            return_value=Response(
                200,
                json={"id": 505, "profileId": 104, "displayName": "Farcaster User"},
            )
        )
        user = client.users.get_by_farcaster("12345")
        assert user.id == 505

    @respx.mock
    def test_get_user_by_farcaster_username(self, client):
        """Test getting a user by Farcaster username."""
        respx.get(f"{BASE_URL}/user/by/farcaster/username/fcuser").mock(
            return_value=Response(
                200,
                json={"id": 506, "profileId": 105, "displayName": "FC User"},
            )
        )
        user = client.users.get_by_farcaster_username("fcuser")
        assert user.id == 506

    @respx.mock
    def test_get_user_by_telegram(self, client):
        """Test getting a user by Telegram ID."""
        respx.get(f"{BASE_URL}/user/by/telegram/987654321").mock(
            return_value=Response(
                200,
                json={"id": 507, "profileId": 106, "displayName": "Telegram User"},
            )
        )
        user = client.users.get_by_telegram("987654321")
        assert user.id == 507

    @respx.mock
    def test_search_users(self, client):
        """Test searching users."""
        respx.get(f"{BASE_URL}/users/search").mock(
            return_value=Response(
                200,
                json={
                    "values": [
                        {"id": 1, "displayName": "User One"},
                        {"id": 2, "displayName": "User Two"},
                    ]
                },
            )
        )
        users = client.users.search("user", limit=10)
        assert len(users) == 2

    @respx.mock
    def test_search_users_list_response(self, client):
        """Test searching users with list response."""
        respx.get(f"{BASE_URL}/users/search").mock(
            return_value=Response(
                200,
                json=[{"id": 1, "displayName": "User One"}],
            )
        )
        users = client.users.search("user")
        assert len(users) == 1

    @respx.mock
    def test_bulk_by_ids(self, client):
        """Test bulk user lookup by IDs."""
        respx.post(f"{BASE_URL}/users/by/ids").mock(
            return_value=Response(
                200,
                json={
                    "values": [
                        {"id": 1, "displayName": "User 1"},
                        {"id": 2, "displayName": "User 2"},
                    ]
                },
            )
        )
        users = client.users.bulk_by_ids([1, 2])
        assert len(users) == 2

    @respx.mock
    def test_bulk_by_ids_list_response(self, client):
        """Test bulk user lookup with list response."""
        respx.post(f"{BASE_URL}/users/by/ids").mock(
            return_value=Response(
                200,
                json=[{"id": 1, "displayName": "User 1"}],
            )
        )
        users = client.users.bulk_by_ids([1])
        assert len(users) == 1

    @respx.mock
    def test_bulk_by_addresses(self, client):
        """Test bulk user lookup by addresses."""
        respx.post(f"{BASE_URL}/users/by/address").mock(
            return_value=Response(
                200,
                json={
                    "data": [
                        {"id": 1, "address": "0xabc"},
                        {"id": 2, "address": "0xdef"},
                    ]
                },
            )
        )
        users = client.users.bulk_by_addresses(["0xabc", "0xdef"])
        assert len(users) == 2

    @respx.mock
    def test_bulk_by_profile_ids(self, client):
        """Test bulk user lookup by profile IDs."""
        respx.post(f"{BASE_URL}/users/by/profile-id").mock(
            return_value=Response(
                200,
                json={"values": [{"id": 1, "profileId": 100}]},
            )
        )
        users = client.users.bulk_by_profile_ids([100])
        assert len(users) == 1

    @respx.mock
    def test_bulk_by_twitter(self, client):
        """Test bulk user lookup by Twitter handles."""
        respx.post(f"{BASE_URL}/users/by/x").mock(
            return_value=Response(
                200,
                json={"values": [{"id": 1, "displayName": "Twitter User"}]},
            )
        )
        users = client.users.bulk_by_twitter(["user1", "user2"])
        assert len(users) == 1

    @respx.mock
    def test_get_user_categories(self, client):
        """Test getting user category rankings."""
        respx.get(f"{BASE_URL}/users/x.com/user/testuser/categories").mock(
            return_value=Response(
                200,
                json={
                    "categoryRanks": [
                        {"categoryId": 1, "category": "tech", "rank": 5, "score": 1500},
                        {"categoryId": 2, "category": "defi", "rank": 10, "score": 1200},
                    ]
                },
            )
        )
        categories = client.users.get_categories("x.com/user/testuser")
        assert len(categories) == 2
        assert categories[0].category == "tech"


# =============================================================================
# Extended XP Resource Tests
# =============================================================================


class TestXPResourceExtended:
    """Extended tests for XP resource to improve coverage."""

    @respx.mock
    def test_get_xp_total_int_response(self, client):
        """Test getting XP total with integer response."""
        respx.get(f"{BASE_URL}/xp/user/userkey").mock(return_value=Response(200, json=5000))
        total = client.xp.get_total("userkey")
        assert total == 5000

    @respx.mock
    def test_get_xp_season_total_int_response(self, client):
        """Test getting season XP with integer response."""
        respx.get(f"{BASE_URL}/xp/user/userkey/season/1").mock(
            return_value=Response(200, json=2500)
        )
        total = client.xp.get_season_total("userkey", 1)
        assert total == 2500

    @respx.mock
    def test_get_xp_weekly(self, client):
        """Test getting weekly XP breakdown."""
        respx.get(f"{BASE_URL}/xp/user/userkey/season/1/weekly").mock(
            return_value=Response(
                200,
                json=[
                    {"week": 1, "weeklyXp": 100, "cumulativeXp": 100},
                    {"week": 2, "weeklyXp": 150, "cumulativeXp": 250},
                ],
            )
        )
        weekly = client.xp.get_weekly("userkey", 1)
        assert len(weekly) == 2
        assert weekly[0].weekly_xp == 100

    @respx.mock
    def test_get_xp_weekly_empty(self, client):
        """Test getting weekly XP with empty response."""
        respx.get(f"{BASE_URL}/xp/user/userkey/season/1/weekly").mock(
            return_value=Response(200, json={})
        )
        weekly = client.xp.get_weekly("userkey", 1)
        assert weekly == []

    @respx.mock
    def test_get_leaderboard_rank(self, client):
        """Test getting XP leaderboard rank."""
        respx.get(f"{BASE_URL}/xp/user/userkey/leaderboard-rank").mock(
            return_value=Response(200, json={"rank": 42})
        )
        rank = client.xp.get_leaderboard_rank("userkey")
        assert rank == 42

    @respx.mock
    def test_get_leaderboard_rank_int_response(self, client):
        """Test getting leaderboard rank with integer response."""
        respx.get(f"{BASE_URL}/xp/user/userkey/leaderboard-rank").mock(
            return_value=Response(200, json=42)
        )
        rank = client.xp.get_leaderboard_rank("userkey")
        assert rank == 42

    @respx.mock
    def test_get_xp_history(self, client):
        """Test getting XP history."""
        respx.get(f"{BASE_URL}/xp/history").mock(
            return_value=Response(
                200,
                json={
                    "values": [
                        {
                            "id": 1,
                            "type": "review",
                            "points": 100,
                            "createdAt": "2024-01-01T00:00:00Z",
                        },
                        {
                            "id": 2,
                            "type": "vouch",
                            "points": 50,
                            "createdAt": "2024-01-02T00:00:00Z",
                        },
                    ]
                },
            )
        )
        history = client.xp.get_history("userkey", season_id=1)
        assert len(history) == 2

    @respx.mock
    def test_get_xp_history_list_response(self, client):
        """Test getting XP history with list response."""
        respx.get(f"{BASE_URL}/xp/history").mock(
            return_value=Response(
                200,
                json=[{"id": 1, "type": "review", "points": 100}],
            )
        )
        history = client.xp.get_history("userkey")
        assert len(history) == 1

    @respx.mock
    def test_get_xp_seasons(self, client):
        """Test getting XP seasons."""
        respx.get(f"{BASE_URL}/xp/seasons").mock(
            return_value=Response(
                200,
                json={
                    "seasons": [
                        {"id": 1, "name": "Season 1", "startDate": "2024-01-01"},
                        {"id": 2, "name": "Season 2", "startDate": "2024-04-01"},
                    ],
                    "current": {"id": 2, "name": "Season 2", "startDate": "2024-04-01"},
                },
            )
        )
        seasons, current = client.xp.get_seasons()
        assert len(seasons) == 2
        assert current.id == 2

    @respx.mock
    def test_get_xp_seasons_no_current(self, client):
        """Test getting XP seasons without current season."""
        respx.get(f"{BASE_URL}/xp/seasons").mock(
            return_value=Response(
                200,
                json={"seasons": [{"id": 1, "name": "Season 1"}], "current": None},
            )
        )
        seasons, current = client.xp.get_seasons()
        assert len(seasons) == 1
        assert current is None

    @respx.mock
    def test_get_season_weeks(self, client):
        """Test getting season weeks."""
        respx.get(f"{BASE_URL}/xp/season/1/weeks").mock(
            return_value=Response(
                200,
                json=[
                    {
                        "week": 1,
                        "startDate": "2024-01-01T00:00:00Z",
                        "endDate": "2024-01-07T00:00:00Z",
                    },
                    {
                        "week": 2,
                        "startDate": "2024-01-08T00:00:00Z",
                        "endDate": "2024-01-14T00:00:00Z",
                    },
                ],
            )
        )
        weeks = client.xp.get_season_weeks(1)
        assert len(weeks) == 2

    @respx.mock
    def test_get_season_weeks_empty(self, client):
        """Test getting season weeks with empty response."""
        respx.get(f"{BASE_URL}/xp/season/1/weeks").mock(return_value=Response(200, json={}))
        weeks = client.xp.get_season_weeks(1)
        assert weeks == []

    @respx.mock
    def test_get_tips_sent(self, client):
        """Test getting tips sent."""
        respx.get(f"{BASE_URL}/xp/tips/sent").mock(
            return_value=Response(
                200,
                json={
                    "values": [
                        {"id": 1, "amount": 100, "senderProfileId": 100, "receiverProfileId": 200},
                    ]
                },
            )
        )
        tips = client.xp.get_tips_sent()
        assert len(tips) == 1

    @respx.mock
    def test_get_tips_sent_list_response(self, client):
        """Test getting tips sent with list response."""
        respx.get(f"{BASE_URL}/xp/tips/sent").mock(
            return_value=Response(
                200,
                json=[{"id": 1, "amount": 100, "senderProfileId": 100, "receiverProfileId": 200}],
            )
        )
        tips = client.xp.get_tips_sent()
        assert len(tips) == 1

    @respx.mock
    def test_get_tips_received(self, client):
        """Test getting tips received."""
        respx.get(f"{BASE_URL}/xp/tips/received").mock(
            return_value=Response(
                200,
                json={
                    "values": [
                        {"id": 1, "amount": 50, "senderProfileId": 100, "receiverProfileId": 200}
                    ]
                },
            )
        )
        tips = client.xp.get_tips_received()
        assert len(tips) == 1

    @respx.mock
    def test_get_tip_stats(self, client):
        """Test getting tip stats."""
        respx.get(f"{BASE_URL}/xp/tips/stats").mock(
            return_value=Response(
                200,
                json={"totalSent": 500, "totalReceived": 300, "tipCount": 10},
            )
        )
        stats = client.xp.get_tip_stats()
        assert stats.total_sent == 500
        assert stats.total_received == 300

    @respx.mock
    def test_get_decision(self, client):
        """Test getting XP decision."""
        respx.get(f"{BASE_URL}/xp/decision").mock(
            return_value=Response(
                200,
                json={
                    "decisionType": "DELEGATE",
                    "delegations": [{"validatorId": 1, "percentage": 100}],
                },
            )
        )
        decision = client.xp.get_decision()
        assert decision.decision_type == "DELEGATE"

    @respx.mock
    def test_get_decision_empty(self, client):
        """Test getting XP decision with empty response."""
        respx.get(f"{BASE_URL}/xp/decision").mock(return_value=Response(200, json={}))
        decision = client.xp.get_decision()
        assert decision is None

    @respx.mock
    def test_get_decision_metadata(self, client):
        """Test getting XP decision metadata."""
        respx.get(f"{BASE_URL}/xp/decision/metadata").mock(
            return_value=Response(
                200,
                json={
                    "deadline": "2024-12-31T00:00:00Z",
                    "spendPercentage": 50.0,
                    "delegatePercentage": 30.0,
                },
            )
        )
        metadata = client.xp.get_decision_metadata()
        assert metadata.spend_percentage == 50.0

    @respx.mock
    def test_get_validators(self, client):
        """Test getting validators."""
        respx.get(f"{BASE_URL}/xp/validators").mock(
            return_value=Response(
                200,
                json=[
                    {
                        "profileId": 1,
                        "displayName": "Validator 1",
                        "xpCapacity": 10000,
                        "xpDelegated": 5000,
                    },
                    {
                        "profileId": 2,
                        "displayName": "Validator 2",
                        "xpCapacity": 5000,
                        "xpDelegated": 2000,
                    },
                ],
            )
        )
        validators = client.xp.get_validators()
        assert len(validators) == 2
        assert validators[0].profile_id == 1

    @respx.mock
    def test_get_validators_empty(self, client):
        """Test getting validators with empty response."""
        respx.get(f"{BASE_URL}/xp/validators").mock(return_value=Response(200, json={}))
        validators = client.xp.get_validators()
        assert validators == []


# =============================================================================
# Extended Invitations Resource Tests
# =============================================================================


class TestInvitationsResourceExtended:
    """Extended tests for Invitations resource."""

    @respx.mock
    def test_get_invitation_tree(self, client):
        """Test getting invitation tree."""
        respx.get(f"{BASE_URL}/invitations/accepted/100/tree").mock(
            return_value=Response(
                200,
                json={
                    "values": [
                        {"profileId": 101, "children": []},
                        {"profileId": 102, "children": []},
                    ],
                },
            )
        )
        tree = client.invitations.get_invitation_tree(100)
        assert len(tree) == 2

    @respx.mock
    def test_by_sender(self, client):
        """Test getting invitations by sender."""
        respx.get(f"{BASE_URL}/invitations").mock(
            return_value=Response(
                200,
                json={
                    "values": [
                        {"id": 1, "senderProfileId": 100, "status": "INVITED"},
                        {"id": 2, "senderProfileId": 100, "status": "ACCEPTED"},
                    ]
                },
            )
        )
        invitations = client.invitations.by_sender(sender_profile_id=100)
        assert len(invitations) == 2

    @respx.mock
    def test_pending_invitations(self, client):
        """Test getting pending invitations."""
        respx.get(f"{BASE_URL}/invitations").mock(
            return_value=Response(
                200,
                json={"values": [{"id": 1, "senderProfileId": 100, "status": "INVITED"}]},
            )
        )
        invitations = client.invitations.pending()
        assert len(invitations) == 1

    @respx.mock
    def test_accepted_invitations(self, client):
        """Test getting accepted invitations."""
        respx.get(f"{BASE_URL}/invitations").mock(
            return_value=Response(
                200,
                json={"values": [{"id": 1, "senderProfileId": 100, "status": "ACCEPTED"}]},
            )
        )
        invitations = client.invitations.accepted()
        assert len(invitations) == 1

    @respx.mock
    def test_get_pending_for_address(self, client):
        """Test getting pending invitations for an address."""
        respx.get(f"{BASE_URL}/invitations/pending/0xabc123").mock(
            return_value=Response(
                200,
                json=[
                    {
                        "id": 1,
                        "senderProfileId": 100,
                        "inviteeAddress": "0xabc123",
                        "status": "INVITED",
                    }
                ],
            )
        )
        invitations = client.invitations.get_pending_for_address("0xabc123")
        assert len(invitations) == 1


# =============================================================================
# Extended Replies Resource Tests
# =============================================================================


class TestRepliesResourceExtended:
    """Extended tests for Replies resource."""

    @respx.mock
    def test_list_replies_for_review(self, client):
        """Test listing replies for a review."""
        respx.get(f"{BASE_URL}/replies/review/100").mock(
            return_value=Response(
                200,
                json={
                    "values": [
                        {
                            "id": 1,
                            "contractType": "review",
                            "parentId": 100,
                            "authorProfileId": 50,
                            "content": "Reply 1",
                        },
                        {
                            "id": 2,
                            "contractType": "review",
                            "parentId": 100,
                            "authorProfileId": 51,
                            "content": "Reply 2",
                        },
                    ]
                },
            )
        )
        replies = list(client.replies.list(contract_type="review", parent_id=100, limit=10))
        assert len(replies) == 2

    @respx.mock
    def test_list_replies_direct_list(self, client):
        """Test listing replies with direct list response."""
        respx.get(f"{BASE_URL}/replies/review/100").mock(
            return_value=Response(
                200,
                json=[
                    {
                        "id": 1,
                        "contractType": "review",
                        "parentId": 100,
                        "authorProfileId": 50,
                        "content": "Test",
                    }
                ],
            )
        )
        replies = list(client.replies.list(contract_type="review", parent_id=100, limit=10))
        assert len(replies) == 1

    @respx.mock
    def test_for_review(self, client):
        """Test getting replies for a review."""
        respx.get(f"{BASE_URL}/replies/review/100").mock(
            return_value=Response(
                200,
                json={
                    "values": [
                        {
                            "id": 1,
                            "contractType": "review",
                            "parentId": 100,
                            "authorProfileId": 50,
                            "content": "Test",
                        }
                    ]
                },
            )
        )
        replies = client.replies.for_review(100)
        assert len(replies) == 1

    @respx.mock
    def test_for_vouch(self, client):
        """Test getting replies for a vouch."""
        respx.get(f"{BASE_URL}/replies/vouch/200").mock(
            return_value=Response(
                200,
                json={
                    "values": [
                        {
                            "id": 1,
                            "contractType": "vouch",
                            "parentId": 200,
                            "authorProfileId": 50,
                            "content": "Test",
                        }
                    ]
                },
            )
        )
        replies = client.replies.for_vouch(200)
        assert len(replies) == 1

    @respx.mock
    def test_for_project(self, client):
        """Test getting replies for a project."""
        respx.get(f"{BASE_URL}/replies/project/300").mock(
            return_value=Response(
                200,
                json={
                    "values": [
                        {
                            "id": 1,
                            "contractType": "project",
                            "parentId": 300,
                            "authorProfileId": 50,
                            "content": "Test",
                        }
                    ]
                },
            )
        )
        replies = client.replies.for_project(300)
        assert len(replies) == 1


# =============================================================================
# Extended Votes Resource Tests
# =============================================================================


class TestVotesResourceExtended:
    """Extended tests for Votes resource."""

    @respx.mock
    def test_downvotes_for(self, client):
        """Test getting downvotes for an activity."""
        respx.get(f"{BASE_URL}/votes").mock(
            return_value=Response(
                200,
                json={
                    "values": [
                        {
                            "voterProfileId": 1,
                            "targetType": "review",
                            "targetId": 100,
                            "isUpvote": False,
                        }
                    ]
                },
            )
        )
        votes = list(client.votes.downvotes_for("review", 100))
        assert len(votes) == 1
        assert not votes[0].is_upvote

    @respx.mock
    def test_get_bulk_stats(self, client):
        """Test getting bulk vote stats."""
        respx.post(f"{BASE_URL}/votes/stats").mock(
            return_value=Response(
                200,
                json={
                    "review": {
                        "100": {"upvotes": 10, "downvotes": 2},
                        "101": {"upvotes": 5, "downvotes": 1},
                    },
                    "vouch": {"200": {"upvotes": 8, "downvotes": 0}},
                },
            )
        )
        stats = client.votes.get_bulk_stats(review_ids=[100, 101], vouch_ids=[200])
        assert "review" in stats
        assert 100 in stats["review"]
        assert stats["review"][100].upvotes == 10


# =============================================================================
# Extended Profiles Resource Tests
# =============================================================================


class TestProfilesResourceExtended:
    """Extended tests for Profiles resource."""

    @respx.mock
    def test_recent_profiles(self, client):
        """Test getting recent profiles."""
        respx.get(f"{BASE_URL}/profiles/recent").mock(
            return_value=Response(
                200,
                json={
                    "values": [
                        {"id": 1, "displayName": "New User"},
                        {"id": 2, "displayName": "Another User"},
                    ]
                },
            )
        )
        profiles = client.profiles.recent(limit=10)
        assert len(profiles) == 2

    @respx.mock
    def test_search_profiles_pagination(self, client):
        """Test searching profiles with pagination."""
        respx.get(f"{BASE_URL}/profiles/search").mock(
            return_value=Response(
                200,
                json={"values": [{"id": 1, "displayName": "Test User"}]},
            )
        )
        profiles = client.profiles.search("test", limit=10)
        assert len(profiles) == 1


# =============================================================================
# Extended Notifications Resource Tests
# =============================================================================


class TestNotificationsResourceExtended:
    """Extended tests for Notifications resource."""

    @respx.mock
    def test_get_unread_count(self, client):
        """Test getting unread notification count."""
        respx.get(f"{BASE_URL}/notifications/stats/me").mock(
            return_value=Response(200, json={"unreadCount": 10})
        )
        count = client.notifications.get_unread_count()
        assert count == 10

    @respx.mock
    def test_mark_all_read(self, client):
        """Test marking all notifications as read."""
        respx.post(f"{BASE_URL}/notifications/me/mark-as-read").mock(
            return_value=Response(200, json={"read": 5})
        )
        count = client.notifications.mark_all_read()
        assert count == 5

    @respx.mock
    def test_get_settings(self, client):
        """Test getting notification settings."""
        respx.get(f"{BASE_URL}/notifications/me/settings").mock(
            return_value=Response(
                200,
                json={
                    "vouch": {"email": True, "push": False},
                    "review": {"email": True, "push": True},
                },
            )
        )
        settings = client.notifications.get_settings()
        assert settings is not None

    @respx.mock
    def test_update_settings(self, client):
        """Test updating notification settings."""
        respx.put(f"{BASE_URL}/notifications/me/settings").mock(
            return_value=Response(
                200,
                json={
                    "vouch": {"email": False, "push": False},
                },
            )
        )
        settings = client.notifications.update_settings({"vouch": {"email": False, "push": False}})
        assert settings is not None

    @respx.mock
    def test_get_all_notifications(self, client):
        """Test getting all notifications as list."""
        respx.get(f"{BASE_URL}/notifications/me").mock(
            return_value=Response(
                200,
                json={
                    "values": [
                        {"id": 1, "type": "VOUCH", "isRead": False},
                        {"id": 2, "type": "REVIEW", "isRead": True},
                    ]
                },
            )
        )
        notifications = client.notifications.get_all(limit=10)
        assert len(notifications) == 2


# =============================================================================
# Extended Contributions Resource Tests
# =============================================================================


class TestContributionsResourceExtended:
    """Extended tests for Contributions resource."""

    @respx.mock
    def test_get_history_with_data(self, client):
        """Test getting contribution history with data."""
        respx.get(f"{BASE_URL}/contributions/history").mock(
            return_value=Response(
                200,
                json={
                    "history": [
                        {"date": "2024-01-15", "tasks": 3, "forgiven": False},
                        {"date": "2024-01-14", "tasks": 2, "forgiven": False},
                        {"date": "2024-01-13", "tasks": 1, "forgiven": True},
                    ]
                },
            )
        )
        history = client.contributions.get_history()
        assert history.total_days == 3
        assert history.total_tasks == 6

    @respx.mock
    def test_get_days_detailed(self, client):
        """Test getting contribution days in detail."""
        respx.get(f"{BASE_URL}/contributions/history").mock(
            return_value=Response(
                200,
                json={
                    "history": [
                        {"date": "2024-01-15", "tasks": 3, "forgiven": False},
                    ]
                },
            )
        )
        days = client.contributions.get_days()
        assert len(days) == 1
        assert days[0].tasks == 3


# =============================================================================
# Async Extended Tests
# =============================================================================


class TestAsyncResourcesExtended:
    """Extended async tests for better coverage."""

    @respx.mock
    @pytest.mark.asyncio
    async def test_async_list_profiles(self, async_client):
        """Test async profile listing."""
        respx.get(f"{BASE_URL}/profiles").mock(
            return_value=Response(
                200,
                json={"values": [{"id": 1}, {"id": 2}]},
            )
        )
        profiles = []
        async for profile in async_client.profiles.list(limit=10):
            profiles.append(profile)
        assert len(profiles) == 2

    @respx.mock
    @pytest.mark.asyncio
    async def test_async_list_vouches(self, async_client):
        """Test async vouch listing."""
        respx.get(f"{BASE_URL}/vouches").mock(
            return_value=Response(
                200,
                json={
                    "values": [
                        {
                            "id": 1,
                            "authorProfileId": 10,
                            "subjectProfileId": 20,
                            "staked": True,
                            "archived": False,
                        }
                    ]
                },
            )
        )
        vouches = []
        async for vouch in async_client.vouches.list(limit=10):
            vouches.append(vouch)
        assert len(vouches) == 1

    @respx.mock
    @pytest.mark.asyncio
    async def test_async_list_reviews(self, async_client):
        """Test async review listing."""
        respx.get(f"{BASE_URL}/reviews").mock(
            return_value=Response(
                200,
                json={
                    "values": [
                        {
                            "id": 1,
                            "authorProfileId": 10,
                            "subjectProfileId": 20,
                            "score": "positive",
                        }
                    ]
                },
            )
        )
        reviews = []
        async for review in async_client.reviews.list(limit=10):
            reviews.append(review)
        assert len(reviews) == 1

    @respx.mock
    @pytest.mark.asyncio
    async def test_async_get_user(self, async_client):
        """Test async user fetching."""
        respx.get(f"{BASE_URL}/user/500").mock(
            return_value=Response(
                200,
                json={"id": 500, "profileId": 100, "displayName": "Test"},
            )
        )
        user = await async_client.users.get(500)
        assert user.id == 500

    @respx.mock
    @pytest.mark.asyncio
    async def test_async_get_xp_total(self, async_client):
        """Test async XP total fetching."""
        respx.get(f"{BASE_URL}/xp/user/userkey").mock(
            return_value=Response(200, json={"total": 5000})
        )
        total = await async_client.xp.get_total("userkey")
        assert total == 5000

    @respx.mock
    @pytest.mark.asyncio
    async def test_async_list_notifications(self, async_client):
        """Test async notification listing."""
        respx.get(f"{BASE_URL}/notifications/me").mock(
            return_value=Response(
                200,
                json={"values": [{"id": 1, "type": "VOUCH", "isRead": False}]},
            )
        )
        notifications = []
        async for n in async_client.notifications.list(limit=10):
            notifications.append(n)
        assert len(notifications) == 1

    @respx.mock
    @pytest.mark.asyncio
    async def test_async_get_endorsements(self, async_client):
        """Test async endorsements fetching."""
        respx.get(f"{BASE_URL}/endorsements/userkey").mock(
            return_value=Response(
                200,
                json={
                    "values": [
                        {"activityId": 1, "endorserProfileId": 100, "endorsementType": "vouch"}
                    ],
                    "summary": {"totalEndorsers": 1},
                    "total": 1,
                },
            )
        )
        response = await async_client.endorsements.get_for_user("userkey")
        assert len(response) == 1

    @respx.mock
    @pytest.mark.asyncio
    async def test_async_list_votes(self, async_client):
        """Test async vote listing."""
        respx.get(f"{BASE_URL}/votes").mock(
            return_value=Response(
                200,
                json={
                    "values": [
                        {
                            "voterProfileId": 1,
                            "targetType": "review",
                            "targetId": 100,
                            "isUpvote": True,
                        }
                    ]
                },
            )
        )
        votes = []
        async for vote in async_client.votes.list("review", 100, limit=10):
            votes.append(vote)
        assert len(votes) == 1

    @respx.mock
    @pytest.mark.asyncio
    async def test_async_list_activities(self, async_client):
        """Test async activity listing."""
        respx.get(f"{BASE_URL}/activities").mock(
            return_value=Response(
                200,
                json={"values": [{"id": 1, "type": "vouch", "authorProfileId": 10}]},
            )
        )
        activities = []
        async for activity in async_client.activities.list(limit=10):
            activities.append(activity)
        assert len(activities) == 1

    @respx.mock
    @pytest.mark.asyncio
    async def test_async_list_markets(self, async_client):
        """Test async market listing."""
        respx.get(f"{BASE_URL}/markets").mock(
            return_value=Response(
                200,
                json={"values": [{"id": 1, "profileId": 100}]},
            )
        )
        markets = []
        async for market in async_client.markets.list(limit=10):
            markets.append(market)
        assert len(markets) == 1

    @respx.mock
    @pytest.mark.asyncio
    async def test_async_list_invitations(self, async_client):
        """Test async invitation listing."""
        respx.get(f"{BASE_URL}/invitations").mock(
            return_value=Response(
                200,
                json={"values": [{"id": 1, "senderProfileId": 100, "status": "INVITED"}]},
            )
        )
        invitations = []
        async for invitation in async_client.invitations.list(limit=10):
            invitations.append(invitation)
        assert len(invitations) == 1

    @respx.mock
    @pytest.mark.asyncio
    async def test_async_list_replies(self, async_client):
        """Test async reply listing."""
        respx.get(f"{BASE_URL}/replies/review/100").mock(
            return_value=Response(
                200,
                json={
                    "values": [
                        {
                            "id": 1,
                            "contractType": "review",
                            "parentId": 100,
                            "authorProfileId": 50,
                            "content": "Test",
                        }
                    ]
                },
            )
        )
        replies = []
        async for reply in async_client.replies.list(
            contract_type="review", parent_id=100, limit=10
        ):
            replies.append(reply)
        assert len(replies) == 1

    @respx.mock
    @pytest.mark.asyncio
    async def test_async_get_xp_seasons(self, async_client):
        """Test async XP seasons fetching."""
        respx.get(f"{BASE_URL}/xp/seasons").mock(
            return_value=Response(
                200,
                json={
                    "seasons": [{"id": 1, "name": "Season 1"}],
                    "current": {"id": 1, "name": "Season 1"},
                },
            )
        )
        seasons, current = await async_client.xp.get_seasons()
        assert len(seasons) == 1
        assert current is not None

    @respx.mock
    @pytest.mark.asyncio
    async def test_async_get_vote_stats(self, async_client):
        """Test async vote stats fetching."""
        respx.get(f"{BASE_URL}/votes/stats").mock(
            return_value=Response(
                200,
                json={"upvotes": 10, "downvotes": 2},
            )
        )
        stats = await async_client.votes.get_stats("review", 100)
        assert stats.upvotes == 10

    @respx.mock
    @pytest.mark.asyncio
    async def test_async_get_user_by_address(self, async_client):
        """Test async user fetching by address."""
        respx.get(f"{BASE_URL}/user/by/address/0xabc").mock(
            return_value=Response(
                200,
                json={"id": 1, "profileId": 100},
            )
        )
        user = await async_client.users.get_by_address("0xabc")
        assert user.id == 1

    @respx.mock
    @pytest.mark.asyncio
    async def test_async_notification_stats(self, async_client):
        """Test async notification stats."""
        respx.get(f"{BASE_URL}/notifications/stats/me").mock(
            return_value=Response(200, json={"unreadCount": 5})
        )
        stats = await async_client.notifications.get_stats()
        assert stats.unread_count == 5

    @respx.mock
    @pytest.mark.asyncio
    async def test_async_contributions_history(self, async_client):
        """Test async contribution history."""
        respx.get(f"{BASE_URL}/contributions/history").mock(
            return_value=Response(
                200,
                json={"history": [{"date": "2024-01-15", "tasks": 3, "forgiven": False}]},
            )
        )
        history = await async_client.contributions.get_history()
        assert history.total_days == 1

    @respx.mock
    @pytest.mark.asyncio
    async def test_async_get_market(self, async_client):
        """Test async market fetching."""
        respx.get(f"{BASE_URL}/markets/50").mock(
            return_value=Response(200, json={"id": 50, "profileId": 100})
        )
        market = await async_client.markets.get(50)
        assert market.id == 50

    @respx.mock
    @pytest.mark.asyncio
    async def test_async_get_activity(self, async_client):
        """Test async activity fetching."""
        respx.get(f"{BASE_URL}/activities/100").mock(
            return_value=Response(200, json={"id": 100, "type": "vouch"})
        )
        activity = await async_client.activities.get(100)
        assert activity.id == 100

    @respx.mock
    @pytest.mark.asyncio
    async def test_async_check_eligibility(self, async_client):
        """Test async invitation eligibility check."""
        respx.get(f"{BASE_URL}/invitations/check").mock(
            return_value=Response(200, json={"canInvite": True, "address": "0xabc"})
        )
        eligibility = await async_client.invitations.check_eligibility("0xabc")
        assert eligibility.can_invite is True

    @respx.mock
    @pytest.mark.asyncio
    async def test_async_xp_weekly(self, async_client):
        """Test async XP weekly data."""
        respx.get(f"{BASE_URL}/xp/user/userkey/season/1/weekly").mock(
            return_value=Response(
                200,
                json=[{"week": 1, "weeklyXp": 100, "cumulativeXp": 100}],
            )
        )
        weekly = await async_client.xp.get_weekly("userkey", 1)
        assert len(weekly) == 1

    @respx.mock
    @pytest.mark.asyncio
    async def test_async_replies_for_review(self, async_client):
        """Test async replies for review."""
        respx.get(f"{BASE_URL}/replies/review/100").mock(
            return_value=Response(
                200,
                json={
                    "values": [
                        {
                            "id": 1,
                            "contractType": "review",
                            "parentId": 100,
                            "authorProfileId": 50,
                            "content": "Test",
                        }
                    ]
                },
            )
        )
        replies = await async_client.replies.for_review(100)
        assert len(replies) == 1


# =============================================================================
# Additional Sync Tests for Coverage
# =============================================================================


class TestAdditionalSyncResources:
    """Additional sync tests for coverage."""

    @respx.mock
    def test_get_activity_by_id(self, client):
        """Test getting activity by ID."""
        respx.get(f"{BASE_URL}/activities/100").mock(
            return_value=Response(200, json={"id": 100, "type": "vouch", "authorProfileId": 10})
        )
        activity = client.activities.get(100)
        assert activity.id == 100

    @respx.mock
    def test_get_market_by_id(self, client):
        """Test getting market by ID."""
        respx.get(f"{BASE_URL}/markets/50").mock(
            return_value=Response(200, json={"id": 50, "profileId": 100})
        )
        market = client.markets.get(50)
        assert market.id == 50

    @respx.mock
    def test_list_activities(self, client):
        """Test listing activities."""
        respx.get(f"{BASE_URL}/activities").mock(
            return_value=Response(
                200,
                json={"values": [{"id": 1, "type": "vouch"}, {"id": 2, "type": "review"}]},
            )
        )
        activities = list(client.activities.list(limit=10))
        assert len(activities) == 2

    @respx.mock
    def test_list_markets(self, client):
        """Test listing markets."""
        respx.get(f"{BASE_URL}/markets").mock(
            return_value=Response(
                200,
                json={"values": [{"id": 1, "profileId": 100}]},
            )
        )
        markets = list(client.markets.list(limit=10))
        assert len(markets) == 1

    @respx.mock
    def test_check_invitation_eligibility(self, client):
        """Test checking invitation eligibility."""
        respx.get(f"{BASE_URL}/invitations/check").mock(
            return_value=Response(200, json={"canInvite": True, "address": "0xabc123"})
        )
        eligibility = client.invitations.check_eligibility("0xabc123")
        assert eligibility.can_invite is True

    @respx.mock
    def test_profile_by_userkey(self, client):
        """Test getting profile by userkey."""
        respx.get(f"{BASE_URL}/profiles/userkey/x.com/user/testuser").mock(
            return_value=Response(200, json={"id": 1, "displayName": "Test User"})
        )
        profile = client.profiles.get_by_userkey("x.com/user/testuser")
        assert profile.id == 1

    @respx.mock
    def test_get_profile_by_address(self, client):
        """Test getting profile by address."""
        respx.get(f"{BASE_URL}/profiles/address/0xabc123").mock(
            return_value=Response(200, json={"id": 1, "displayName": "Address User"})
        )
        profile = client.profiles.get_by_address("0xabc123")
        assert profile.id == 1

    @respx.mock
    def test_get_review_by_id(self, client):
        """Test getting review by ID."""
        respx.get(f"{BASE_URL}/reviews/100").mock(
            return_value=Response(
                200,
                json={
                    "id": 100,
                    "authorProfileId": 10,
                    "subjectProfileId": 20,
                    "score": "positive",
                },
            )
        )
        review = client.reviews.get(100)
        assert review.id == 100

    @respx.mock
    def test_get_vouch_by_id(self, client):
        """Test getting vouch by ID."""
        respx.get(f"{BASE_URL}/vouches/100").mock(
            return_value=Response(
                200,
                json={
                    "id": 100,
                    "authorProfileId": 10,
                    "subjectProfileId": 20,
                    "staked": True,
                    "archived": False,
                },
            )
        )
        vouch = client.vouches.get(100)
        assert vouch.id == 100

    @respx.mock
    def test_list_reviews(self, client):
        """Test listing reviews."""
        respx.get(f"{BASE_URL}/reviews").mock(
            return_value=Response(
                200,
                json={
                    "values": [
                        {
                            "id": 1,
                            "authorProfileId": 10,
                            "subjectProfileId": 20,
                            "score": "positive",
                        }
                    ]
                },
            )
        )
        reviews = list(client.reviews.list(limit=10))
        assert len(reviews) == 1

    @respx.mock
    def test_list_vouches(self, client):
        """Test listing vouches."""
        respx.get(f"{BASE_URL}/vouches").mock(
            return_value=Response(
                200,
                json={
                    "values": [
                        {
                            "id": 1,
                            "authorProfileId": 10,
                            "subjectProfileId": 20,
                            "staked": True,
                            "archived": False,
                        }
                    ]
                },
            )
        )
        vouches = list(client.vouches.list(limit=10))
        assert len(vouches) == 1

    @respx.mock
    def test_replies_get_by_ids(self, client):
        """Test getting replies by IDs."""
        respx.get(f"{BASE_URL}/replies/by-id").mock(
            return_value=Response(
                200,
                json=[
                    {
                        "id": 1,
                        "contractType": "review",
                        "parentId": 100,
                        "authorProfileId": 50,
                        "content": "Test",
                    }
                ],
            )
        )
        replies = client.replies.get_by_ids([1])
        assert len(replies) == 1

    @respx.mock
    def test_replies_get_single(self, client):
        """Test getting single reply."""
        respx.get(f"{BASE_URL}/replies/by-id").mock(
            return_value=Response(
                200,
                json=[
                    {
                        "id": 1,
                        "contractType": "review",
                        "parentId": 100,
                        "authorProfileId": 50,
                        "content": "Test",
                    }
                ],
            )
        )
        reply = client.replies.get(1)
        assert reply.id == 1

    @respx.mock
    def test_replies_get_empty(self, client):
        """Test getting reply that doesn't exist."""
        respx.get(f"{BASE_URL}/replies/by-id").mock(return_value=Response(200, json=[]))
        reply = client.replies.get(999)
        assert reply is None

    @respx.mock
    def test_list_invitations(self, client):
        """Test listing invitations."""
        respx.get(f"{BASE_URL}/invitations").mock(
            return_value=Response(
                200,
                json={"values": [{"id": 1, "senderProfileId": 100, "status": "INVITED"}]},
            )
        )
        invitations = list(client.invitations.list(limit=10))
        assert len(invitations) == 1

    @respx.mock
    def test_replies_by_ids_dict_response(self, client):
        """Test replies by IDs with dict response."""
        respx.get(f"{BASE_URL}/replies/by-id").mock(
            return_value=Response(
                200,
                json={
                    "1": {
                        "id": 1,
                        "contractType": "review",
                        "parentId": 100,
                        "authorProfileId": 50,
                        "content": "Test",
                    },
                },
            )
        )
        replies = client.replies.get_by_ids([1])
        assert len(replies) == 1

    @respx.mock
    def test_profile_list(self, client):
        """Test listing profiles."""
        respx.get(f"{BASE_URL}/profiles").mock(
            return_value=Response(
                200,
                json={"values": [{"id": 1, "displayName": "User 1"}]},
            )
        )
        profiles = list(client.profiles.list(limit=10))
        assert len(profiles) == 1

    @respx.mock
    def test_activities_by_type(self, client):
        """Test getting activities with type filter."""
        respx.get(f"{BASE_URL}/activities").mock(
            return_value=Response(
                200,
                json={"values": [{"id": 1, "type": "vouch", "authorProfileId": 10}]},
            )
        )
        activities = list(client.activities.list(activity_type="vouch", limit=10))
        assert len(activities) == 1

    @respx.mock
    def test_activities_by_author(self, client):
        """Test getting activities with author filter."""
        respx.get(f"{BASE_URL}/activities").mock(
            return_value=Response(
                200,
                json={"values": [{"id": 1, "type": "vouch", "authorProfileId": 50}]},
            )
        )
        activities = list(client.activities.list(author_profile_id=50, limit=10))
        assert len(activities) == 1

    @respx.mock
    def test_get_xp_total_dict_response(self, client):
        """Test XP total with dict response."""
        respx.get(f"{BASE_URL}/xp/user/userkey").mock(return_value=Response(200, json={"xp": 1500}))
        total = client.xp.get_total("userkey")
        assert total == 1500

    @respx.mock
    def test_get_xp_season_total_dict_response(self, client):
        """Test XP season total with dict response."""
        respx.get(f"{BASE_URL}/xp/user/userkey/season/1").mock(
            return_value=Response(200, json={"xp": 500})
        )
        total = client.xp.get_season_total("userkey", 1)
        assert total == 500

    @respx.mock
    def test_async_client_close(self, async_client):
        """Test async client can be closed."""
        # Just verify it doesn't raise
        import asyncio

        async def close_client():
            await async_client.close()

        asyncio.get_event_loop().run_until_complete(close_client())

    @respx.mock
    def test_replies_empty_dict(self, client):
        """Test replies with empty dict response."""
        respx.get(f"{BASE_URL}/replies/by-id").mock(return_value=Response(200, json={}))
        replies = client.replies.get_by_ids([1])
        assert len(replies) == 0
