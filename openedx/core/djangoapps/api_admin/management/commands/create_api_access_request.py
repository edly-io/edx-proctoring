""" Management command to create an ApiAccessRequest for given users """
import logging
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from django.contrib.sites.models import Site

from openedx.core.djangoapps.api_admin.models import (
    ApiAccessConfig,
    ApiAccessRequest,
)

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Create an ApiAccessRequest for the given user

    Example usage:
        $ ./manage.py lms create_api_request <username> --create-config
    """

    help = 'Create an ApiAccessRequest for the given user'
    DEFAULT_WEBSITE = 'www.test-edx-example-website.edu'
    DEFAULT_REASON = 'Generated by management job create_api_request'

    def add_arguments(self, parser):
        parser.add_argument('username')
        parser.add_argument(
            '--create-config',
            action='store_true',
            help='Create ApiAccessConfig if it does not exist'
        )
        parser.add_argument(
            '--status',
            choices=[choice[0] for choice in ApiAccessRequest.STATUS_CHOICES],
            default=ApiAccessRequest.APPROVED,
            help='Status of the created ApiAccessRequest'
        )
        parser.add_argument(
            '--reason',
            default=self.DEFAULT_REASON,
            help='Reason that the ApiAccessRequest is being created'
        )
        parser.add_argument(
            '--website',
            default=self.DEFAULT_WEBSITE,
            help='Website associated with the user of the created ApiAccessRequest'
        )

    def handle(self, *args, **options):
        if options.get('create_config'):
            self.create_api_access_config()
        user = self.get_user(options.get('username'))
        self.create_api_access_request(
            user,
            options.get('status'),
            options.get('reason'),
            options.get('website'),
        )

    def get_user(self, username):
        try:
            return User.objects.get(username=username)
        except User.DoesNotExist:
            raise CommandError(u'User {} not found'.format(username))

    def create_api_access_request(self, user, status, reason, website):
        """
        Creates an ApiAccessRequest with the given values.
        """
        try:
            ApiAccessRequest.objects.create(
                user=user,
                status=status,
                website=website,
                reason=reason,
                site=Site.objects.get_current(),
            )
        except Exception as e:
            msg = u'Unable to create ApiAccessRequest for {}. Exception is {}: {}'.format(
                user.username,
                type(e).__name__,
                e
            )
            raise CommandError(msg)
        logger.info(u'Created ApiAccessRequest for user {}'.format(user.username))

    def create_api_access_config(self):
        """
        Creates an active ApiAccessConfig if one does not currectly exist
        """
        try:
            _, created = ApiAccessConfig.objects.get_or_create(enabled=True)
        except Exception as e:
            msg = u'Unable to create ApiAccessConfig. Exception is {}: {}'.format(type(e).__name__, e)
            raise CommandError(msg)
        if created:
            logger.info(u'Created ApiAccessConfig')
        else:
            logger.info(u'ApiAccessConfig already exists')
