"""
Basic tests for Ethos SDK.
"""

from ethos import Ethos, EthosConfig
from ethos.types import Profile, Review, Vouch
from ethos.types.contribution import ContributionDay, ContributionHistory
from ethos.types.endorsement import Endorsement
from ethos.types.invitation import Invitation
from ethos.types.notification import Notification, NotificationStats
from ethos.types.reply import Reply
from ethos.types.user import User
from ethos.types.vote import Vote, VoteStats
from ethos.types.xp import XPHistoryEntry, XPTip


class TestEthosClient:
    """Tests for the main Ethos client."""

    def test_client_creation(self):
        """Test that client can be created with defaults."""
        client = Ethos()
        assert client is not None
        assert client.config.client_name == "ethos-py"
        client.close()

    def test_client_custom_config(self):
        """Test client with custom configuration."""
        client = Ethos(
            client_name="test-app",
            timeout=60.0,
            rate_limit=1.0,
        )
        assert client.config.client_name == "test-app"
        assert client.config.timeout == 60.0
        assert client.config.rate_limit == 1.0
        client.close()

    def test_client_context_manager(self):
        """Test client as context manager."""
        with Ethos() as client:
            assert client is not None

    def test_client_has_resources(self):
        """Test that client has all resource attributes."""
        with Ethos() as client:
            # Core resources
            assert hasattr(client, "profiles")
            assert hasattr(client, "vouches")
            assert hasattr(client, "reviews")
            assert hasattr(client, "markets")
            assert hasattr(client, "activities")
            assert hasattr(client, "scores")
            # Extended resources
            assert hasattr(client, "users")
            assert hasattr(client, "endorsements")
            assert hasattr(client, "votes")
            assert hasattr(client, "replies")
            assert hasattr(client, "xp")
            assert hasattr(client, "invitations")
            assert hasattr(client, "notifications")
            assert hasattr(client, "contributions")


class TestEthosConfig:
    """Tests for configuration."""

    def test_default_config(self):
        """Test default configuration values."""
        config = EthosConfig()
        assert config.base_url == "https://api.ethos.network/api/v2"
        assert config.client_name == "ethos-py"
        assert config.timeout == 30.0
        assert config.rate_limit == 0.5
        assert config.max_retries == 3

    def test_config_from_env(self, monkeypatch):
        """Test configuration from environment variables."""
        monkeypatch.setenv("ETHOS_CLIENT_NAME", "env-test-app")
        monkeypatch.setenv("ETHOS_TIMEOUT", "60")

        config = EthosConfig.from_env()
        assert config.client_name == "env-test-app"
        assert config.timeout == 60.0


class TestProfileModel:
    """Tests for Profile type."""

    def test_profile_parsing(self):
        """Test that profile can be parsed from API response."""
        data = {
            "id": 123,
            "profileId": 123,
            "address": "0x1234567890abcdef",
            "displayName": "Test User",
            "score": 1500,
            "status": "ACTIVE",
            "userkeys": ["x.com/user/testuser"],
        }

        profile = Profile.model_validate(data)

        assert profile.id == 123
        assert profile.address == "0x1234567890abcdef"
        assert profile.display_name == "Test User"
        assert profile.score == 1500
        assert profile.twitter_handle == "testuser"

    def test_profile_score_level(self):
        """Test score level calculation."""
        profile = Profile(id=1, score=500)
        assert profile.score_level == "untrusted"

        profile = Profile(id=2, score=1000)
        assert profile.score_level == "questionable"

        profile = Profile(id=3, score=1400)
        assert profile.score_level == "neutral"

        profile = Profile(id=4, score=1800)
        assert profile.score_level == "reputable"

        profile = Profile(id=5, score=2200)
        assert profile.score_level == "exemplary"


class TestVouchModel:
    """Tests for Vouch type."""

    def test_vouch_parsing(self):
        """Test that vouch can be parsed from API response."""
        data = {
            "id": 456,
            "authorProfileId": 100,
            "subjectProfileId": 200,
            "staked": True,
            "archived": False,
            "balance": "1000000000000000000",  # 1 ETH in wei
        }

        vouch = Vouch.model_validate(data)

        assert vouch.id == 456
        assert vouch.author_profile_id == 100
        assert vouch.target_profile_id == 200
        assert vouch.is_active
        assert vouch.amount_wei == 1000000000000000000
        assert vouch.amount_eth == 1.0


class TestReviewModel:
    """Tests for Review type."""

    def test_review_parsing(self):
        """Test that review can be parsed from API response."""
        data = {
            "id": 789,
            "authorProfileId": 100,
            "subjectProfileId": 200,
            "score": "positive",
            "comment": "Great person!",
            "archived": False,
        }

        review = Review.model_validate(data)

        assert review.id == 789
        assert review.author_profile_id == 100
        assert review.target_profile_id == 200
        assert review.is_positive
        assert not review.is_negative
        assert review.comment == "Great person!"


class TestUserModel:
    """Tests for User type."""

    def test_user_parsing(self):
        """Test that user can be parsed from API response."""
        data = {
            "id": 123,
            "profileId": 456,
            "address": "0xabcdef",
            "displayName": "Test User",
            "username": "testuser",
            "score": 1500,
            "xpTotal": 1000,
            "xpStreakDays": 5,
            "influenceFactor": 1.5,
            "userkeys": ["x.com/user/testuser", "discord.com/user/123456"],
        }

        user = User.model_validate(data)

        assert user.id == 123
        assert user.profile_id == 456
        assert user.score == 1500
        assert user.xp_total == 1000
        assert user.twitter_handle == "testuser"
        assert user.discord_id == "123456"
        assert user.score_level == "neutral"


