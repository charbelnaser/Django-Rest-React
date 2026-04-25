from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .models import WatchlistItem, UserMovieInteraction
from .serializers import WatchlistItemSerializer
import logging

logger = logging.getLogger(__name__)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_watchlist(request):
    """Get user's watchlist with optional filtering"""
    try:
        watchlist_items = WatchlistItem.objects.filter(user=request.user)

        # Filter by watch status if provided
        status_filter = request.GET.get("status")
        if status_filter in ["want_to_watch", "watched"]:
            watchlist_items = watchlist_items.filter(watch_status=status_filter)

        serializer = WatchlistItemSerializer(watchlist_items, many=True)

        return Response(
            {"watchlist": serializer.data, "count": watchlist_items.count()},
            status=status.HTTP_200_OK,
        )

    except Exception as e:
        logger.error(f"Get watchlist error: {str(e)}")
        return Response(
            {"error": "Failed to get watchlist"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def add_to_watchlist(request):
    """Add movie to user's watchlist"""
    try:
        movie_id = request.data.get("movie_id")
        if not movie_id:
            return Response(
                {"error": "Movie ID is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        # Check if already in watchlist
        if WatchlistItem.objects.filter(user=request.user, movie_id=movie_id).exists():
            return Response(
                {"error": "Movie is already in your watchlist"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Use provided movie data or get from TMDB
        movie_title = request.data.get("movie_title", "")
        movie_poster = request.data.get("movie_poster", "")
        movie_overview = request.data.get("movie_overview", "")
        movie_release_date = request.data.get("movie_release_date", "")
        movie_rating = request.data.get("movie_rating", 0)

        # If no data provided, try to get from TMDB
        if not movie_title:
            try:
                movie_data = tmdb_service.get_movie_details(movie_id)
                if movie_data:
                    movie_title = movie_data.get("title", "")
                    movie_poster = tmdb_service.get_full_image_url(
                        movie_data.get("poster_path")
                    )
                    movie_overview = movie_data.get("overview", "")
                    movie_release_date = movie_data.get("release_date", "")
                    movie_rating = movie_data.get("vote_average", 0)
            except Exception as tmdb_error:
                logger.warning(f"TMDB lookup failed: {tmdb_error}")
                # Continue with provided data or defaults

        # Create watchlist item
        watchlist_item = WatchlistItem.objects.create(
            user=request.user,
            movie_id=movie_id,
            movie_title=movie_title,
            movie_poster=movie_poster,
            movie_overview=movie_overview,
            movie_release_date=movie_release_date,
            movie_rating=movie_rating,
            watch_status="want_to_watch",
        )

        # Log interaction
        UserMovieInteraction.objects.create(
            user=request.user, movie_id=movie_id, interaction_type="add_to_watchlist"
        )

        serializer = WatchlistItemSerializer(watchlist_item)

        return Response(
            {"message": "Movie added to watchlist", "watchlist_item": serializer.data},
            status=status.HTTP_201_CREATED,
        )

    except Exception as e:
        logger.error(f"Add to watchlist error: {str(e)}")
        return Response(
            {"error": "Failed to add movie to watchlist"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def remove_from_watchlist(request, movie_id):
    """Remove movie from user's watchlist"""
    try:
        watchlist_item = get_object_or_404(
            WatchlistItem, user=request.user, movie_id=movie_id
        )

        watchlist_item.delete()

        # Log interaction
        UserMovieInteraction.objects.create(
            user=request.user,
            movie_id=movie_id,
            interaction_type="remove_from_watchlist",
        )

        return Response(
            {"message": "Movie removed from watchlist"}, status=status.HTTP_200_OK
        )

    except Exception as e:
        logger.error(f"Remove from watchlist error: {str(e)}")
        return Response(
            {"error": "Failed to remove movie from watchlist"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def toggle_watch_status(request, movie_id):
    """Toggle watch status between 'want_to_watch' and 'watched'"""
    try:
        watchlist_item = get_object_or_404(
            WatchlistItem, user=request.user, movie_id=movie_id
        )

        # Toggle status
        if watchlist_item.watch_status == "want_to_watch":
            watchlist_item.mark_as_watched()
            interaction_type = "mark_watched"
            message = "Movie marked as watched"
        else:
            watchlist_item.mark_as_want_to_watch()
            interaction_type = "mark_unwatched"
            message = "Movie marked as want to watch"

        # Log interaction
        UserMovieInteraction.objects.create(
            user=request.user, movie_id=movie_id, interaction_type=interaction_type
        )

        serializer = WatchlistItemSerializer(watchlist_item)

        return Response(
            {"message": message, "watchlist_item": serializer.data},
            status=status.HTTP_200_OK,
        )

    except Exception as e:
        logger.error(f"Toggle watch status error: {str(e)}")
        return Response(
            {"error": "Failed to update watch status"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def check_watchlist_status(request, movie_id):
    """Check if a movie is in user's watchlist and its status"""
    try:
        try:
            watchlist_item = WatchlistItem.objects.get(
                user=request.user, movie_id=movie_id
            )
            serializer = WatchlistItemSerializer(watchlist_item)
            return Response(
                {"in_watchlist": True, "watchlist_item": serializer.data},
                status=status.HTTP_200_OK,
            )

        except WatchlistItem.DoesNotExist:
            return Response(
                {"in_watchlist": False, "watchlist_item": None},
                status=status.HTTP_200_OK,
            )

    except Exception as e:
        logger.error(f"Check watchlist status error: {str(e)}")
        return Response(
            {"error": "Failed to check watchlist status"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


class WatchlistView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Get user's watchlist with optional filtering"""
        return get_watchlist(request)


class WatchlistView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Get user's watchlist with optional filtering"""
        try:
            watchlist_items = WatchlistItem.objects.filter(user=request.user)

            # Filter by watch status if provided
            status_filter = request.GET.get("status")
            if status_filter in ["want_to_watch", "watched"]:
                watchlist_items = watchlist_items.filter(watch_status=status_filter)

            serializer = WatchlistItemSerializer(watchlist_items, many=True)

            return Response(
                {"watchlist": serializer.data, "count": watchlist_items.count()},
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            logger.error(f"Get watchlist error: {str(e)}")
            return Response(
                {"error": "Failed to get watchlist"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class AddToWatchlistView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Add movie to user's watchlist"""
        try:
            movie_id = request.data.get("movie_id")
            if not movie_id:
                return Response(
                    {"error": "Movie ID is required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Check if already in watchlist
            if WatchlistItem.objects.filter(
                user=request.user, movie_id=movie_id
            ).exists():
                return Response(
                    {"error": "Movie is already in your watchlist"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Use provided movie data
            movie_title = request.data.get("movie_title", "")
            movie_poster = request.data.get("movie_poster", "")
            movie_overview = request.data.get("movie_overview", "")
            movie_release_date = request.data.get("movie_release_date", "")
            movie_rating = request.data.get("movie_rating", 0)

            # Create watchlist item
            watchlist_item = WatchlistItem.objects.create(
                user=request.user,
                movie_id=movie_id,
                movie_title=movie_title,
                movie_poster=movie_poster,
                movie_overview=movie_overview,
                movie_release_date=movie_release_date or None,
                movie_rating=movie_rating,
                watch_status="want_to_watch",
            )

            # Log interaction
            UserMovieInteraction.objects.create(
                user=request.user,
                movie_id=movie_id,
                interaction_type="add_to_watchlist",
            )

            serializer = WatchlistItemSerializer(watchlist_item)

            return Response(
                {
                    "message": "Movie added to watchlist",
                    "watchlist_item": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )

        except Exception as e:
            logger.error(f"Add to watchlist error: {str(e)}")
            return Response(
                {"error": "Failed to add movie to watchlist"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class RemoveFromWatchlistView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, movie_id):
        """Remove movie from user's watchlist"""
        try:
            watchlist_item = get_object_or_404(
                WatchlistItem, user=request.user, movie_id=movie_id
            )

            watchlist_item.delete()

            # Log interaction
            UserMovieInteraction.objects.create(
                user=request.user,
                movie_id=movie_id,
                interaction_type="remove_from_watchlist",
            )

            return Response(
                {"message": "Movie removed from watchlist"}, status=status.HTTP_200_OK
            )

        except Exception as e:
            logger.error(f"Remove from watchlist error: {str(e)}")
            return Response(
                {"error": "Failed to remove movie from watchlist"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class CheckWatchlistView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, movie_id):
        """Check if a movie is in user's watchlist"""
        try:
            try:
                watchlist_item = WatchlistItem.objects.get(
                    user=request.user, movie_id=movie_id
                )
                serializer = WatchlistItemSerializer(watchlist_item)
                return Response(
                    {"in_watchlist": True, "watchlist_item": serializer.data},
                    status=status.HTTP_200_OK,
                )

            except WatchlistItem.DoesNotExist:
                return Response(
                    {"in_watchlist": False, "watchlist_item": None},
                    status=status.HTTP_200_OK,
                )

        except Exception as e:
            logger.error(f"Check watchlist status error: {str(e)}")
            return Response(
                {"error": "Failed to check watchlist status"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class WatchedMoviesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Get user's watched movies"""
        try:
            watched_items = WatchlistItem.objects.filter(
                user=request.user, watch_status="watched"
            )
            serializer = WatchlistItemSerializer(watched_items, many=True)

            return Response(
                {"watched_movies": serializer.data, "count": watched_items.count()},
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            logger.error(f"Get watched movies error: {str(e)}")
            return Response(
                {"error": "Failed to get watched movies"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class MarkAsWatchedView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Mark a movie as watched"""
        try:
            movie_id = request.data.get("movie_id")
            if not movie_id:
                return Response(
                    {"error": "Movie ID is required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            watchlist_item = get_object_or_404(
                WatchlistItem, user=request.user, movie_id=movie_id
            )

            watchlist_item.mark_as_watched()

            # Log interaction
            UserMovieInteraction.objects.create(
                user=request.user, movie_id=movie_id, interaction_type="mark_watched"
            )

            serializer = WatchlistItemSerializer(watchlist_item)

            return Response(
                {
                    "message": "Movie marked as watched",
                    "watchlist_item": serializer.data,
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            logger.error(f"Mark as watched error: {str(e)}")
            return Response(
                {"error": "Failed to mark movie as watched"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class UnmarkAsWatchedView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, movie_id):
        """Unmark a movie as watched"""
        return self.put(request, movie_id)

    def put(self, request, movie_id):
        """Toggle watch status between 'want_to_watch' and 'watched'"""
        try:
            watchlist_item = get_object_or_404(
                WatchlistItem, user=request.user, movie_id=movie_id
            )

            # Toggle status
            if watchlist_item.watch_status == "want_to_watch":
                watchlist_item.mark_as_watched()
                interaction_type = "mark_watched"
                message = "Movie marked as watched"
            else:
                watchlist_item.mark_as_want_to_watch()
                interaction_type = "mark_unwatched"
                message = "Movie marked as want to watch"

            # Log interaction
            UserMovieInteraction.objects.create(
                user=request.user, movie_id=movie_id, interaction_type=interaction_type
            )

            serializer = WatchlistItemSerializer(watchlist_item)

            return Response(
                {"message": message, "watchlist_item": serializer.data},
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            logger.error(f"Toggle watch status error: {str(e)}")
            return Response(
                {"error": "Failed to update watch status"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class WatchlistStatsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Get watchlist statistics"""
        try:
            user_watchlist = WatchlistItem.objects.filter(user=request.user)

            total_movies = user_watchlist.count()
            want_to_watch = user_watchlist.filter(watch_status="want_to_watch").count()
            watched = user_watchlist.filter(watch_status="watched").count()

            # Get recent activity (last 10 items)
            recent_activity = user_watchlist.order_by("-added_at")[:10]
            recent_serializer = WatchlistItemSerializer(recent_activity, many=True)

            return Response(
                {
                    "total_movies": total_movies,
                    "want_to_watch": want_to_watch,
                    "watched": watched,
                    "total_watch_time": 0,  # Placeholder - would need movie runtime data
                    "favorite_genres": [],  # Placeholder - would need genre analysis
                    "recent_activity": recent_serializer.data,
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            logger.error(f"Get watchlist stats error: {str(e)}")
            return Response(
                {"error": "Failed to get watchlist statistics"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