class TestEndorsementModel:
    """Tests for Endorsement type."""

    def test_endorsement_parsing(self):
        """Test that endorsement can be parsed from API response."""
        data = {
            "activityId": 1000,
            "endorserProfileId": 100,
            "endorsementType": "vouch",
            "sourceId": 500,
            "connectionDegree": "1st",
        }

        endorsement = Endorsement.model_validate(data)

        assert endorsement.activity_id == 1000
        assert endorsement.endorser_profile_id == 100
        assert endorsement.endorsement_type == "vouch"
        assert endorsement.is_first_degree
        assert endorsement.is_vouch
        assert not endorsement.is_review


class TestVoteModel:
    """Tests for Vote type."""

    def test_vote_parsing(self):
        """Test that vote can be parsed from API response."""
        data = {
            "voterProfileId": 100,
            "targetType": "review",
            "targetId": 500,
            "isUpvote": True,
            "weight": 1.5,
        }

        vote = Vote.model_validate(data)

        assert vote.voter_profile_id == 100
        assert vote.target_type == "review"
        assert vote.target_id == 500
        assert vote.is_upvote
        assert not vote.is_downvote
        assert vote.weight == 1.5

    def test_vote_stats_parsing(self):
        """Test vote stats parsing."""
        data = {
            "upvotes": 10,
            "downvotes": 3,
            "weightedUpvotes": 15.5,
            "weightedDownvotes": 4.2,
        }

        stats = VoteStats.model_validate(data)

        assert stats.upvotes == 10
        assert stats.downvotes == 3
        assert stats.total_votes == 13
        assert stats.net_votes == 7


class TestReplyModel:
    """Tests for Reply type."""

    def test_reply_parsing(self):
        """Test that reply can be parsed from API response."""
        data = {
            "id": 999,
            "contractType": "review",
            "parentId": 500,
            "authorProfileId": 100,
            "content": "Thanks for the review!",
        }

        reply = Reply.model_validate(data)

        assert reply.id == 999
        assert reply.contract_type == "review"
        assert reply.parent_id == 500
        assert reply.content == "Thanks for the review!"
        assert reply.is_review_reply
        assert not reply.is_vouch_reply


class TestXPModels:
    """Tests for XP types."""

    def test_xp_history_parsing(self):
        """Test XP history entry parsing."""
        data = {
            "id": 1,
            "type": "daily_task",
            "points": 100,
            "week": 5,
            "xpSeasonId": 1,
        }

        entry = XPHistoryEntry.model_validate(data)

        assert entry.id == 1
        assert entry.type == "daily_task"
        assert entry.points == 100
        assert entry.week == 5

    def test_xp_tip_parsing(self):
        """Test XP tip parsing."""
        data = {
            "id": 1,
            "senderProfileId": 100,
            "receiverProfileId": 200,
            "amount": 50,
        }

        tip = XPTip.model_validate(data)

        assert tip.id == 1
        assert tip.sender_profile_id == 100
        assert tip.receiver_profile_id == 200
        assert tip.amount == 50


class TestInvitationModel:
    """Tests for Invitation type."""

    def test_invitation_parsing(self):
        """Test that invitation can be parsed from API response."""
        data = {
            "id": 1,
            "senderProfileId": 100,
            "inviteeAddress": "0xabcdef",
            "status": "INVITED",
        }

        invitation = Invitation.model_validate(data)

        assert invitation.id == 1
        assert invitation.sender_profile_id == 100
        assert invitation.status == "INVITED"
        assert invitation.is_pending
        assert not invitation.is_accepted


class TestNotificationModel:
    """Tests for Notification type."""

    def test_notification_parsing(self):
        """Test that notification can be parsed from API response."""
        data = {
            "id": 1,
            "type": "VOUCH",
            "title": "New vouch received",
            "isRead": False,
            "actorProfileId": 100,
        }

        notification = Notification.model_validate(data)

        assert notification.id == 1
        assert notification.type == "VOUCH"
        assert notification.is_unread
        assert not notification.is_read

    def test_notification_stats_parsing(self):
        """Test notification stats parsing."""
        data = {"unreadCount": 5}

        stats = NotificationStats.model_validate(data)

        assert stats.unread_count == 5


class TestContributionModel:
    """Tests for Contribution type."""

    def test_contribution_day_parsing(self):
        """Test contribution day parsing."""
        data = {"date": "2024-01-15", "tasks": 3, "forgiven": False}

        day = ContributionDay.model_validate(data)

        assert day.date == "2024-01-15"
        assert day.tasks == 3
        assert day.has_activity

    def test_contribution_history(self):
        """Test contribution history aggregation."""
        data = {
            "history": [
                {"date": "2024-01-15", "tasks": 3, "forgiven": False},
                {"date": "2024-01-16", "tasks": 0, "forgiven": True},
                {"date": "2024-01-17", "tasks": 2, "forgiven": False},
            ]
        }

        history = ContributionHistory.model_validate(data)

        assert history.total_days == 3
        assert history.active_days == 3  # All have activity (tasks or forgiven)
        assert history.total_tasks == 5
        assert history.forgiven_days == 1
